#!/usr/bin/env python3
"""
CPM/RPM Estimation Utilities

Heuristic (no OAuth) CPM/RPM estimates based on:
- Niche/country baselines
- Engagement-adjusted scaling
- Region/language multipliers
- Seasonality multipliers

Public YouTube Data API does not expose actual CPM/RPM; these are estimates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from math import sqrt


# -------------------------- Baselines --------------------------

# Baseline CPM (USD) ranges by niche for US market.
# Numbers are indicative only and should be refined over time.
NICHE_BASELINES_USD: Dict[str, Tuple[float, float]] = {
    "tech": (8.0, 20.0),
    "finance": (12.0, 35.0),
    "business": (10.0, 25.0),
    "education": (6.0, 18.0),
    "health": (7.0, 20.0),
    "fitness": (6.0, 15.0),
    "beauty": (5.0, 14.0),
    "gaming": (3.0, 9.0),
    "travel": (4.0, 12.0),
    "lifestyle": (4.0, 12.0),
    "sports": (4.0, 12.0),
    "default": (5.0, 12.0),
}

# Country multipliers relative to US — coarse defaults.
COUNTRY_MULTIPLIER: Dict[str, float] = {
    "US": 1.00, "CA": 0.95, "GB": 0.95, "UK": 0.95, "AU": 0.90,
    "DE": 0.90, "FR": 0.85, "NL": 0.90, "SE": 0.90, "NO": 0.95,
    "DK": 0.90, "FI": 0.85, "CH": 1.00, "JP": 0.90, "SG": 0.95,
    "IN": 0.35, "BR": 0.45, "MX": 0.50, "PH": 0.35, "ID": 0.35,
    "ES": 0.75, "IT": 0.75, "PL": 0.65, "TR": 0.45, "AE": 0.95,
}

# Language multipliers (very rough). Applied if country missing.
LANG_MULTIPLIER: Dict[str, float] = {"en": 1.0, "de": 0.9, "fr": 0.85, "es": 0.8, "pt": 0.75, "hi": 0.4}

# Seasonality multiplier by month (1..12). Q4 uplift.
SEASONALITY: Dict[int, float] = {1: 0.85, 2: 0.9, 3: 0.95, 4: 1.0, 5: 1.0, 6: 0.95, 7: 0.95, 8: 1.0, 9: 1.05, 10: 1.15, 11: 1.25, 12: 1.3}


# -------------------------- Data Model --------------------------

@dataclass
class ChannelSignals:
    niche: str
    country: Optional[str] = None
    language: Optional[str] = None  # ISO-639-1 if known
    avg_recent_views: Optional[float] = None  # per video
    engagement_rate: Optional[float] = None  # (likes+comments)/views over recent vids (0..1)
    subscribers: Optional[int] = None
    videos_sampled: Optional[int] = None  # number of recent vids used to compute metrics
    month: Optional[int] = None  # 1..12 for seasonality


# -------------------------- Helpers --------------------------

def pick_baseline_usd(niche: str) -> Tuple[float, float]:
    key = (niche or "").strip().lower()
    for k in NICHE_BASELINES_USD:
        if k != "default" and k in key:
            return NICHE_BASELINES_USD[k]
    return NICHE_BASELINES_USD["default"]


def region_multiplier(country: Optional[str], language: Optional[str]) -> float:
    if country:
        c = country.upper()
        if c in COUNTRY_MULTIPLIER:
            return COUNTRY_MULTIPLIER[c]
    if language:
        l = language.lower()
        if l in LANG_MULTIPLIER:
            return LANG_MULTIPLIER[l]
    return 0.8  # conservative default if region unknown


def seasonality_multiplier(month: Optional[int]) -> float:
    if month and 1 <= month <= 12:
        return SEASONALITY.get(month, 1.0)
    return 1.0


def engagement_scaler(engagement_rate: Optional[float]) -> float:
    """Map ER to a multiplier. 3% ~ 1.0; every +1% adds ~0.12x; floor at 0.7, cap at 1.5."""
    if engagement_rate is None:
        return 1.0
    er = max(0.0, min(0.2, engagement_rate))  # clamp at 20%
    # Base around 3%
    base = 0.03
    delta = er - base
    mult = 1.0 + (delta / 0.01) * 0.12
    return max(0.7, min(1.5, mult))


def scale_by_recency(avg_recent_views: Optional[float], subscribers: Optional[int]) -> float:
    """If recent views punch above subs, scale up; below, scale down slightly.
    Use sqrt to reduce variance. Bound within [0.7, 1.3].
    """
    if not avg_recent_views or not subscribers or subscribers <= 0:
        return 1.0
    ratio = (avg_recent_views / max(1.0, subscribers))  # views per sub per recent vid
    # views per sub near 0.05..0.2 typical; map through sqrt curve
    mult = sqrt(max(0.05, min(0.4, ratio)) / 0.1)
    return max(0.7, min(1.3, mult))


# -------------------------- Public API --------------------------

def estimate_cpm_range(signals: ChannelSignals) -> Tuple[float, float]:
    """Return estimated CPM min/max in USD for the channel's audience."""
    base_min, base_max = pick_baseline_usd(signals.niche)
    r_mult = region_multiplier(signals.country, signals.language)
    s_mult = seasonality_multiplier(signals.month)
    e_mult = engagement_scaler(signals.engagement_rate)
    p_mult = scale_by_recency(signals.avg_recent_views, signals.subscribers)

    min_cpm = base_min * r_mult * s_mult * e_mult * p_mult
    max_cpm = base_max * r_mult * s_mult * e_mult * p_mult
    # tidy rounding
    return round(min_cpm, 2), round(max_cpm, 2)


