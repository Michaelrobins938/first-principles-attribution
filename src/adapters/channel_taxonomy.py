"""
Channel Taxonomy for Multi-Source Attribution

Maps source-specific channel names to a unified taxonomy.
This ensures consistent attribution across data sources.

The taxonomy is hierarchical:
- Level 1: Broad category (Paid, Organic, Direct, Social, Email)
- Level 2: Specific channel (Google Ads, Facebook Ads, etc.)
- Level 3: Sub-channel (Brand search, Non-brand search, etc.)

Usage:
    from src.adapters.channel_taxonomy import normalize_channel

    # Normalize various source names
    normalize_channel('cpc')              # -> 'Paid Search'
    normalize_channel('facebook.com')     # -> 'Social'
    normalize_channel('newsletter')       # -> 'Email'
"""

from typing import Dict, List, Optional, Tuple
import re


# Master channel taxonomy
CHANNEL_TAXONOMY = {
    # Level 1 -> Level 2 -> Level 3
    'Paid': {
        'Paid Search': ['Brand Search', 'Non-Brand Search', 'Shopping'],
        'Paid Social': ['Facebook Ads', 'Instagram Ads', 'LinkedIn Ads', 'Twitter Ads', 'TikTok Ads'],
        'Display': ['Programmatic', 'Direct Buy', 'Retargeting'],
        'Video': ['YouTube Ads', 'OTT/CTV', 'Pre-roll'],
        'Affiliate': ['Partner', 'Influencer', 'Cashback'],
    },
    'Organic': {
        'Organic Search': ['Google', 'Bing', 'DuckDuckGo', 'Other Search'],
        'Organic Social': ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'TikTok', 'Reddit'],
        'Content': ['Blog', 'News', 'Press'],
        'Referral': ['Partner Sites', 'Review Sites', 'Forums'],
    },
    'Direct': {
        'Direct': ['Typed URL', 'Bookmark', 'App'],
        'Internal': ['Cross-sell', 'Upsell', 'Navigation'],
    },
    'Email': {
        'Email': ['Newsletter', 'Promotional', 'Transactional', 'Triggered'],
    },
    'Other': {
        'SMS': ['Marketing SMS', 'Transactional SMS'],
        'Push': ['App Push', 'Web Push'],
        'Offline': ['Store', 'Call Center', 'Event'],
        'Unknown': ['Unknown'],
    }
}


