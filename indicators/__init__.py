"""
Trend Indicators Module

This module provides a flexible framework for defining and combining
multiple trend indicators for trade direction determination.
"""

from .base import TrendIndicator, IndicatorResult
from .price_difference import PriceDifferenceIndicator
from .moving_average import MovingAverageIndicator
from .momentum import MomentumIndicator
from .candle_color import CandleColorIndicator
from .opening_position import OpeningPositionIndicator
from .weekly_pattern import WeeklyPatternIndicator
from .combiner import IndicatorCombiner, CombinationMode

__all__ = [
    'TrendIndicator',
    'IndicatorResult',
    'PriceDifferenceIndicator',
    'MovingAverageIndicator',
    'MomentumIndicator',
    'CandleColorIndicator',
    'OpeningPositionIndicator',
    'WeeklyPatternIndicator',
    'IndicatorCombiner',
    'CombinationMode',
]
