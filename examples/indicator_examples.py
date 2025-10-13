#!/usr/bin/env python3
"""
Examples of how to use different trend indicators and combinations

This file demonstrates various ways to configure the backtesting system
with different trend indicators and indicator combinations.
"""

import sys
sys.path.append('..')

from taiwan_futures_backtest import TaiwanFuturesBacktest
from indicators import (
    PriceDifferenceIndicator,
    MovingAverageIndicator,
    MomentumIndicator,
    IndicatorCombiner,
    CombinationMode
)


def example_1_original_indicator():
    """
    Example 1: Using the original price difference indicator (default)
    This is equivalent to the original system behavior
    """
    print("="*80)
    print("Example 1: Original Price Difference Indicator")
    print("="*80)

    # Method 1: Don't specify indicator (uses default)
    backtester = TaiwanFuturesBacktest(
        start_date='2017-05-16',
        end_date='2024-12-31',
        counting_period='weekly'
    )

    # Method 2: Explicitly specify the indicator
    indicator = PriceDifferenceIndicator(
        opening_price_calc='standard',
        prev_close_calc='standard'
    )

    backtester = TaiwanFuturesBacktest(
        start_date='2017-05-16',
        end_date='2024-12-31',
        counting_period='weekly',
        trend_indicator=indicator
    )

    # Run backtest
    backtester.get_taiwan_futures_data()
    backtester.calculate_settlement_dates()
    backtester.run_backtest()
    backtester.generate_report()

    return backtester


def example_2_moving_average():
    """
    Example 2: Using moving average as trend indicator
    """
    print("="*80)
    print("Example 2: Moving Average Indicator (5-period)")
    print("="*80)

    # Create a 5-period moving average indicator
    indicator = MovingAverageIndicator(
        name="MA5",
        period=5,
        price_type='close'
    )

    backtester = TaiwanFuturesBacktest(
        start_date='2017-05-16',
        end_date='2024-12-31',
        counting_period='weekly',
        trend_indicator=indicator
    )

    # Run backtest
    backtester.get_taiwan_futures_data()
    backtester.calculate_settlement_dates()
    backtester.run_backtest()
    backtester.generate_report()

    return backtester


def example_3_momentum():
    """
    Example 3: Using momentum as trend indicator
    """
    print("="*80)
    print("Example 3: Momentum Indicator (5-period)")
    print("="*80)

    # Create a momentum indicator
    indicator = MomentumIndicator(
        name="Momentum5",
        period=5,
        price_type='close'
    )

    backtester = TaiwanFuturesBacktest(
        start_date='2017-05-16',
        end_date='2024-12-31',
        counting_period='weekly',
        trend_indicator=indicator
    )

    # Run backtest
    backtester.get_taiwan_futures_data()
    backtester.calculate_settlement_dates()
    backtester.run_backtest()
    backtester.generate_report()

    return backtester


def example_4_combined_all_agree():
    """
    Example 4: Combine multiple indicators with ALL_AGREE mode
    All indicators must agree for a trade signal
    """
    print("="*80)
    print("Example 4: Combined Indicators (ALL_AGREE mode)")
    print("="*80)

    # Create individual indicators
    price_diff = PriceDifferenceIndicator()
    ma5 = MovingAverageIndicator(name="MA5", period=5)
    momentum5 = MomentumIndicator(name="Momentum5", period=5)

    # Combine with ALL_AGREE mode (all must agree)
    # Weights are ignored in ALL_AGREE mode
    combined_indicator = IndicatorCombiner(
        indicators=[
            (price_diff, 1.0),
            (ma5, 1.0),
            (momentum5, 1.0)
        ],
        mode=CombinationMode.ALL_AGREE,
        name="AllAgree_3Indicators"
    )

    backtester = TaiwanFuturesBacktest(
        start_date='2017-05-16',
        end_date='2024-12-31',
        counting_period='weekly',
        trend_indicator=combined_indicator
    )

    # Run backtest
    backtester.get_taiwan_futures_data()
    backtester.calculate_settlement_dates()
    backtester.run_backtest()
    backtester.generate_report()

    return backtester