# Source-specific mappings to normalized channels
CHANNEL_MAPPINGS = {
    # Google Analytics medium/source mappings
    'ga': {
        # Mediums
        'cpc': 'Paid Search',
        'ppc': 'Paid Search',
        'paid search': 'Paid Search',
        'paidsearch': 'Paid Search',
        'organic': 'Organic Search',
        'referral': 'Referral',
        'social': 'Organic Social',
        'social-network': 'Organic Social',
        'social-media': 'Organic Social',
        'email': 'Email',
        'e-mail': 'Email',
        'newsletter': 'Email',
        'affiliate': 'Affiliate',
        'display': 'Display',
        'cpm': 'Display',
        'banner': 'Display',
        'video': 'Video',
        'cpv': 'Video',
        'none': 'Direct',
        '(none)': 'Direct',
        'direct': 'Direct',
        '(direct)': 'Direct',
        'push': 'Push',
        'sms': 'SMS',
        'not set': 'Unknown',
        '(not set)': 'Unknown',
    },

    # Facebook data export mappings
    'facebook': {
        'facebook': 'Organic Social',
        'fb': 'Organic Social',
        'facebook.com': 'Organic Social',
        'fb.com': 'Organic Social',
        'm.facebook.com': 'Organic Social',
        'l.facebook.com': 'Organic Social',
        'facebook ads': 'Paid Social',
        'fb ads': 'Paid Social',
        'facebook_ads': 'Paid Social',
        'instagram': 'Organic Social',
        'instagram.com': 'Organic Social',
        'ig': 'Organic Social',
        'instagram ads': 'Paid Social',
        'messenger': 'Organic Social',
        'whatsapp': 'Organic Social',
    },

    # Common URL/domain patterns
    'domains': {
        'google.com': 'Organic Search',
        'google': 'Organic Search',
        'bing.com': 'Organic Search',
        'bing': 'Organic Search',
        'yahoo.com': 'Organic Search',
        'duckduckgo.com': 'Organic Search',
        'baidu.com': 'Organic Search',
        'yandex.com': 'Organic Search',
        'facebook.com': 'Organic Social',
        'twitter.com': 'Organic Social',
        'x.com': 'Organic Social',
        'linkedin.com': 'Organic Social',
        'instagram.com': 'Organic Social',
        'pinterest.com': 'Organic Social',
        'reddit.com': 'Organic Social',
        'tiktok.com': 'Organic Social',
        'youtube.com': 'Video',
        'youtu.be': 'Video',
        'vimeo.com': 'Video',
        'medium.com': 'Content',
        'substack.com': 'Content',
        'mail.google.com': 'Email',
        'outlook.live.com': 'Email',
        'mail.yahoo.com': 'Email',
    },

    # UTM campaign patterns
    'utm_patterns': {
        r'brand': 'Brand Search',
        r'nonbrand|non-brand|non_brand': 'Non-Brand Search',
        r'retarget|remarketing|remarket': 'Retargeting',
        r'prospecting|prospect': 'Display',
        r'newsletter|news_letter': 'Email',
        r'promo|promotional': 'Email',
        r'affiliate|partner': 'Affiliate',
        r'influencer': 'Affiliate',
    }
}


