"""
Full Validation Test Suite for First-Principles Attribution Engine
Run with: python tests/full_validation.py
"""

import json
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.adapters import (
    FacebookAdapter,
    GoogleAnalyticsAdapter,
    CSVAdapter,
    BrowserHistoryAdapter,
    UniversalEvent,
    validate_events,
    merge_event_streams,
    ChannelTaxonomy
)
from src.validation import (
    validation_suite,
    generate_synthetic_ground_truth,
    compare_to_ground_truth,
    run_validation_report
)


def test_universal_event():
    print("\n" + "="*60)
    print("TEST 1: UniversalEvent Schema")
    print("="*60)
    
    event = UniversalEvent(
        timestamp="2024-01-15T14:30:00Z",
        user_id="abc123def456",
        channel="Paid Search",
        event_type="conversion",
        context={'device': 'mobile', 'intent_signal': 'high', 'session_depth': 'medium', 'source_platform': 'ga'},
        conversion_value=99.99,
        metadata={'campaign': 'winter_sale'}
    )
    
    assert event.timestamp == "2024-01-15T14:30:00Z"
    assert event.channel == "Paid Search"
    assert event.conversion_value == 99.99
    
    event_dict = event.to_dict()
    restored = UniversalEvent.from_dict(event_dict)
    assert restored.timestamp == event.timestamp
    
    print("[OK] UniversalEvent creation works")
    print("[OK] Serialization/deserialization works")
    return True


def test_validate_events():
    print("\n" + "="*60)
    print("TEST 2: Event Validation")
    print("="*60)
    
    events = [
        UniversalEvent(timestamp="2024-01-15T14:30:00Z", user_id="user1", channel="Search", event_type="conversion"),
        UniversalEvent(timestamp="2024-01-15T14:35:00Z", user_id="user2", channel="Email", event_type="pageview"),
    ]
    
    errors = validate_events(events)
    assert len(errors) == 0, f"Expected no errors, got {errors}"
    print("[OK] Valid events pass validation")
    
    invalid_events = [UniversalEvent(timestamp="", user_id="user1", channel="Search", event_type="conversion")]
    errors = validate_events(invalid_events)
    assert len(errors) > 0, "Expected validation errors"
    print("[OK] Invalid events caught correctly")
    return True


def test_merge_streams():
    print("\n" + "="*60)
    print("TEST 3: Merge Event Streams")
    print("="*60)
    
    stream1 = [
        UniversalEvent(timestamp="2024-01-15T10:00:00Z", user_id="user1", channel="Search", event_type="pageview"),
        UniversalEvent(timestamp="2024-01-15T10:05:00Z", user_id="user1", channel="Email", event_type="click"),
    ]
    
    stream2 = [
        UniversalEvent(timestamp="2024-01-15T09:00:00Z", user_id="user2", channel="Direct", event_type="pageview"),
    ]
    
    merged = merge_event_streams(stream1, stream2, sort_by_time=True)
    assert len(merged) == 3
    assert merged[0].timestamp < merged[1].timestamp
    print("[OK] Events merged and sorted correctly")
    
    duplicate = [UniversalEvent(timestamp="2024-01-15T10:00:00Z", user_id="user1", channel="Search", event_type="pageview")]
    merged_dedup = merge_event_streams(stream1, duplicate, deduplicate=True)
    assert len(merged_dedup) == 2
    print("[OK] Deduplication works")
    return True


def test_channel_taxonomy():
    print("\n" + "="*60)
    print("TEST 4: Channel Taxonomy")
    print("="*60)
    
    taxonomy = ChannelTaxonomy()
    
    tests = [
        ('cpc', 'ga', 'Paid Search'),
        ('organic', 'ga', 'Organic Search'),
        ('facebook.com', 'domains', 'Organic Social'),
        ('(direct)', 'ga', 'Direct'),
        ('newsletter', 'ga', 'Email'),
        ('display', 'ga', 'Display'),
    ]
    
    for raw, source, expected in tests:
        result = taxonomy.normalize(raw, source)
        assert result == expected, f"Failed: {raw} -> {result}"
        print(f"[OK] {raw} ({source}) -> {expected}")
    
    return True


