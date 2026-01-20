"""
Data Adapters for Multi-Source Integration

Converts data from various sources into the universal event schema
required by the attribution engine.

Supported Sources:
- Facebook Data Export (JSON)
- Google Analytics 4 (BigQuery/JSON export)
- Generic CSV (flexible column mapping)
- Browser History (Chrome, Firefox, Safari)
- Manual Event Log (JSON)

Usage:
    from src.adapters import FacebookAdapter, GoogleAnalyticsAdapter

    # Parse Facebook export
    fb = FacebookAdapter('facebook_export.json')
    events = fb.parse()

    # Parse GA4 export
    ga = GoogleAnalyticsAdapter('ga4_export.json')
    events = ga.parse()

    # Combine sources
    all_events = events_fb + events_ga

    # Feed to attribution engine
    result = attribution_engine.run(all_events)
"""

from .base_adapter import (
    BaseAdapter,
    UniversalEvent,
    UNIVERSAL_EVENT_SCHEMA,
    validate_events,
    merge_event_streams
)

from .facebook_adapter import FacebookAdapter
from .google_analytics_adapter import GoogleAnalyticsAdapter
from .csv_adapter import CSVAdapter
from .browser_history_adapter import BrowserHistoryAdapter
from .channel_taxonomy import (
    ChannelTaxonomy,
    normalize_channel,
    CHANNEL_MAPPINGS
)

__all__ = [
    # Base
    'BaseAdapter',
    'UniversalEvent',
    'UNIVERSAL_EVENT_SCHEMA',
    'validate_events',
    'merge_event_streams',

    # Adapters
    'FacebookAdapter',
    'GoogleAnalyticsAdapter',
    'CSVAdapter',
    'BrowserHistoryAdapter',

    # Taxonomy
    'ChannelTaxonomy',
    'normalize_channel',
    'CHANNEL_MAPPINGS'
]
