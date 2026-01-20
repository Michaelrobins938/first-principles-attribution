"""
Browser History Adapter

Parses browser history exports (Chrome, Firefox, Safari) into universal events.
Supports JSON and CSV export formats from various browsers.

Supported Sources:
- Chrome/Edge History (JSON export via extensions)
- Firefox JSON backups
- Safari Reading List exports
- Generic browser history CSV

Usage:
    from src.adapters import BrowserHistoryAdapter

    adapter = BrowserHistoryAdapter('browser_history.json')
    events = adapter.parse()
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import re

from .base_adapter import BaseAdapter, UniversalEvent
from .channel_taxonomy import normalize_channel, ChannelTaxonomy


class BrowserHistoryAdapter(BaseAdapter):
    """
    Adapter for browser history data exports.

    Handles various browser export formats and normalizes to universal events.
    """

    def __init__(self, source_path: str, browser_type: str = 'auto'):
        """
        Initialize browser history adapter.

        Parameters
        ----------
        source_path : str
            Path to browser history export file
        browser_type : str
            Browser type ('chrome', 'firefox', 'safari', 'auto')
        """
        super().__init__(source_path)
        self.source_name = "browser_history"
        self.browser_type = browser_type
        self.raw_data: List[Dict] = []
        self.taxonomy = ChannelTaxonomy()

    def parse(self) -> List[UniversalEvent]:
        """Parse browser history into universal events."""
        self._detect_browser_type()
        self._load_data()

        events = []
        for item in self.raw_data:
            event = self._convert_item(item)
            if event:
                events.append(event)

        events.sort(key=lambda e: e.timestamp)
        events = self._add_session_context(events)

        self.events = events
        return events

    def _detect_browser_type(self):
        """Auto-detect browser type from file structure."""
        if self.browser_type != 'auto':
            return

        path = Path(self.source_path)
        if not path.exists():
            return

        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                self.browser_type = 'generic_csv'
                return

        # Check for browser-specific structures
        if isinstance(data, list) and len(data) > 0:
            first = data[0]
            if 'URL' in first and 'visitTime' in first:
                self.browser_type = 'chrome'
            elif 'uri' in first and 'visitDate' in first:
                self.browser_type = 'firefox'
            elif 'url' in first and 'title' in first and 'lastVisitTime' in first:
                self.browser_type = 'chrome_new'

        elif isinstance(data, dict):
            if 'Browser_History' in data:
                self.browser_type = 'chrome_new'
            elif 'history' in data:
                self.browser_type = 'firefox'

    def _load_data(self):
        """Load browser history data."""
        path = Path(self.source_path)

        if path.suffix.lower() == '.csv':
            self._load_csv(path)
        else:
            self._load_json(path)

    def _load_json(self, path: Path):
        """Load JSON format browser history."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            self.raw_data = data
        elif isinstance(data, dict):
            # Handle nested structures
            for key in ['Browser_History', 'history', 'items', 'results']:
                if key in data:
                    items = data[key]
                    if isinstance(items, list):
                        self.raw_data = items
                        return
            # Use dict as single item
            self.raw_data = [data]

    def _load_csv(self, path: Path):
        """Load CSV format browser history."""
        import csv

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.raw_data.append(row)

    def _convert_item(self, item: Dict) -> Optional[UniversalEvent]:
        """Convert browser history item to UniversalEvent."""
        # Extract URL
        url = self._extract_url(item)
        if not url:
            return None

        # Extract timestamp
        timestamp = self._extract_timestamp(item)
        if not timestamp:
            return None

        # Extract title
        title = self._extract_title(item)

        # Determine channel from URL
        channel = self._determine_channel(url)

        # Infer device (browser history typically desktop)
        device = 'desktop'

        # Infer intent from URL and title
        intent = self._infer_intent(url, title)

        return UniversalEvent(
            timestamp=timestamp,
            user_id=self.hash_user_id('browser_user', 'history'),
            channel=channel,
            event_type='pageview',
            context={
                'device': device,
                'intent_signal': intent,
                'session_depth': 'unknown',
                'source_platform': f'browser_{self.browser_type}'
            },
            conversion_value=0.0,
            metadata={
                'url': url,
                'title': title,
                'browser_type': self.browser_type
            }
        )

    def _extract_url(self, item: Dict) -> Optional[str]:
        """Extract URL from item."""
        url_fields = ['URL', 'url', 'uri', 'link', 'href']

        for field in url_fields:
            if field in item and item[field]:
                return str(item[field])

        return None

    def _extract_timestamp(self, item: Dict) -> Optional[str]:
        """Extract and convert timestamp."""
        ts_fields = [
            ('visitTime', 1000),  # Chrome: milliseconds
            ('lastVisitTime', 1000),  # Chrome new: milliseconds
            ('visitDate', 1),  # Firefox: microseconds
            ('date', 1),  # Generic
            ('timestamp', 1),  # Generic Unix
            ('time', 1000),  # Generic milliseconds
        ]

        for field, multiplier in ts_fields:
            if field in item and item[field]:
                ts = item[field]
                if isinstance(ts, (int, float)):
                    ts = ts * multiplier
                    return self.parse_timestamp(ts / 1000 if multiplier > 1 else ts)

        return None

    def _extract_title(self, item: Dict) -> str:
        """Extract page title."""
        title_fields = ['title', 'Title', 'name', 'Name']

        for field in title_fields:
            if field in item and item[field]:
                return str(item[field])

        return ''

    def _determine_channel(self, url: str) -> str:
        """Determine channel from URL."""
        url_lower = url.lower()

        # Search engines
        search_domains = [
            'google.com/search', 'bing.com/search', 'yahoo.com/search',
            'duckduckgo.com', 'baidu.com', 'yandex.com'
        ]
        if any(d in url_lower for d in search_domains):
            return 'Organic Search'

        # Social media
        social_domains = [
            'facebook.com', 'twitter.com', 'x.com', 'linkedin.com',
            'instagram.com', 'pinterest.com', 'reddit.com', 'tiktok.com',
            'youtube.com', 'tumblr.com'
        ]
        if any(d in url_lower for d in social_domains):
            return 'Organic Social'

        # Email
        email_domains = [
            'mail.google.com', 'outlook.live.com', 'mail.yahoo.com',
            'protonmail.com', 'icloud.com'
        ]
        if any(d in url_lower for d in email_domains):
            return 'Email'

        # Direct navigation (typed URL, bookmark)
        if url_lower.startswith('about:') or url_lower.startswith('chrome://'):
            return 'Direct'

        # Check for UTM parameters
        if 'utm_source=' in url_lower:
            utm_source = self._extract_param(url, 'utm_source')
            if utm_source:
                return normalize_channel(utm_source, 'ga')

        # Check for referral
        if 'referrer' in url_lower or 'ref=' in url_lower:
            return 'Referral'

        return 'Direct'

    def _extract_param(self, url: str, param: str) -> str:
        """Extract URL parameter value."""
        pattern = rf'{param}=([^&]+)'
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
        return ''

    def _infer_intent(self, url: str, title: str) -> str:
        """Infer intent signal from URL and title."""
        content = (url + ' ' + (title or '')).lower()

        # High intent
        high_intent = [
            'checkout', 'purchase', 'buy', 'order', 'payment',
            'pricing', 'subscribe', 'signup', 'register'
        ]
        if any(kw in content for kw in high_intent):
            return 'high'

        # Low intent
        low_intent = [
            'about', 'blog', 'news', 'faq', 'help', 'contact',
            'terms', 'privacy', 'conditions'
        ]
        if any(kw in content for kw in low_intent):
            return 'low'

        return 'medium'

    def _add_session_context(
        self,
        events: List[UniversalEvent]
    ) -> List[UniversalEvent]:
        """Add session depth context."""
        for i, event in enumerate(events):
            if i < 2:
                depth = 'shallow'
            elif i < 5:
                depth = 'medium'
            else:
                depth = 'deep'
            event.context['session_depth'] = depth

        return events

    def detect_conversions(self, events: List[Dict]) -> List[Dict]:
        """Identify conversion events (rare in browser history)."""
        for event in events:
            url = event.get('url', '').lower()
            if any(kw in url for kw in ['checkout', 'purchase', 'order-confirm']):
                event['is_conversion'] = True
            else:
                event['is_conversion'] = False
        return events


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        adapter = BrowserHistoryAdapter(sys.argv[1])
        events = adapter.parse()
        print(f"Parsed {len(events)} events")
        print()
        print("Summary:")
        print(json.dumps(adapter.summary(), indent=2))
    else:
        print("Usage: python browser_history_adapter.py <path_to_export>")
