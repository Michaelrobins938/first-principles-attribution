"""
Facebook Data Export Adapter

Parses Facebook's data export format (JSON) into universal events.

Supported Facebook Export Sections:
- Your Activity Across Facebook (posts, comments, reactions)
- Ads and Businesses (ad interactions)
- Apps and Websites (off-Facebook activity)
- Search History
- Location History
- Messages (metadata only, not content)

Usage:
    from src.adapters import FacebookAdapter

    adapter = FacebookAdapter('facebook_export/')
    events = adapter.parse()
    print(adapter.summary())
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base_adapter import BaseAdapter, UniversalEvent
from .channel_taxonomy import normalize_channel


class FacebookAdapter(BaseAdapter):
    """
    Adapter for Facebook data exports.

    Facebook exports data as JSON files organized in directories.
    This adapter handles the various export formats and structures.
    """

    def __init__(self, source_path: str):
        """
        Initialize Facebook adapter.

        Parameters
        ----------
        source_path : str
            Path to Facebook export directory or JSON file
        """
        super().__init__(source_path)
        self.source_name = "facebook"
        self.raw_data = {}

    def parse(self) -> List[UniversalEvent]:
        """
        Parse Facebook export into universal events.

        Returns
        -------
        list
            List of UniversalEvent objects
        """
        if os.path.isdir(self.source_path):
            self._load_directory()
        else:
            self._load_file(self.source_path)

        # Process each data type
        events = []

        # Activity events
        events.extend(self._parse_activity())

        # Ad interactions
        events.extend(self._parse_ads())

        # Off-Facebook activity
        events.extend(self._parse_off_facebook())

        # Search history
        events.extend(self._parse_searches())

        # Posts and interactions
        events.extend(self._parse_posts())

        # Messages (metadata only)
        events.extend(self._parse_messages())

        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)

        # Add session depth context
        events = self._add_session_context(events)

        self.events = events
        return events

    def _load_directory(self):
        """Load all JSON files from Facebook export directory."""
        path = Path(self.source_path)

        # Common Facebook export paths
        json_files = list(path.rglob('*.json'))

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Store by relative path
                rel_path = str(json_file.relative_to(path))
                self.raw_data[rel_path] = data

            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

    def _load_file(self, filepath: str):
        """Load single JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.raw_data['main'] = data

    def _parse_activity(self) -> List[UniversalEvent]:
        """Parse general activity data."""
        events = []

        # Look for activity files
        activity_patterns = [
            'your_activity',
            'activity_across_facebook',
            'posts_and_comments',
            'likes_and_reactions'
        ]

        for key, data in self.raw_data.items():
            if any(p in key.lower() for p in activity_patterns):
                events.extend(self._extract_activity_events(data, key))

        return events

    def _extract_activity_events(
        self,
        data: Any,
        source_key: str
    ) -> List[UniversalEvent]:
        """Extract events from activity data structure."""
        events = []

        # Handle different structures
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Try common keys
            for key in ['activity', 'entries', 'items', 'data', 'v2']:
                if key in data:
                    items = data[key]
                    break
            else:
                items = [data]
        else:
            return events

        for item in items:
            if not isinstance(item, dict):
                continue

            event = self._item_to_event(item, 'engagement', source_key)
            if event:
                events.append(event)

        return events

    def _parse_ads(self) -> List[UniversalEvent]:
        """Parse ad interaction data."""
        events = []

        ad_patterns = [
            'ads_and_businesses',
            'ad_interests',
            'advertisers',
            'your_off_facebook_activity'
        ]

        for key, data in self.raw_data.items():
            if any(p in key.lower() for p in ad_patterns):
                events.extend(self._extract_ad_events(data, key))
            # Also check main key content for ad patterns
            elif key == 'main' and isinstance(data, dict):
                for k, v in data.items():
                    if any(p in k.lower() for p in ad_patterns):
                        events.extend(self._extract_ad_events(v, k))
                # Also check if data itself contains ad fields at top level
                for pattern in ad_patterns:
                    if pattern in data and isinstance(data[pattern], list):
                        events.extend(self._extract_ad_events(data, key))
                        break

        return events

    def _extract_ad_events(
        self,
        data: Any,
        source_key: str
    ) -> List[UniversalEvent]:
        """Extract ad interaction events."""
        events = []

        if isinstance(data, dict):
            # Handle advertiser interactions
            if 'advertisers_using_your_activity' in data:
                for advertiser in data['advertisers_using_your_activity']:
                    if isinstance(advertiser, dict):
                        event = UniversalEvent(
                            timestamp=self.parse_timestamp(
                                advertiser.get('timestamp', datetime.now().timestamp())
                            ),
                            user_id=self.hash_user_id('facebook_user'),
                            channel='Paid Social',
                            event_type='click',
                            context={
                                'device': 'unknown',
                                'intent_signal': 'medium',
                                'session_depth': 'unknown',
                                'source_platform': 'facebook'
                            },
                            metadata={
                                'advertiser': advertiser.get('name', 'unknown'),
                                'source_file': source_key
                            }
                        )
                        events.append(event)

            # Handle off-Facebook activity
            if 'off_facebook_activity' in data:
                for activity in data['off_facebook_activity']:
                    if isinstance(activity, dict):
                        for event_data in activity.get('events', []):
                            ts = event_data.get('timestamp', datetime.now().timestamp())
                            event = UniversalEvent(
                                timestamp=self.parse_timestamp(ts),
                                user_id=self.hash_user_id('facebook_user'),
                                channel='Paid Social',
                                event_type=self._classify_event_type(event_data),
                                context={
                                    'device': 'unknown',
                                    'intent_signal': self._infer_intent_from_type(
                                        event_data.get('type', '')
                                    ),
                                    'session_depth': 'unknown',
                                    'source_platform': activity.get('name', 'unknown')
                                },
                                metadata={
                                    'business': activity.get('name', 'unknown'),
                                    'event_type': event_data.get('type', 'unknown'),
                                    'source_file': source_key
                                }
                            )
                            events.append(event)

        elif isinstance(data, list):
            # Handle direct list of advertisers or events
            for item in data:
                if isinstance(item, dict):
                    # Check if it's an advertiser
                    if 'name' in item and 'timestamp' in item:
                        event = UniversalEvent(
                            timestamp=self.parse_timestamp(item.get('timestamp', datetime.now().timestamp())),
                            user_id=self.hash_user_id('facebook_user'),
                            channel='Paid Social',
                            event_type='click',
                            context={
                                'device': 'unknown',
                                'intent_signal': 'medium',
                                'session_depth': 'unknown',
                                'source_platform': 'facebook'
                            },
                            metadata={
                                'advertiser': item.get('name', 'unknown'),
                                'source_file': source_key
                            }
                        )
                        events.append(event)

        return events

    def _parse_off_facebook(self) -> List[UniversalEvent]:
        """Parse off-Facebook activity."""
        events = []

        for key, data in self.raw_data.items():
            # Check key name for patterns
            key_match = 'off_facebook' in key.lower() or 'off-facebook' in key.lower()
            
            if isinstance(data, dict):
                # Try finding off_facebook_activity_v2 in the data
                if 'off_facebook_activity_v2' in data:
                    data = data['off_facebook_activity_v2']
                # Also handle case where data is directly the activity list
                elif key == 'main' and isinstance(data, dict):
                    # When loading single file, search for activity data
                    for k, v in data.items():
                        if 'off_facebook' in k.lower():
                            if isinstance(v, dict) and 'off_facebook_activity_v2' in v:
                                data = v['off_facebook_activity_v2']
                                break
                            elif isinstance(v, list):
                                data = v
                                break
                
                # Process as list of businesses
                if isinstance(data, list):
                    for business in data:
                        if isinstance(business, dict):
                            business_name = business.get('name', 'unknown')
                            for event_data in business.get('events', []):
                                if isinstance(event_data, dict):
                                    ts = event_data.get('timestamp', datetime.now().timestamp())
                                    event = UniversalEvent(
                                        timestamp=self.parse_timestamp(ts),
                                        user_id=self.hash_user_id('facebook_user'),
                                        channel=self._map_business_to_channel(business_name),
                                        event_type=self._classify_event_type(event_data),
                                        context={
                                            'device': 'unknown',
                                            'intent_signal': self._infer_intent_from_type(
                                                event_data.get('type', '')
                                            ),
                                            'session_depth': 'unknown',
                                            'source_platform': business_name
                                        },
                                        metadata={
                                            'business': business_name,
                                            'raw_type': event_data.get('type', 'unknown'),
                                            'source_file': key
                                        }
                                    )
                                    events.append(event)

        return events

    def _parse_searches(self) -> List[UniversalEvent]:
        """Parse search history."""
        events = []

        for key, data in self.raw_data.items():
            if 'search' in key.lower():
                if isinstance(data, dict) and 'searches_v2' in data:
                    for search in data['searches_v2']:
                        if isinstance(search, dict):
                            ts = search.get('timestamp', datetime.now().timestamp())
                            event = UniversalEvent(
                                timestamp=self.parse_timestamp(ts),
                                user_id=self.hash_user_id('facebook_user'),
                                channel='Organic Social',
                                event_type='engagement',
                                context={
                                    'device': 'unknown',
                                    'intent_signal': 'high',  # Searches indicate intent
                                    'session_depth': 'unknown',
                                    'source_platform': 'facebook'
                                },
                                metadata={
                                    'search_type': 'facebook_search',
                                    'source_file': key
                                }
                            )
                            events.append(event)

        return events

    def _parse_posts(self) -> List[UniversalEvent]:
        """Parse posts and interactions."""
        events = []

        post_patterns = ['posts', 'comments', 'reactions', 'likes']

        for key, data in self.raw_data.items():
            if any(p in key.lower() for p in post_patterns):
                if isinstance(data, list):
                    for item in data:
                        event = self._item_to_event(item, 'engagement', key)
                        if event:
                            events.append(event)
                elif isinstance(data, dict):
                    for sub_key in ['posts', 'comments', 'reactions']:
                        if sub_key in data:
                            for item in data[sub_key]:
                                event = self._item_to_event(item, 'engagement', key)
                                if event:
                                    events.append(event)

        return events

    def _parse_messages(self) -> List[UniversalEvent]:
        """Parse message metadata (not content)."""
        events = []

        for key, data in self.raw_data.items():
            if 'messages' in key.lower() or 'inbox' in key.lower():
                if isinstance(data, dict) and 'messages' in data:
                    for msg in data['messages']:
                        if isinstance(msg, dict):
                            ts = msg.get('timestamp_ms', datetime.now().timestamp() * 1000)
                            event = UniversalEvent(
                                timestamp=self.parse_timestamp(ts / 1000),
                                user_id=self.hash_user_id('facebook_user'),
                                channel='Organic Social',
                                event_type='engagement',
                                context={
                                    'device': 'unknown',
                                    'intent_signal': 'medium',
                                    'session_depth': 'unknown',
                                    'source_platform': 'messenger'
                                },
                                metadata={
                                    'message_type': msg.get('type', 'unknown'),
                                    'source_file': key
                                }
                            )
                            events.append(event)

        return events

    def _item_to_event(
        self,
        item: Dict,
        default_type: str,
        source_key: str
    ) -> Optional[UniversalEvent]:
        """Convert a generic item to UniversalEvent."""
        if not isinstance(item, dict):
            return None

        # Find timestamp
        ts = None
        for ts_key in ['timestamp', 'timestamp_ms', 'time', 'created_time', 'date']:
            if ts_key in item:
                ts = item[ts_key]
                if ts_key == 'timestamp_ms':
                    ts = ts / 1000
                break

        if ts is None:
            ts = datetime.now().timestamp()

        return UniversalEvent(
            timestamp=self.parse_timestamp(ts),
            user_id=self.hash_user_id('facebook_user'),
            channel='Organic Social',
            event_type=default_type,
            context={
                'device': 'unknown',
                'intent_signal': 'medium',
                'session_depth': 'unknown',
                'source_platform': 'facebook'
            },
            metadata={
                'source_file': source_key
            }
        )

    def _classify_event_type(self, event_data: Dict) -> str:
        """Classify Facebook event type to universal type."""
        raw_type = str(event_data.get('type', '')).lower()

        if any(x in raw_type for x in ['purchase', 'buy', 'order', 'checkout']):
            return 'conversion'
        elif any(x in raw_type for x in ['click', 'view', 'visit', 'page']):
            return 'click'
        else:
            return 'engagement'

    def _infer_intent_from_type(self, event_type: str) -> str:
        """Infer intent signal from event type."""
        event_type = event_type.lower()

        if any(x in event_type for x in ['purchase', 'checkout', 'buy']):
            return 'high'
        elif any(x in event_type for x in ['add_to_cart', 'wishlist', 'save']):
            return 'high'
        elif any(x in event_type for x in ['view', 'click', 'visit']):
            return 'medium'
        else:
            return 'low'

    def _map_business_to_channel(self, business_name: str) -> str:
        """Map business name to channel."""
        name_lower = business_name.lower()

        # E-commerce
        if any(x in name_lower for x in ['amazon', 'ebay', 'etsy', 'shopify']):
            return 'Referral'

        # Social
        if any(x in name_lower for x in ['instagram', 'twitter', 'tiktok', 'pinterest']):
            return 'Organic Social'

        # Search
        if any(x in name_lower for x in ['google', 'bing', 'yahoo']):
            return 'Organic Search'

        # Default to Paid Social (most off-Facebook activity is ad-related)
        return 'Paid Social'

    def _add_session_context(
        self,
        events: List[UniversalEvent]
    ) -> List[UniversalEvent]:
        """Add session depth context to events."""
        # Group by user (in this case, single user)
        for i, event in enumerate(events):
            depth = self.calculate_session_depth(
                [e.to_dict() for e in events], i
            )
            event.context['session_depth'] = depth

        return events

    def detect_conversions(self, events: List[Dict]) -> List[Dict]:
        """
        Identify conversion events.

        For Facebook data, conversions are typically:
        - Purchase events in off-Facebook activity
        - App install events
        - Lead generation events
        """
        for event in events:
            raw_type = str(event.get('type', '')).lower()
            if any(x in raw_type for x in ['purchase', 'buy', 'order', 'lead', 'install']):
                event['is_conversion'] = True
                event['event_type'] = 'conversion'
            else:
                event['is_conversion'] = False

        return events


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        adapter = FacebookAdapter(sys.argv[1])
        events = adapter.parse()
        print(f"Parsed {len(events)} events")
        print()
        print("Summary:")
        print(json.dumps(adapter.summary(), indent=2))
    else:
        print("Usage: python facebook_adapter.py <path_to_facebook_export>")
