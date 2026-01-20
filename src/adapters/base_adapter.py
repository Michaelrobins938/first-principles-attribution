"""
Base Adapter and Universal Event Schema

All data sources are converted to this common format before
being processed by the attribution engine.

The Universal Event Schema ensures:
- Consistent field names across sources
- Privacy-preserving user identification
- Normalized channel taxonomy
- Structured context for psychographic weights
"""

import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field


# Universal Event Schema Definition
UNIVERSAL_EVENT_SCHEMA = {
    "type": "object",
    "required": ["timestamp", "user_id", "channel", "event_type"],
    "properties": {
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO8601 datetime of the event"
        },
        "user_id": {
            "type": "string",
            "description": "Hashed/anonymized user identifier"
        },
        "channel": {
            "type": "string",
            "description": "Normalized channel name from taxonomy"
        },
        "event_type": {
            "type": "string",
            "enum": ["pageview", "click", "engagement", "conversion"],
            "description": "Type of event"
        },
        "context": {
            "type": "object",
            "properties": {
                "device": {
                    "type": "string",
                    "enum": ["mobile", "desktop", "tablet", "unknown"]
                },
                "intent_signal": {
                    "type": "string",
                    "enum": ["high", "medium", "low", "unknown"]
                },
                "session_depth": {
                    "type": "string",
                    "enum": ["shallow", "medium", "deep", "unknown"]
                },
                "source_platform": {
                    "type": "string",
                    "description": "Original platform (facebook, google, etc.)"
                }
            }
        },
        "conversion_value": {
            "type": "number",
            "description": "Monetary value if conversion event"
        },
        "metadata": {
            "type": "object",
            "description": "Additional source-specific fields"
        }
    }
}


@dataclass
class UniversalEvent:
    """
    Universal event format for the attribution engine.

    All adapters convert source-specific formats into this structure.
    """
    timestamp: str  # ISO8601
    user_id: str    # Hashed identifier
    channel: str    # Normalized channel name
    event_type: str  # pageview, click, engagement, conversion

    # Optional context for psychographic weights
    context: Dict[str, str] = field(default_factory=lambda: {
        'device': 'unknown',
        'intent_signal': 'unknown',
        'session_depth': 'unknown',
        'source_platform': 'unknown'
    })

    # Conversion value (only for conversion events)
    conversion_value: float = 0.0

    # Source-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict) -> 'UniversalEvent':
        """Create from dictionary."""
        return cls(
            timestamp=data['timestamp'],
            user_id=data['user_id'],
            channel=data['channel'],
            event_type=data['event_type'],
            context=data.get('context', {}),
            conversion_value=data.get('conversion_value', 0.0),
            metadata=data.get('metadata', {})
        )

    def __repr__(self):
        return (f"UniversalEvent({self.timestamp[:10]}, "
                f"{self.channel}, {self.event_type})")