def test_facebook_adapter():
    print("\n" + "="*60)
    print("TEST 5: Facebook Adapter")
    print("="*60)
    
    synthetic_fb = {
        "advertisers_using_your_activity": [
            {"name": "ExampleStore", "timestamp": 1705315800000}
        ],
        "off_facebook_activity_v2": [
            {"name": "ShopOnline", "events": [
                {"timestamp": 1705314600000, "type": "PAGE_VIEW"},
                {"timestamp": 1705314000000, "type": "PURCHASE"}
            ]}
        ]
    }
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(synthetic_fb, f)
        temp_path = f.name
    
    try:
        adapter = FacebookAdapter(temp_path)
        events = adapter.parse()
        
        assert len(events) > 0, f"Should parse events, got {len(events)}"
        print(f"[OK] Parsed {len(events)} Facebook events")
        
        for event in events:
            assert event.timestamp, "Missing timestamp"
            assert event.user_id, "Missing user_id"
        print("[OK] All events have required fields")
        
        summary = adapter.summary()
        print(f"[OK] Summary - {summary['total_events']} events")
    finally:
        os.unlink(temp_path)
    
    return True


def test_ga4_adapter():
    print("\n" + "="*60)
    print("TEST 6: GA4 Adapter")
    print("="*60)
    
    synthetic_ga4 = [
        {"event_name": "page_view", "event_timestamp": 1705315800000000,
         "user_pseudo_id": "ga_user_12345", "traffic_source": {"source": "google", "medium": "organic"},
         "device": {"category": "mobile"}},
        {"event_name": "purchase", "event_timestamp": 1705316400000000,
         "user_pseudo_id": "ga_user_12345", "traffic_source": {"source": "google", "medium": "cpc"},
         "device": {"category": "mobile"}, "ecommerce": {"purchase": {"value": 149.99}}}
    ]
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(synthetic_ga4, f)
        temp_path = f.name
    
    try:
        adapter = GoogleAnalyticsAdapter(temp_path)
        events = adapter.parse()
        
        assert len(events) > 0, f"Should parse events, got {len(events)}"
        print(f"[OK] Parsed {len(events)} GA4 events")
        
        conv_events = [e for e in events if e.event_type == 'conversion']
        assert len(conv_events) > 0, "Should detect purchase as conversion"
        print(f"[OK] {len(conv_events)} conversion events detected")
        
        channels = set(e.channel for e in events)
        print(f"[OK] Channels: {channels}")
    finally:
        os.unlink(temp_path)
    
    return True


def test_csv_adapter():
    print("\n" + "="*60)
    print("TEST 7: CSV Adapter")
    print("="*60)
    
    csv_content = """timestamp,user_id,channel,event_type,conversion_value
2024-01-15T10:00:00Z,user_001,google / organic,pageview,0
2024-01-15T10:05:00Z,user_001,google / cpc,conversion,99.99
2024-01-15T10:00:00Z,user_002,email / newsletter,pageview,0
"""
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    
    try:
        adapter = CSVAdapter(temp_path)
        events = adapter.parse()
        
        assert len(events) == 3, f"Expected 3 events, got {len(events)}"
        print(f"[OK] Parsed {len(events)} CSV events")
        print(f"[OK] Channels: {set(e.channel for e in events)}")
    finally:
        os.unlink(temp_path)
    
    return True


def test_browser_adapter():
    print("\n" + "="*60)
    print("TEST 8: Browser History Adapter")
    print("="*60)
    
    synthetic_history = [
        {"URL": "https://www.google.com/search?q=product", "title": "Search", "visitTime": 1705315800000},
        {"URL": "https://example.com/products", "title": "Products", "visitTime": 1705315200000},
    ]
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(synthetic_hi
