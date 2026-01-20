"""
A/B Test Analysis for Causal Attribution

The GOLD STANDARD for causal inference - randomized experiments.

When you run an A/B test (e.g., show ads to treatment group, no ads to control),
you get TRUE CAUSAL EFFECTS because randomization eliminates confounding.

Usage:
    analyzer = ABTestAnalyzer(
        treatment_conversions=150, treatment_total=1000,
        control_conversions=120, control_total=1000
    )
    result = analyzer.analyze()
    print(f"Lift: {result.lift:.1%}, p-value: {result.p_value:.4f}")
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ABTestResult:
    """Results from A/B test analysis."""
    # Core metrics
    treatment_rate: float
    control_rate: float
    lift: float  # (treatment - control) / control
    absolute_difference: float

    # Statistical significance
    p_value: float
    confidence_interval: Tuple[float, float]
    is_significant: bool
    confidence_level: float

    # Sample sizes
    treatment_n: int
    control_n: int

    # Power analysis
    achieved_power: float
    minimum_detectable_effect: float

    def __repr__(self):
        sig_str = "SIGNIFICANT" if self.is_significant else "NOT significant"
        return f"""ABTestResult(
    Treatment Rate: {self.treatment_rate:.2%}
    Control Rate:   {self.control_rate:.2%}
    Lift:           {self.lift:+.1%} ({sig_str} at {self.confidence_level:.0%})
    P-value:        {self.p_value:.4f}
    95% CI:         [{self.confidence_interval[0]:+.2%}, {self.confidence_interval[1]:+.2%}]
    Power:          {self.achieved_power:.1%}
)"""


class ABTestAnalyzer:
    """
    Analyze A/B test results for causal attribution.

    This is the gold standard for determining TRUE CAUSAL EFFECTS
    because randomization eliminates confounding.

    Parameters
    ----------
    treatment_conversions : int
        Number of conversions in treatment group
    treatment_total : int
        Total users in treatment group
    control_conversions : int
        Number of conversions in control group
    control_total : int
        Total users in control group
    confidence_level : float
        Desired confidence level (default: 0.95)

    Example
    -------
    >>> # Test: Does showing Search ads increase conversions?
    >>> analyzer = ABTestAnalyzer(
    ...     treatment_conversions=150,  # With Search ads
    ...     treatment_total=1000,
    ...     control_conversions=120,    # Without Search ads
    ...     control_total=1000
    ... )
    >>> result = analyzer.analyze()
    >>> if result.is_significant:
    ...     print(f"Search ads CAUSE {result.lift:.1%} lift in conversions")
    """

    def __init__(
        self,
        treatment_conversions: int,
        treatment_total: int,
        control_conversions: int,
        control_total: int,
        confidence_level: float = 0.95
    ):
        self.t_conv = treatment_conversions
        self.t_total = treatment_total
        self.c_conv = control_conversions
        self.c_total = control_total
        self.confidence_level = confidence_level

    def analyze(self) -> ABTestResult:
        """Run full A/B test analysis."""
        # Conversion rates
        t_rate = self.t_conv / self.t_total
        c_rate = self.c_conv / self.c_total

        # Lift
        lift = (t_rate - c_rate) / c_rate if c_rate > 0 else float('inf')
        abs_diff = t_rate - c_rate

        # Statistical significance (two-proportion z-test)
        p_value, ci = self._two_proportion_z_test(t_rate, c_rate)

        # Significance determination
        alpha = 1 - self.confidence_level
        is_significant = p_value < alpha

        # Power analysis
        power = self._calculate_power(t_rate, c_rate)
        mde = self._minimum_detectable_effect()

        return ABTestResult(
            treatment_rate=t_rate,
            control_rate=c_rate,
            lift=lift,
            absolute_difference=abs_diff,
            p_value=p_value,
            confidence_interval=ci,
            is_significant=is_significant,
            confidence_level=self.confidence_level,
            treatment_n=self.t_total,
            control_n=self.c_total,
            achieved_power=power,
            minimum_detectable_effect=mde
        )

    def _two_proportion_z_test(
        self,
        p1: float,
        p2: float
    ) -> Tuple[float, Tuple[float, float]]:
        """Two-proportion z-test for difference in conversion rates."""
        n1, n2 = self.t_total, self.c_total

        # Pooled proportion
        p_pool = (self.t_conv + self.c_conv) / (n1 + n2)

        # Standard error
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))

        if se == 0:
            return 1.0, (0.0, 0.0)

        # Z statistic
        z = (p1 - p2) / se

        # Two-tailed p-value
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))

        # Confidence interval for the difference
        z_crit = stats.norm.ppf(1 - (1 - self.confidence_level) / 2)
        se_diff = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        ci_lower = (p1 - p2) - z_crit * se_diff
        ci_upper = (p1 - p2) + z_crit * se_diff

        return p_value, (ci_lower, ci_upper)

    def _calculate_power(self, p1: float, p2: float) -> float:
        """Calculate achieved statistical power."""
        n1, n2 = self.t_total, self.c_total
        alpha = 1 - self.confidence_level

        # Effect size (Cohen's h)
        h = 2 * (np.arcsin(np.sqrt(p1)) - np.arcsin(np.sqrt(p2)))

        # Non-centrality parameter
        n_harmonic = 2 * n1 * n2 / (n1 + n2)
        ncp = abs(h) * np.sqrt(n_harmonic / 2)

        # Critical value
        z_crit = stats.norm.ppf(1 - alpha / 2)

        # Power
        power = 1 - stats.norm.cdf(z_crit - ncp) + stats.norm.cdf(-z_crit - ncp)

        return power

    def _minimum_detectable_effect(self) -> float:
        """Calculate minimum detectable effect at 80% power."""
        n1, n2 = self.t_total, self.c_total
        alpha = 1 - self.confidence_level
        power = 0.80

        # Z values
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)

        # Pooled rate estimate
        p_pool = (self.t_conv + self.c_conv) / (n1 + n2)

        # MDE formula
        n_harmonic = 2 * n1 * n2 / (n1 + n2)
        se = np.sqrt(2 * p_pool * (1 - p_pool) / n_harmonic)
        mde = (z_alpha + z_beta) * se

        return mde


def calculate_lift(
    treatment_rate: float,
    control_rate: float
) -> float:
    """
    Calculate relative lift.

    Lift = (Treatment - Control) / Control

    Parameters
    ----------
    treatment_rate : float
        Conversion rate in treatment group
    control_rate : float
        Conversion rate in control group

    Returns
    -------
    float
        Relative lift (e.g., 0.25 = 25% lift)
    """
    if control_rate == 0:
        return float('inf') if treatment_rate > 0 else 0.0
    return (treatment_rate - control_rate) / control_rate


def calculate_statistical_significance(
    t_conversions: int,
    t_total: int,
    c_conversions: int,
    c_total: int,
    alpha: float = 0.05
) -> Dict[str, float]:
    """
    Quick check for statistical significance.

    Returns
    -------
    dict
        Contains 'p_value', 'is_significant', 'z_score'
    """
    p1 = t_conversions / t_total
    p2 = c_conversions / c_total

    # Pooled proportion
    p_pool = (t_conversions + c_conversions) / (t_total + c_total)

    # Standard error
    se = np.sqrt(p_pool * (1 - p_pool) * (1/t_total + 1/c_total))

    if se == 0:
        return {'p_value': 1.0, 'is_significant': False, 'z_score': 0.0}

    z = (p1 - p2) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    return {
        'p_value': p_value,
        'is_significant': p_value < alpha,
        'z_score': z
    }


def run_ab_test_analysis(
    treatment_data: List[Dict],
    control_data: List[Dict],
    conversion_field: str = 'converted',
    confidence_level: float = 0.95
) -> ABTestResult:
    """
    Run A/B test analysis on raw user data.

    Parameters
    ----------
    treatment_data : list
        List of user records in treatment group
    control_data : list
        List of user records in control group
    conversion_field : str
        Field name indicating conversion (True/False or 1/0)
    confidence_level : float
        Desired confidence level

    Returns
    -------
    ABTestResult
    """
    t_conv = sum(1 for u in treatment_data if u.get(conversion_field))
    t_total = len(treatment_data)
    c_conv = sum(1 for u in control_data if u.get(conversion_field))
    c_total = len(control_data)

    analyzer = ABTestAnalyzer(
        treatment_conversions=t_conv,
        treatment_total=t_total,
        control_conversions=c_conv,
        control_total=c_total,
        confidence_level=confidence_level
    )

    return analyzer.analyze()


class MultiChannelABTestSuite:
    """
    Run A/B tests for multiple channels to get causal attribution.

    For each channel, you need an experiment where:
    - Treatment: Users exposed to that channel
    - Control: Users NOT exposed to that channel (holdout)

    This gives you TRUE CAUSAL EFFECTS per channel.
    """

    def __init__(self):
        self.results = {}

    def add_channel_test(
        self,
        channel: str,
        treatment_conversions: int,
        treatment_total: int,
        control_conversions: int,
        control_total: int
    ):
        """Add A/B test results for a channel."""
        analyzer = ABTestAnalyzer(
            treatment_conversions=treatment_conversions,
            treatment_total=treatment_total,
            control_conversions=control_conversions,
            control_total=control_total
        )
        self.results[channel] = analyzer.analyze()

    def get_causal_attribution(self) -> Dict[str, Dict]:
        """
        Get causal attribution based on A/B test results.

        Returns dict with causal lift per channel.
        """
        attribution = {}
        total_lift = 0

        for channel, result in self.results.items():
            if result.is_significant and result.lift > 0:
                attribution[channel] = {
                    'causal_lift': result.lift,
                    'absolute_effect': result.absolute_difference,
                    'p_value': result.p_value,
                    'confidence': 'high' if result.p_value < 0.01 else 'medium'
                }
                total_lift += result.absolute_difference

        # Normalize to shares
        if total_lift > 0:
            for channel in attribution:
                attribution[channel]['share'] = (
                    attribution[channel]['absolute_effect'] / total_lift
                )

        return attribution

    def generate_report(self) -> str:
        """Generate human-readable report."""
        lines = [
            "=" * 60,
            "CAUSAL ATTRIBUTION FROM A/B TESTS",
            "=" * 60,
            "",
            "These are TRUE CAUSAL EFFECTS from randomized experiments.",
            "",
        ]

        for channel, result in sorted(
            self.results.items(),
            key=lambda x: x[1].lift,
            reverse=True
        ):
            sig = "***" if result.p_value < 0.001 else (
                "**" if result.p_value < 0.01 else (
                    "*" if result.p_value < 0.05 else ""
                )
            )
            lines.append(
                f"{channel:15} Lift: {result.lift:+6.1%} "
                f"(p={result.p_value:.4f}) {sig}"
            )

        lines.append("")
        lines.append("Significance: *** p<0.001, ** p<0.01, * p<0.05")
        lines.append("")

        attribution = self.get_causal_attribution()
        if attribution:
            lines.append("CAUSAL SHARE OF CONVERSION LIFT:")
            lines.append("-" * 40)
            for channel, data in sorted(
                attribution.items(),
                key=lambda x: x[1]['share'],
                reverse=True
            ):
                lines.append(f"  {channel:15} {data['share']:.1%}")

        return "\n".join(lines)


if __name__ == "__main__":
    # Demo: A/B test analysis
    print("=" * 60)
    print("A/B TEST ANALYSIS DEMO")
    print("=" * 60)
    print()

    # Single channel test
    print("Single Channel Test: Search Ads")
    print("-" * 40)
    analyzer = ABTestAnalyzer(
        treatment_conversions=150,
        treatment_total=1000,
        control_conversions=120,
        control_total=1000
    )
    result = analyzer.analyze()
    print(result)
    print()

    # Multi-channel suite
    print("Multi-Channel Causal Attribution")
    print("-" * 40)
    suite = MultiChannelABTestSuite()

    # Add test results for each channel
    suite.add_channel_test('Search', 150, 1000, 120, 1000)
    suite.add_channel_test('Email', 130, 1000, 120, 1000)
    suite.add_channel_test('Social', 125, 1000, 120, 1000)
    suite.add_channel_test('Display', 118, 1000, 120, 1000)  # Not significant

    print(suite.generate_report())