class BaseAdapter(ABC):
    """
    Abstract base class for data source adapters.

    All adapters must implement:
    - parse(): Convert source data to UniversalEvent list
    - detect_conversions(): Identify conversion events
    - extract_user_id(): Generate privacy-preserving user ID
    """

    def __init__(self, source_path: Optional[str] = None):
        """
        Initialize adapter.

        Parameters
        ----------
        source_path : str, optional
            Path to data file or directory
        """
        self.source_path = source_path
        self.events: List[UniversalEvent] = []
        self.source_name = "unknown"

    @abstractmethod
    def parse(self) -> List[UniversalEvent]:
        """
        Parse source data into universal events.

        Returns
        -------
        list
            List of UniversalEvent objects
        """
        pass

    @abstractmethod
    def detect_conversions(self, events: List[Dict]) -> List[Dict]:
        """
        Identify which events are conversions.

        Parameters
        ----------
        events : list
            Raw events from source

        Returns
        -------
        list
            Events with conversion flags
        """
        pass

    def hash_user_id(self, raw_id: str, salt: str = "") -> str:
        """
        Create privacy-preserving user identifier.

        Uses SHA256 hash to anonymize while preserving uniqueness.

        Parameters
        ----------
        raw_id : str
            Original user identifier
        salt : str
            Optional salt for additional privacy

        Returns
        -------
        str
            Hashed user ID (first 16 chars of hex digest)
        """
        combined = f"{raw_id}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def parse_timestamp(self, timestamp: Any) -> str:
        """
        Convert various timestamp formats to ISO8601.

        Parameters
        ----------
        timestamp : various
            Unix timestamp, datetime string, or datetime object

        Returns
        -------
        str
            ISO8601 formatted timestamp
        """
        if isinstance(timestamp, (int, float)):
            # Unix timestamp
            dt = datetime.fromtimestamp(timestamp)
            return dt.isoformat()
        elif isinstance(timestamp, datetime):
            return timestamp.isoformat()
        elif isinstance(timestamp, str):
            # Try common formats
            formats = [
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
                '%d/%m/%Y %H:%M:%S',
                '%m/%d/%Y %H:%M:%S',
            ]
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
            # Return as-is if can't parse
            return timestamp
        else:
            return datetime.now().isoformat()

    def infer_device(self, user_agent: str = "", metadata: Optional[Dict] = None) -> str:
        """
        Infer device type from user agent or metadata.

        Parameters
        ----------
        user_agent : str
            Browser user agent string
        metadata : dict
            Additional context

        Returns
        -------
        str
            'mobile', 'desktop', 'tablet', or 'unknown'
        """
        if metadata and 'device' in metadata:
            return metadata['device'].lower()

        ua_lower = user_agent.lower()

        if any(x in ua_lower for x in ['iphone', 'android', 'mobile']):
            return 'mobile'
        elif any(x in ua_lower for x in ['ipad', 'tablet']):
            return 'tablet'
        elif any(x in ua_lower for x in ['windows', 'macintosh', 'linux']):
            return 'desktop'
        else:
            return 'unknown'

    def infer_intent(self, event: Dict) -> str:
        """
        Infer user intent signal from event context.

        High intent indicators:
        - Purchase-related pages
        - Pricing pages
        - Checkout/cart actions
        - Long session duration

        Parameters
        ----------
        event : dict
            Raw event data

        Returns
        -------
        str
            'high', 'medium', 'low', or 'unknown'
        """
        high_intent_keywords = [
            'buy', 'purchase', 'checkout', 'cart', 'pricing',
            'subscribe', 'signup', 'register', 'order', 'payment'
        ]

        low_intent_keywords = [
            'about', 'blog', 'news', 'faq', 'help', 'contact'
        ]

        # Check URL or page title
        url = str(event.get('url', '')).lower()
        title = str(event.get('title', '')).lower()
        combined = url + ' ' + title

        if any(kw in combined for kw in high_intent_keywords):
            return 'high'
        elif any(kw in combined for kw in low_intent_keywords):
            return 'low'
        else:
            return 'medium'

    def calculate_session_depth(
        self,
        user_events: List[Dict],
        current_index: int
    ) -> str:
        """
        Calculate session depth (position in user journey).

        Parameters
        ----------
        user_events : list
            All events for this user (sorted by time)
        current_index : int
            Index of current event

        Returns
        -------
        str
            'shallow' (1-2), 'medium' (3-5), 'deep' (6+)
        """
        position = current_index + 1

        if position <= 2:
            return 'shallow'
        elif position <= 5:
            return 'medium'
        else:
            return 'deep'

    def validate_event(self, event: UniversalEvent) -> bool:
        """
        Validate event against schema.

        Parameters
        ----------
        event : UniversalEvent

        Returns
        -------
        bool
            True if valid
        """
        # Required fields
        if not event.timestamp:
            return False
        if not event.user_id:
            return False
        if not event.channel:
            return False
        if event.event_type not in ['pageview', 'click', 'engagement', 'conversion']:
            return False

        return True

    def export_events(self, filepath: str):
        """
        Export parsed events to JSON file.

        Parameters
        ----------
        filepath : str
            Output file path
        """
        output = {
            'source': self.source_name,
            'event_count': len(self.events),
            'generated_at': datetime.now().isoformat(),
            'schema_version': '1.0.0',
            'events': [e.to_dict() for e in self.events]
        }

        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)

    def summary(self) -> Dict:
        """
        Generate summary statistics for parsed events.

        Returns
        -------
        dict
            Summary statistics
        """
        if not self.events:
            return {'error': 'No events parsed'}

        channels = {}
        event_types = {}
        users = set()

        for e in self.events:
            channels[e.channel] = channels.get(e.channel, 0) + 1
            event_types[e.event_type] = event_types.get(e.event_type, 0) + 1
            users.add(e.user_id)

        return {
            'source': self.source_name,
            'total_events': len(self.events),
            'unique_users': len(users),
            'channels': channels,
            'event_types': event_types,
            'date_range': {
                'earliest': min(e.timestamp for e in self.events),
                'latest': max(e.timestamp for e in self.events)
            }
        }


def validate_events(events: List[UniversalEvent]) -> List[Dict]:
    """
    Validate a list of events and return validation report.

    Parameters
    ----------
    events : list
        List of UniversalEvent objects

    Returns
    -------
    list
        List of validation errors (empty if all valid)
    """
    errors = []

    for i, event in enumerate(events):
        if not event.timestamp:
            errors.append({'index': i, 'field': 'timestamp', 'error': 'missing'})
        if not event.user_id:
            errors.append({'index': i, 'field': 'user_id', 'error': 'missing'})
        if not event.channel:
            errors.append({'index': i, 'field': 'channel', 'error': 'missing'})
        if event.event_type not in ['pageview', 'click', 'engagement', 'conversion']:
            errors.append({
                'index': i,
                'field': 'event_type',
                'error': f'invalid value: {event.event_type}'
            })

    return errors


def merge_event_streams(
    *event_lists: List[UniversalEvent],
    sort_by_time: bool = True,
    deduplicate: bool = True
) -> List[UniversalEvent]:
    """
    Merge multiple event streams into one.

    Parameters
    ----------
    *event_lists : list
        Variable number of event lists to merge
    sort_by_time : bool
        Sort merged events chronologically
    deduplicate : bool
        Remove duplicate events

    Returns
    -------
    list
        Merged event list
    """
    merged = []

    for events in event_lists:
        merged.extend(events)

    if deduplicate:
        seen = set()
        unique = []
        for e in merged:
            key = (e.timestamp, e.user_id, e.channel, e.event_type)
            if key not in seen:
                seen.add(key)
                unique.append(e)
        merged = unique

    if sort_by_time:
        merged.sort(key=lambda e: e.timestamp)

    return merged
