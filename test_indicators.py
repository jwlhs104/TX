#!/usr/bin/env python3
"""
Quick test script to verify the indicator system works correctly
"""

from taiwan_futures_backtest import TaiwanFuturesBacktest
from indicators import (
    PriceDifferenceIndicator,
    MovingAverageIndicator,
    MomentumIndicator,
    IndicatorCombiner,
    CombinationMode
)


def test_original_indicator():
    """Test that the original indicator still works (backward compatibility)"""
    print("="*80)
    print("Test 1: Original Price Difference Indicator (Default)")
    print("="*80)

    backtester = TaiwanFuturesBacktest(
        start_date='2024-01-01',
        end_date='2024-03-31',
        counting_period='weekly'
    )

    try:
        backtester.get_taiwan_futures_data()
        backtester.calculate_settlement_dates()
        results = backtester.run_backtest()

        print(f"✓ Test passed: {len(results)} trades generated")
        print(f"  Columns: {list(results.columns)}")
        print(f"  Sample result:")
        if len(results) > 0:
            sample = results.iloc[0]
            print(f"    Date: {sample['settlement_date']}")
            print(f"    Trend Indicator: {sample['trend_indicator']:.2f}")
            print(f"    Signal: {sample['trend_signal']}")
            print(f"    Direction: {sample['direction']}")
        print()
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_moving_average_indicator():
    """Test moving average indicator"""
    print("="*80)
    print("Test 2: Moving Average Indicator (5-period)")
    print("="*80)

    indicator = MovingAverageIndicator(name="MA5", period=5, price_type='close')

    backtester = TaiwanFuturesBacktest(
        start_date='2024-01-01',
        end_date='2024-03-31',
        counting_period='weekly',
        trend_indicator=indicator
    )

    try:
        backtester.get_taiwan_futures_data()
        backtester.calculate_settlement_dates()
        results = backtester.run_backtest()

        print(f"✓ Test passed: {len(results)} trades generated with MA5")
        if len(results) > 0:
            sample = results.iloc[0]
            print(f"  Sample result:")
            print(f"    Date: {sample['settlement_date']}")
            print(f"    Trend Indicator: {sample['trend_indicator']:.2f}")
            print(f"    Signal: {sample['trend_signal']}")
            print(f"    Direction: {sample['direction']}")
        print()
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_combined_indicator_weighted():
    """Test combined indicator with weighted mode"""
    print("="*80)
    print("Test 3: Combined Indicator (Weighted)")
    print("="*80)

    price_diff = PriceDifferenceIndicator()
    ma5 = MovingAverageIndicator(name="MA5", period=5)
    momentum = MomentumIndicator(name="Momentum5", period=5)

    combined = IndicatorCombiner(
        indicators=[
            (price_diff, 0.5),
            (ma5, 0.3),
            (momentum, 0.2)
        ],
        mode=CombinationMode.WEIGHTED,
        name="Weighted_Test"
    )

    backtester = TaiwanFuturesBacktest(
        start_date='2024-01-01',
        end_date='2024-03-31',
        counting_period='weekly',
        trend_indicator=combined
    )

    try:
        backtester.get_taiwan_futures_data()
        backtester.calculate_settlement_dates()
        results = backtester.run_backtest()

        print(f"✓ Test passed: {len(results)} trades generated with combined indicator")
        if len(results) > 0:
            sample = results.iloc[0]
            print(f"  Sample result:")
            print(f"    Date: {sample['settlement_date']}")
            print(f"    Trend Indicator: {sample['trend_indicator']:.2f}")
            print(f"    Signal: {sample['trend_signal']}")
            print(f"    Strength: {sample['trend_strength']:.2f}")
            print(f"    Direction: {sample['direction']}")
        print()
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_combined_indicator_all_agree():
    """Test combined indicator with ALL_AGREE mode"""
    print("="*80)
    print("Test 4: Combined Indicator (ALL_AGREE)")
    print("="*80)

    price_diff = PriceDifferenceIndicator()
    ma5 = MovingAverageIndicator(name="MA5", period=5)

    combined = IndicatorCombiner(
        indicators=[
            (price_diff, 1.0),
            (ma5, 1.0)
        ],
        mode=CombinationMode.ALL_AGREE,
        name="AllAgree_Test"
    )

    backtester = TaiwanFuturesBacktest(
        start_date='2024-01-01',
        end_date='2024-03-31',
        counting_period='weekly',
        trend_indicator=combined
    )

    try:
        backtester.get_taiwan_futures_data()
        backtester.calculate_settlement_dates()
        results = backtester.run_backtest()

        print(f"✓ Test passed: {len(results)} trades generated")
        # Count trades by direction
        long_trades = len(results[results['direction'] == 'long'])
        short_trades = len(results[results['direction'] == 'short'])
        no_trades = len(results[results['direction'] == 'no_trade'])
        print(f"  Long: {long_trades}, Short: {short_trades}, No Trade: {no_trades}")
        print(f"  (No trade count may be higher in ALL_AGREE mode)")
        print()
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("INDICATOR SYSTEM TEST SUITE")
    print("="*80 + "\n")

    tests = [
        test_original_indicator,
        test_moving_average_indicator,
        test_combined_indicator_weighted,
        test_combined_indicator_all_agree
    ]

    results = []
    for test in tests:
        passed = test()
        results.append(passed)

    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed_count = sum(results)
    total_count = len(results)
    print(f"Passed: {passed_count}/{total_count}")

    if passed_count == total_count:
        print("✓ All tests passed!")
    else:
        print(f"✗ {total_count - passed_count} test(s) failed")

    print("="*80)