def example_5_combined_majority():
    """
    Example 5: Combine multiple indicators with MAJORITY mode
    Majority of indicators determine the signal
    """
    print("="*80)
    print("Example 5: Combined Indicators (MAJORITY mode)")
    print("="*80)

    # Create individual indicators
    price_diff = PriceDifferenceIndicator()
    ma3 = MovingAverageIndicator(name="MA3", period=3)
    ma5 = MovingAverageIndicator(name="MA5", period=5)
    ma10 = MovingAverageIndicator(name="MA10", period=10)
    momentum = MomentumIndicator(name="Momentum5", period=5)

    # Combine with MAJORITY mode
    combined_indicator = IndicatorCombiner(
        indicators=[
            (price_diff, 1.0),
            (ma3, 1.0),
            (ma5, 1.0),
            (ma10, 1.0),
            (momentum, 1.0)
        ],
        mode=CombinationMode.MAJORITY,
        name="Majority_5Indicators"
    )

    backtester = TaiwanFuturesBacktest(
        start_date='2017-05-16',
        end_date='2024-12-31',
        counting_period='weekly',
        trend_indicator=combined_indicator
    )

    # Run backtest
    backtester.get_taiwan_futures_data()
    backtester.calculate_settlement_dates()
    backtester.run_backtest()
    backtester.generate_report()

    return backtester


def example_6_combined_weighted():
    """
    Example 6: Combine multiple indicators with WEIGHTED mode
    Indicators are weighted by importance
    """
    print("="*80)
    print("Example 6: Combined Indicators (WEIGHTED mode)")
    print("="*80)

    # Create individual indicators
    price_diff = PriceDifferenceIndicator()
    ma5 = MovingAverageIndicator(name="MA5", period=5)
    momentum = MomentumIndicator(name="Momentum5", period=5)

    # Combine with WEIGHTED mode
    # Weights represent the importance of each indicator
    combined_indicator = IndicatorCombiner(
        indicators=[
            (price_diff, 0.5),    # 50% weight
            (ma5, 0.3),           # 30% weight
            (momentum, 0.2)       # 20% weight
        ],
        mode=CombinationMode.WEIGHTED,
        name="Weighted_3Indicators"
    )

    backtester = TaiwanFuturesBacktest(
        start_date='2017-05-16',
        end_date='2024-12-31',
        counting_period='weekly',
        trend_indicator=combined_indicator
    )

    # Run backtest
    backtester.get_taiwan_futures_data()
    backtester.calculate_settlement_dates()
    backtester.run_backtest()
    backtester.generate_report()

    return backtester


def example_7_custom_weights():
    """
    Example 7: Multiple MAs with custom weights
    """
    print("="*80)
    print("Example 7: Multiple Moving Averages with Custom Weights")
    print("="*80)

    # Create multiple moving average indicators with different periods
    ma3 = MovingAverageIndicator(name="MA3", period=3)
    ma5 = MovingAverageIndicator(name="MA5", period=5)
    ma10 = MovingAverageIndicator(name="MA10", period=10)
    ma20 = MovingAverageIndicator(name="MA20", period=20)

    # Combine with weighted mode - shorter periods get more weight
    combined_indicator = IndicatorCombiner(
        indicators=[
            (ma3, 0.4),    # 40% weight - most recent trend
            (ma5, 0.3),    # 30% weight
            (ma10, 0.2),   # 20% weight
            (ma20, 0.1)    # 10% weight - longer term trend
        ],
        mode=CombinationMode.WEIGHTED,
        name="MultiMA_Weighted"
    )

    backtester = TaiwanFuturesBacktest(
        start_date='2017-05-16',
        end_date='2024-12-31',
        counting_period='weekly',
        trend_indicator=combined_indicator
    )

    # Run backtest
    backtester.get_taiwan_futures_data()
    backtester.calculate_settlement_dates()
    backtester.run_backtest()
    backtester.generate_report()

    return backtester


if __name__ == "__main__":
    """
    Run the examples
    Uncomment the example you want to test
    """

    # Example 1: Original indicator (default)
    # example_1_original_indicator()

    # Example 2: Moving average
    # example_2_moving_average()

    # Example 3: Momentum
    # example_3_momentum()

    # Example 4: Combined ALL_AGREE
    # example_4_combined_all_agree()

    # Example 5: Combined MAJORITY
    # example_5_combined_majority()

    # Example 6: Combined WEIGHTED
    example_6_combined_weighted()

    # Example 7: Multiple MAs with custom weights
    # example_7_custom_weights()