def estimate_rpm_range(signals: ChannelSignals) -> Tuple[float, float]:
    """RPM is typically lower than CPM due to fill rates/other revenue sources.
    Heuristic: RPM ~ 0.5..0.7 of CPM range.
    """
    cmin, cmax = estimate_cpm_range(signals)
    return round(cmin * 0.55, 2), round(cmax * 0.65, 2)


def estimate_for_channel(
    niche: str,
    country: Optional[str],
    language: Optional[str],
    avg_recent_views: Optional[float],
    engagement_rate: Optional[float],
    subscribers: Optional[int],
    month: Optional[int] = None,
) -> Dict[str, Tuple[float, float]]:
    """Convenience wrapper: returns both CPM and RPM ranges."""
    sig = ChannelSignals(
        niche=niche,
        country=country,
        language=language,
        avg_recent_views=avg_recent_views,
        engagement_rate=engagement_rate,
        subscribers=subscribers,
        month=month,
    )
    return {
        "cpm_usd": estimate_cpm_range(sig),
        "rpm_usd": estimate_rpm_range(sig),
    }


if __name__ == "__main__":
    # quick manual test
    test = estimate_for_channel(
        niche="fitness",
        country="US",
        language="en",
        avg_recent_views=25000,
        engagement_rate=0.045,
        subscribers=120000,
        month=11,
    )
    print(test)


def calculate_suggested_pricing(cpm_min: float, cpm_max: float, rpm_min: float, rpm_max: float, 
                               avg_recent_views: int, subscribers: int, engagement_rate: float = None) -> tuple[float, float]:
    """
    Calculate suggested pricing range for influencer partnerships based on CPM, RPM, and engagement metrics.
    
    Args:
        cpm_min: Minimum CPM in USD
        cpm_max: Maximum CPM in USD
        rpm_min: Minimum RPM in USD
        rpm_max: Maximum RPM in USD
        avg_recent_views: Average views per video
        subscribers: Total subscriber count
        engagement_rate: Engagement rate (likes+comments/views) if available
        
    Returns:
        tuple: (suggested_pricing_min_usd, suggested_pricing_max_usd)
    """
    if not avg_recent_views or avg_recent_views <= 0:
        return 0.0, 0.0
    
    # Base pricing calculation using CPM as primary factor
    # Typical influencer pricing is 1-3x CPM for 1000 views
    base_pricing_per_1k_views = (cpm_min + cpm_max) / 2.0
    
    # Calculate base pricing for average views
    base_pricing = (avg_recent_views / 1000.0) * base_pricing_per_1k_views
    
    # Apply multipliers based on various factors
    
    # 1. Subscriber count multiplier (more subscribers = higher pricing)
    if subscribers:
        if subscribers >= 1000000:  # 1M+ subscribers
            sub_multiplier = 1.5
        elif subscribers >= 500000:  # 500K+ subscribers
            sub_multiplier = 1.3
        elif subscribers >= 100000:  # 100K+ subscribers
            sub_multiplier = 1.1
        elif subscribers >= 10000:  # 10K+ subscribers
            sub_multiplier = 1.0
        else:  # < 10K subscribers
            sub_multiplier = 0.8
    else:
        sub_multiplier = 1.0
    
    # 2. Engagement rate multiplier (higher engagement = higher pricing)
    if engagement_rate and engagement_rate > 0:
        if engagement_rate >= 0.1:  # 10%+ engagement
            engagement_multiplier = 1.4
        elif engagement_rate >= 0.05:  # 5%+ engagement
            engagement_multiplier = 1.2
        elif engagement_rate >= 0.02:  # 2%+ engagement
            engagement_multiplier = 1.0
        else:  # < 2% engagement
            engagement_multiplier = 0.8
    else:
        engagement_multiplier = 1.0
    
    # 3. RPM-based quality multiplier (higher RPM = premium audience)
    avg_rpm = (rpm_min + rpm_max) / 2.0
    if avg_rpm >= 5.0:  # High RPM = premium audience
        quality_multiplier = 1.3
    elif avg_rpm >= 2.0:  # Medium RPM
        quality_multiplier = 1.1
    else:  # Lower RPM
        quality_multiplier = 0.9
    
    # Apply all multipliers
    adjusted_pricing = base_pricing * sub_multiplier * engagement_multiplier * quality_multiplier
    
    # Create pricing range (min = 80% of adjusted, max = 120% of adjusted)
    pricing_min = adjusted_pricing * 0.8
    pricing_max = adjusted_pricing * 1.2
    
    # Ensure minimum pricing of $50 for any partnership
    pricing_min = max(pricing_min, 50.0)
    pricing_max = max(pricing_max, pricing_min * 1.2)
    
    return round(pricing_min, 2), round(pricing_max, 2)