class ChannelTaxonomy:
    """
    Channel taxonomy manager for normalizing channel names.

    Provides consistent channel classification across data sources.
    """

    def __init__(self, custom_mappings: Optional[Dict] = None):
        """
        Initialize taxonomy with optional custom mappings.

        Parameters
        ----------
        custom_mappings : dict, optional
            Additional source-specific mappings
        """
        self.mappings = CHANNEL_MAPPINGS.copy()
        if custom_mappings:
            for source, mapping in custom_mappings.items():
                if source in self.mappings:
                    self.mappings[source].update(mapping)
                else:
                    self.mappings[source] = mapping

    def normalize(
        self,
        raw_channel: str,
        source: str = 'ga',
        utm_campaign: str = '',
        url: str = ''
    ) -> str:
        """
        Normalize a channel name to taxonomy.

        Parameters
        ----------
        raw_channel : str
            Raw channel/medium/source from data
        source : str
            Data source ('ga', 'facebook', 'domains')
        utm_campaign : str
            UTM campaign parameter (for additional context)
        url : str
            Referrer URL (for domain-based classification)

        Returns
        -------
        str
            Normalized channel name
        """
        if not raw_channel:
            return 'Unknown'

        raw_lower = raw_channel.lower().strip()

        # Try source-specific mapping first
        if source in self.mappings:
            if raw_lower in self.mappings[source]:
                return self.mappings[source][raw_lower]

        # Try GA mappings (most common)
        if raw_lower in self.mappings['ga']:
            return self.mappings['ga'][raw_lower]

        # Try domain extraction from URL
        if url:
            domain = self._extract_domain(url)
            if domain in self.mappings['domains']:
                return self.mappings['domains'][domain]

        # Try UTM campaign patterns
        if utm_campaign:
            for pattern, channel in self.mappings['utm_patterns'].items():
                if re.search(pattern, utm_campaign.lower()):
                    return channel

        # Fuzzy matching for common terms
        normalized = self._fuzzy_match(raw_lower)
        if normalized:
            return normalized

        # Default to Unknown
        return 'Unknown'

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        url = url.lower()
        # Remove protocol
        url = re.sub(r'^https?://', '', url)
        # Remove www
        url = re.sub(r'^www\.', '', url)
        # Get domain
        domain = url.split('/')[0]
        return domain

    def _fuzzy_match(self, raw: str) -> Optional[str]:
        """Fuzzy match channel name."""
        # Search engine patterns
        if any(x in raw for x in ['google', 'bing', 'yahoo', 'search']):
            if any(x in raw for x in ['paid', 'cpc', 'ppc', 'ad']):
                return 'Paid Search'
            return 'Organic Search'

        # Social patterns
        if any(x in raw for x in ['facebook', 'twitter', 'linkedin', 'instagram', 'social', 'tiktok']):
            if any(x in raw for x in ['paid', 'ad', 'sponsored']):
                return 'Paid Social'
            return 'Organic Social'

        # Email patterns
        if any(x in raw for x in ['email', 'mail', 'newsletter', 'smtp']):
            return 'Email'

        # Direct patterns
        if any(x in raw for x in ['direct', 'none', 'typed', 'bookmark']):
            return 'Direct'

        # Display patterns
        if any(x in raw for x in ['display', 'banner', 'programmatic', 'dv360']):
            return 'Display'

        # Video patterns
        if any(x in raw for x in ['youtube', 'video', 'vimeo', 'ctv', 'ott']):
            return 'Video'

        return None

    def get_hierarchy(self, channel: str) -> Tuple[str, str, str]:
        """
        Get full hierarchy for a channel.

        Returns
        -------
        tuple
            (Level1, Level2, Level3) or ('Unknown', 'Unknown', 'Unknown')
        """
        for level1, level2_dict in CHANNEL_TAXONOMY.items():
            for level2, level3_list in level2_dict.items():
                if channel == level2:
                    return (level1, level2, level3_list[0] if level3_list else level2)
                if channel in level3_list:
                    return (level1, level2, channel)

        return ('Unknown', 'Unknown', channel)

    def list_channels(self, level: int = 2) -> List[str]:
        """
        List all channels at a given taxonomy level.

        Parameters
        ----------
        level : int
            1 = broad categories, 2 = specific channels, 3 = sub-channels

        Returns
        -------
        list
            Channel names
        """
        channels = []

        for level1, level2_dict in CHANNEL_TAXONOMY.items():
            if level == 1:
                channels.append(level1)
            else:
                for level2, level3_list in level2_dict.items():
                    if level == 2:
                        channels.append(level2)
                    else:
                        channels.extend(level3_list)

        return sorted(set(channels))


# Convenience function
def normalize_channel(
    raw_channel: str,
    source: str = 'ga',
    utm_campaign: str = '',
    url: str = ''
) -> str:
    """
    Normalize a channel name to standard taxonomy.

    Parameters
    ----------
    raw_channel : str
        Raw channel name from data source
    source : str
        Data source ('ga', 'facebook', 'domains')
    utm_campaign : str
        UTM campaign for context
    url : str
        URL for domain extraction

    Returns
    -------
    str
        Normalized channel name
    """
    taxonomy = ChannelTaxonomy()
    return taxonomy.normalize(raw_channel, source, utm_campaign, url)


if __name__ == "__main__":
    # Demo
    print("Channel Taxonomy Demo")
    print("=" * 50)
    print()

    test_cases = [
        ('cpc', 'ga'),
        ('organic', 'ga'),
        ('facebook.com', 'domains'),
        ('(direct)', 'ga'),
        ('newsletter', 'ga'),
        ('instagram ads', 'facebook'),
        ('google', 'domains'),
        ('reddit.com', 'domains'),
    ]

    taxonomy = ChannelTaxonomy()

    for raw, source in test_cases:
        normalized = taxonomy.normalize(raw, source)
        hierarchy = taxonomy.get_hierarchy(normalized)
        print(f"{raw:20} ({source}) -> {normalized:15} [{hierarchy[0]}]")

    print()
    print("All Level 2 Channels:")
    print(taxonomy.list_channels(level=2))
