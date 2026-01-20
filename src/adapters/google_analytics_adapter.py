"""
Google Analytics 4 Adapter

Parses GA4 data exports (BigQuery export format or JSON export)
into universal events for attribution analysis.

Supported Formats:
- BigQuery export JSON (events_* tables)
- Google Analytics Data API response
- Google Takeout export
- Custom GA4 JSON export

Key GA4 Fields Mapped:
- event_name -> event_type
- traffic_source.medium -> channel
- user_pseudo_id -> user_id (hashed)
- event_timestamp -> timestamp
- device.category -> context.device

Usage:
    from src.adapters import GoogleAnalyticsAdapter

    adapter = GoogleAnalyticsAdapter('ga4_export.json')
    events = adapter.parse()
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base_adapter import BaseAdapter, UniversalEvent
from .channel_taxonomy import normalize_channel, ChannelTaxonomy


class GoogleAnalyticsAdapter(BaseAdapter):
    """
    Adapter for Google Analytics 4 data exports.

    Handles BigQuery export format and various JSON export structures.
    """

    def __init__(self, source_path: str):
        """
        Initialize GA4 adapter.

        Parameters
        ----------
        source_path : str
            Path to GA4 export file or directory
        """
        super().__init__(source_path)
        self.source_name = "google_analytics"
        self.raw_data = []
        self.taxonomy = ChannelTaxonomy()

    def parse(self) -> List[UniversalEvent]:
        """
        Parse GA4 export into universal events.

        Returns
        -------
        list
            List of UniversalEvent objects
        """
        # Load data
        if os.path.isdir(self.source_path):
            self._load_directory()
        else:
            self._load_file(self.source_path)

        # Convert to universal events
        events = []

        for raw_event in self.raw_data:
            event = self._convert_event(raw_event)
            if event:
                events.append(event)

        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)

        # Add session context
        events = self._add_session_context(events)

        self.events = events
        return events

    def _load_directory(self):
        """Load all GA4 JSON files from directory."""
        path = Path(self.source_path)

        for json_file in path.rglob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if isinstance(data, list):
                    self.raw_data.extend(data)
                elif isinstance(data, dict):
                    # Handle nested structures
                    if 'rows' in data:
                        self.raw_data.extend(data['rows'])
                    elif 'events' in data:
                        self.raw_data.extend(data['events'])
                    else:
                        self.raw_data.append(data)

            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

    def _load_file(self, filepath: str):
        """Load single GA4 JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            self.raw_data = data
        elif isinstance(data, dict):
            if 'rows' in data:
                self.raw_data = data['rows']
            elif 'events' in data:
                self.raw_data = data['events']
            elif 'data' in data:
                self.raw_data = data['data']
            else:
                self.raw_data = [data]

    def _convert_event(self, raw: Dict) -> Optional[UniversalEvent]:
        """
        Convert GA4 event to universal event.

        Parameters
        ----------
        raw : dict
            Raw GA4 event data

        Returns
        -------
        UniversalEvent or None
        """
        if not isinstance(raw, dict):
            return None

        # Extract timestamp
        timestamp = self._extract_timestamp(raw)
        if not timestamp:
            return None

        # Extract user ID
        user_id = self._extract_user_id(raw)

        # Extract channel
        channel = self._extract_channel(raw)

        # Extract event type
        event_type = self._extract_event_type(raw)

        # Extract device
        device = self._extract_device(raw)

        # Extract intent
        intent = self._infer_intent(raw)

        # Extract conversion value
        conversion_value = self._extract_conversion_value(raw)

        return UniversalEvent(
            timestamp=timestamp,
            user_id=user_id,
            channel=channel,
            event_type=event_type,
            context={
                'device': device,
                'intent_signal': intent,
                'session_depth': 'unknown',
                'source_platform': 'google_analytics'
            },
            conversion_value=conversion_value,
            metadata={
                'ga_event_name': raw.get('event_name', raw.get('eventName', '')),
                'ga_session_id': self._get_nested(raw, 'session_id', ''),
                'ga_page_path': self._get_nested(raw, 'page_location', '')
            }
        )

    def _extract_timestamp(self, raw: Dict) -> Optional[str]:
        """Extract and convert timestamp."""
        # Try different timestamp field names
        ts_fields = [
            'event_timestamp',
            'eventTimestamp',
            'timestamp',
            'event_time',
            'dateHourMinute'
        ]

        for field in ts_fields:
            if field in raw:
                ts = raw[field]

                # GA4 timestamps are in microseconds
                if isinstance(ts, (int, float)):
                    if ts > 1e15:  # Microseconds
                        ts = ts / 1e6
                    elif ts > 1e12:  # Milliseconds
                        ts = ts / 1e3

                return self.parse_timestamp(ts)

        # Try nested event_params
        params = raw.get('event_params', raw.get('eventParams', []))
        if isinstance(params, list):
            for param in params:
                if param.get('key') == 'ga_session_id':
                    # Fallback: use session start as timestamp
                    pass

        return None

    def _extract_user_id(self, raw: Dict) -> str:
        """Extract and hash user ID."""
        user_fields = [
            'user_pseudo_id',
            'userPseudoId',
            'user_id',
            'userId',
            'client_id',
            'clientId'
        ]

        for field in user_fields:
            if field in raw and raw[field]:
                return self.hash_user_id(str(raw[field]), 'ga')

        return self.hash_user_id('unknown_ga_user', 'ga')

    def _extract_channel(self, raw: Dict) -> str:
        """Extract and normalize channel."""
        # Try traffic_source fields
        traffic_source = raw.get('traffic_source', raw.get('trafficSource', {}))

        if isinstance(traffic_source, dict):
            medium = traffic_source.get('medium', traffic_source.get('source', ''))
            source = traffic_source.get('source', '')
            campaign = traffic_source.get('campaign', '')

            if medium:
                return normalize_channel(medium, 'ga', campaign)
            if source:
                return normalize_channel(source, 'ga', campaign, source)

        # Try flat fields
        for field in ['medium', 'source', 'channelGrouping', 'channel']:
            if field in raw and raw[field]:
                return normalize_channel(str(raw[field]), 'ga')

        # Try event_params
        params = self._get_event_params(raw)
        if 'source' in params:
            return normalize_channel(params['source'], 'ga')
        if 'medium' in params:
            return normalize_channel(params['medium'], 'ga')

        return 'Unknown'

    def _extract_event_type(self, raw: Dict) -> str:
        """Classify GA4 event to universal event type."""
        event_name = raw.get('event_name', raw.get('eventName', '')).lower()

        # Conversion events
        conversion_events = [
            'purchase', 'ecommerce_purchase', 'in_app_purchase',
            'generate_lead', 'sign_up', 'complete_registration',
            'add_payment_info', 'checkout_complete'
        ]
        if event_name in conversion_events or 'purchase' in event_name:
            return 'conversion'

        # Click events
        click_events = [
            'click', 'select_content', 'select_item',
            'add_to_cart', 'add_to_wishlist', 'begin_checkout'
        ]
        if event_name in click_events or 'click' in event_name:
            return 'click'

        # Pageview events
        if event_name in ['page_view', 'pageview', 'screen_view']:
            return 'pageview'

        # Default to engagement
        return 'engagement'

    def _extract_device(self, raw: Dict) -> str:
        """Extract device category."""
        device = raw.get('device', {})

        if isinstance(device, dict):
            category = device.get('category', device.get('deviceCategory', ''))
            if category:
                return category.lower()

        # Try flat fields
        if 'deviceCategory' in raw:
            return raw['deviceCategory'].lower()

        return 'unknown'

    def _infer_intent(self, raw: Dict) -> str:
        """Infer intent signal from event context."""
        event_name = raw.get('event_name', raw.get('eventName', '')).lower()

        # High intent events
        high_intent = [
            'add_to_cart', 'begin_checkout', 'add_payment_info',
            'purchase', 'sign_up', 'generate_lead'
        ]
        if event_name in high_intent:
            return 'high'

        # Medium intent events
        medium_intent = [
            'view_item', 'select_item', 'view_cart',
            'view_promotion', 'select_content'
        ]
        if event_name in medium_intent:
            return 'medium'

        # Check page path for intent signals
        page_path = self._get_nested(raw, 'page_location', '')
        if any(x in page_path.lower() for x in ['cart', 'checkout', 'pricing', 'buy']):
            return 'high'

        return 'low'

    def _extract_conversion_value(self, raw: Dict) -> float:
        """Extract conversion value if present."""
        # Try ecommerce fields
        ecommerce = raw.get('ecommerce', {})
        if isinstance(ecommerce, dict):
            value = ecommerce.get('purchase', {}).get('value', 0)
            if value:
                return float(value)

        # Try event_params
        params = self._get_event_params(raw)
        if 'value' in params:
            try:
                return float(params['value'])
            except (ValueError, TypeError):
                pass

        # Try direct value field
        if 'value' in raw:
            try:
                return float(raw['value'])
            except (ValueError, TypeError):
                pass

        return 0.0

    def _get_event_params(self, raw: Dict) -> Dict:
        """Extract event parameters as flat dict."""
        params = raw.get('event_params', raw.get('eventParams', []))

        if isinstance(params, list):
            result = {}
            for param in params:
                if isinstance(param, dict) and 'key' in param:
                    key = param['key']
                    value = param.get('value', param.get('string_value', ''))
                    if isinstance(value, dict):
                        value = value.get('string_value', value.get('int_value', ''))
                    result[key] = value
            return result

        elif isinstance(params, dict):
            return params

        return {}

    def _get_nested(self, raw: Dict, key: str, default: Any = None) -> Any:
        """Get value from nested structure."""
        # Try direct key
        if key in raw:
            return raw[key]

        # Try event_params
        params = self._get_event_params(raw)
        if key in params:
            return params[key]

        # Try nested dicts
        for nested_key in ['event_params', 'user_properties', 'device', 'geo']:
            if nested_key in raw and isinstance(raw[nested_key], dict):
                if key in raw[nested_key]:
                    return raw[nested_key][key]

        return default

    def _add_session_context(
        self,
        events: List[UniversalEvent]
    ) -> List[UniversalEvent]:
        """Add session depth context based on user journey position."""
        # Group events by user
        user_events = {}
        for i, event in enumerate(events):
            uid = event.user_id
            if uid not in user_events:
                user_events[uid] = []
            user_events[uid].append((i, event))

        # Calculate session depth per user
        for uid, user_event_list in user_events.items():
            for position, (idx, event) in enumerate(user_event_list):
                if position < 2:
                    depth = 'shallow'
                elif position < 5:
                    depth = 'medium'
                else:
                    depth = 'deep'
                events[idx].context['session_depth'] = depth

        return events

    def detect_conversions(self, events: List[Dict]) -> List[Dict]:
        """Identify conversion events in raw data."""
        conversion_events = [
            'purchase', 'ecommerce_purchase', 'in_app_purchase',
            'generate_lead', 'sign_up', 'complete_registration'
        ]

        for event in events:
            event_name = event.get('event_name', '').lower()
            if event_name in conversion_events:
                event['is_conversion'] = True
            else:
                event['is_conversion'] = False

        return events

    @classmethod
    def from_bigquery_export(cls, filepath: str) -> 'GoogleAnalyticsAdapter':
        """
        Create adapter from BigQuery export file.

        BigQuery exports GA4 data in a specific nested format.
        """
        adapter = cls(filepath)
        return adapter

    @classmethod
    def from_data_api(cls, response: Dict) -> 'GoogleAnalyticsAdapter':
        """
        Create adapter from GA4 Data API response.

        Parameters
        ----------
        response : dict
            Response from Google Analytics Data API
        """
        adapter = cls.__new__(cls)
        adapter.source_path = None
        adapter.source_name = "google_analytics_api"
        adapter.raw_data = []
        adapter.taxonomy = ChannelTaxonomy()

        # Parse API response
        if 'rows' in response:
            for row in response['rows']:
                event = {
                    'dimensions': {},
                    'metrics': {}
                }

                # Map dimension values
                dim_headers = response.get('dimensionHeaders', [])
                dim_values = row.get('dimensionValues', [])
                for header, value in zip(dim_headers, dim_values):
                    event['dimensions'][header.get('name', '')] = value.get('value', '')

                # Map metric values
                metric_headers = response.get('metricHeaders', [])
                metric_values = row.get('metricValues', [])
                for header, value in zip(metric_headers, metric_values):
                    event['metrics'][header.get('name', '')] = value.get('value', '')

                adapter.raw_data.append(event)

        return adapter


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        adapter = GoogleAnalyticsAdapter(sys.argv[1])
        events = adapter.parse()
        print(f"Parsed {len(events)} events")
        print()
        print("Summary:")
        print(json.dumps(adapter.summary(), indent=2))
    else:
        print("Usage: python google_analytics_adapter.py <path_to_ga4_export>")
