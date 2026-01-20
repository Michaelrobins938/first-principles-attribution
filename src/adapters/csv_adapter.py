"""
CSV Adapter for Generic Data Import

Parses flexible CSV formats into universal events.
Supports column mapping and various CSV conventions.

Usage:
    from src.adapters import CSVAdapter

    # Auto-detect columns
    adapter = CSVAdapter('data.csv')
    events = adapter.parse()

    # Custom column mapping
    adapter = CSVAdapter('data.csv', column_mapping={
        'timestamp': 'date_column',
        'user_id': 'user_column',
        'channel': 'source_column'
    })
    events = adapter.parse()
"""

import csv
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base_adapter import BaseAdapter, UniversalEvent
from .channel_taxonomy import normalize_channel


class CSVAdapter(BaseAdapter):
    """
    Adapter for generic CSV data imports.

    Supports flexible column mapping and common CSV formats.
    """

    def __init__(
        self,
        source_path: str,
        column_mapping: Optional[Dict[str, str]] = None,
        has_header: bool = True
    ):
        """
        Initialize CSV adapter.

        Parameters
        ----------
        source_path : str
            Path to CSV file
        column_mapping : dict, optional
            Mapping from standard fields to CSV column names
        has_header : bool
            Whether first row is header (default: True)
        """
        super().__init__(source_path)
        self.source_name = "csv"
        self.column_mapping = column_mapping or self._default_mapping()
        self.has_header = has_header
        self.raw_data: List[Dict] = []

    def _default_mapping(self) -> Dict[str, str]:
        """Default column mapping."""
        return {
            'timestamp': 'timestamp',
            'user_id': 'user_id',
            'channel': 'channel',
            'event_type': 'event_type',
            'device': 'device',
            'url': 'url',
            'title': 'title',
            'conversion_value': 'conversion_value'
        }

    def parse(self) -> List[UniversalEvent]:
        """Parse CSV file into universal events."""
        self._load_csv()

        events = []
        for row in self.raw_data:
            event = self._convert_row(row)
            if event:
                events.append(event)

        events.sort(key=lambda e: e.timestamp)
        events = self._add_session_context(events)

        self.events = events
        return events

    def _load_csv(self):
        """Load CSV data with flexible parsing."""
        path = Path(self.source_path)

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        sniffer = csv.Sniffer()
        has_header = sniffer.has_header(content) if self.has_header else False

        reader = csv.DictReader(
            content.splitlines(),
            skipinitialspace=True
        )

        for row in reader:
            # Clean row values
            cleaned = {k: v.strip() for k, v in row.items() if v}
            if cleaned:
                self.raw_data.append(cleaned)

    def _convert_row(self, row: Dict) -> Optional[UniversalEvent]:
        """Convert CSV row to UniversalEvent."""
        # Map columns using custom or default mapping
        mapped = self._map_columns(row)

        # Required: timestamp
        timestamp = mapped.get('timestamp')
        if not timestamp:
            return None

        # Required: user_id
        user_id = mapped.get('user_id', 'anonymous')

        # Channel
        channel = mapped.get('channel', 'Direct')

        # Event type
        event_type = mapped.get('event_type', 'engagement')

        # Device
        device = self.infer_device(
            user_agent=mapped.get('user_agent', ''),
            metadata={'device': mapped.get('device', '')}
        )

        # Intent
        intent = self.infer_intent({
            'url': mapped.get('url', ''),
            'title': mapped.get('title', '')
        })

        # Conversion value
        conversion_value = 0.0
        if 'conversion_value' in mapped:
            try:
                conversion_value = float(mapped['conversion_value'])
            except (ValueError, TypeError):
                pass

        return UniversalEvent(
            timestamp=self.parse_timestamp(timestamp),
            user_id=self.hash_user_id(user_id, 'csv'),
            channel=normalize_channel(channel, 'ga'),
            event_type=event_type,
            context={
                'device': device,
                'intent_signal': intent,
                'session_depth': 'unknown',
                'source_platform': 'csv_import'
            },
            conversion_value=conversion_value,
            metadata={
                'original_row': row,
                'source_file': self.source_path
            }
        )

    def _map_columns(self, row: Dict) -> Dict[str, str]:
        """Apply column mapping to row."""
        mapped = {}

        for standard_field, column_name in self.column_mapping.items():
            if column_name in row:
                mapped[standard_field] = row[column_name]

        return mapped

    def _add_session_context(
        self,
        events: List[UniversalEvent]
    ) -> List[UniversalEvent]:
        """Add session depth context."""
        user_events = {}
        for i, event in enumerate(events):
            uid = event.user_id
            if uid not in user_events:
                user_events[uid] = []
            user_events[uid].append((i, event))

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
        """Identify conversion events."""
        for event in events:
            event_type = event.get('event_type', '').lower()
            if event_type in ['purchase', 'conversion', 'sale', 'checkout']:
                event['is_conversion'] = True
            else:
                event['is_conversion'] = False
        return events

    @classmethod
    def from_dataframe(cls, df, column_mapping: Optional[Dict[str, str]] = None):
        """
        Create adapter from pandas DataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame with event data
        column_mapping : dict, optional
            Column mapping
        """
        adapter = cls.__new__(cls)
        adapter.source_path = None
        adapter.source_name = "csv_dataframe"
        adapter.column_mapping = column_mapping or adapter._default_mapping()
        adapter.has_header = False
        adapter.raw_data = df.to_dict('records')
        adapter.events = []
        return adapter


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        adapter = CSVAdapter(sys.argv[1])
        events = adapter.parse()
        print(f"Parsed {len(events)} events")
        print()
        print("Summary:")
        import json
        print(json.dumps(adapter.summary(), indent=2))
    else:
        print("Usage: python csv_adapter.py <path_to_csv>")