def calculate_expected_profit(product_profit: float, cpm_min: float, cpm_max: float, 
                            rpm_min: float, rpm_max: float, avg_recent_views: int, 
                            subscribers: int, engagement_rate: float = None, 
                            suggested_pricing_min: float = None, suggested_pricing_max: float = None) -> tuple[float, float]:
    """
    Calculate expected profit for a product based on influencer metrics and suggested pricing.
    
    Args:
        product_profit: Profit per unit sold (in USD)
        cpm_min: Minimum CPM in USD
        cpm_max: Maximum CPM in USD
        rpm_min: Minimum RPM in USD
        rpm_max: Maximum RPM in USD
        avg_recent_views: Average views per video
        subscribers: Total subscriber count
        engagement_rate: Engagement rate (likes+comments/views) if available
        suggested_pricing_min: Minimum suggested pricing for partnership
        suggested_pricing_max: Maximum suggested pricing for partnership
        
    Returns:
        tuple: (expected_profit_min_usd, expected_profit_max_usd)
    """
    if not product_profit or product_profit <= 0:
        return 0.0, 0.0
    
    if not avg_recent_views or avg_recent_views <= 0:
        return 0.0, 0.0
    
    # Calculate conversion rate based on engagement and audience quality
    base_conversion_rate = 0.001  # 0.1% base conversion rate
    
    # Engagement multiplier for conversion rate
    if engagement_rate and engagement_rate > 0:
        if engagement_rate >= 0.1:  # 10%+ engagement
            engagement_multiplier = 3.0
        elif engagement_rate >= 0.05:  # 5%+ engagement
            engagement_multiplier = 2.0
        elif engagement_rate >= 0.02:  # 2%+ engagement
            engagement_multiplier = 1.5
        else:  # < 2% engagement
            engagement_multiplier = 1.0
    else:
        engagement_multiplier = 1.0
    
    # RPM-based quality multiplier (higher RPM = better audience quality)
    avg_rpm = (rpm_min + rpm_max) / 2.0
    if avg_rpm >= 5.0:  # High RPM = premium audience
        quality_multiplier = 2.0
    elif avg_rpm >= 2.0:  # Medium RPM
        quality_multiplier = 1.5
    else:  # Lower RPM
        quality_multiplier = 1.0
    
    # Subscriber count multiplier (more subscribers = better reach)
    if subscribers:
        if subscribers >= 1000000:  # 1M+ subscribers
            reach_multiplier = 1.5
        elif subscribers >= 500000:  # 500K+ subscribers
            reach_multiplier = 1.3
        elif subscribers >= 100000:  # 100K+ subscribers
            reach_multiplier = 1.1
        elif subscribers >= 10000:  # 10K+ subscribers
            reach_multiplier = 1.0
        else:  # < 10K subscribers
            reach_multiplier = 0.8
    else:
        reach_multiplier = 1.0
    
    # Calculate adjusted conversion rate
    adjusted_conversion_rate = base_conversion_rate * engagement_multiplier * quality_multiplier * reach_multiplier
    
    # Cap conversion rate at 5% (realistic maximum)
    adjusted_conversion_rate = min(adjusted_conversion_rate, 0.05)
    
    # Calculate expected units sold
    expected_units_min = int(avg_recent_views * adjusted_conversion_rate * 0.8)  # Conservative estimate
    expected_units_max = int(avg_recent_views * adjusted_conversion_rate * 1.2)  # Optimistic estimate
    
    # Calculate expected revenue from sales
    expected_revenue_min = expected_units_min * product_profit
    expected_revenue_max = expected_units_max * product_profit
    
    # Subtract partnership cost if pricing is available
    if suggested_pricing_min and suggested_pricing_max:
        expected_profit_min = expected_revenue_min - suggested_pricing_max  # Use max pricing for min profit
        expected_profit_max = expected_revenue_max - suggested_pricing_min  # Use min pricing for max profit
    else:
        # If no pricing available, just show revenue potential
        expected_profit_min = expected_revenue_min
        expected_profit_max = expected_revenue_max
    
    # Ensure non-negative profits (at worst, break even)
    expected_profit_min = max(expected_profit_min, 0.0)
    expected_profit_max = max(expected_profit_max, expected_profit_min)
    
    return round(expected_profit_min, 2), round(expected_profit_max, 2)


