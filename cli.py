#!/usr/bin/env python3
"""
Unified Command-Line Interface for Taiwan Futures Analysis Toolkit

Usage:
    python cli.py backtest [options]     # Run TX futures backtest
    python cli.py maxpain [options]      # Run TXO max pain analysis
    python cli.py report                 # Generate comprehensive report
    python cli.py calc <file>            # Calculate max pain from CSV
"""

import argparse
import sys
from pathlib import Path


def run_backtest(args):
    """Run Taiwan Futures backtest"""
    from taiwan_futures_backtest import TaiwanFuturesBacktest
    from indicators import (
        PriceDifferenceIndicator,
        MovingAverageIndicator,
        MomentumIndicator,
        CandleColorIndicator,
        OpeningPositionIndicator,
        WeeklyPatternIndicator,
        IndicatorCombiner,
        CombinationMode
    )

    print("="*80)
    print("Taiwan Futures Settlement Day Backtest")
    print("="*80)
    print(f"Counting period: {args.counting_period}")
    print(f"Opening price calc: {args.opening_price_calc}")
    print(f"Previous close calc: {args.prev_close_calc}")
    print(f"Date range: {args.start_date} to {args.end_date}")
    if args.benchmark:
        print(f"Benchmark mode: Enabled (comparing with other weekdays)")
    print()

    # Parse indicators from CLI
    indicators_to_test = []
    if hasattr(args, 'indicators') and args.indicators:
        for ind_spec in args.indicators:
            parts = ind_spec.split(':')
            ind_type = parts[0]

            if ind_type == 'price-diff':
                ind = PriceDifferenceIndicator(
                    name="PriceDiff",
                    opening_price_calc=args.opening_price_calc,
                    prev_close_calc=args.prev_close_calc
                )
                indicators_to_test.append(('Price Difference', ind))
            elif ind_type == 'ma':
                period = int(parts[1]) if len(parts) > 1 else 5
                price_type = parts[2] if len(parts) > 2 else 'close'
                ind = MovingAverageIndicator(
                    name=f"MA{period}",
                    period=period,
                    price_type=price_type
                )
                indicators_to_test.append((f'MA{period}_{price_type}', ind))
            elif ind_type == 'momentum':
                period = int(parts[1]) if len(parts) > 1 else 5
                price_type = parts[2] if len(parts) > 2 else 'close'
                ind = MomentumIndicator(
                    name=f"Momentum{period}",
                    period=period,
                    price_type=price_type
                )
                indicators_to_test.append((f'Momentum{period}_{price_type}', ind))
            elif ind_type == 'candle' or ind_type == 'candle-color':
                invert = (parts[1].lower() == 'invert') if len(parts) > 1 else False
                ind = CandleColorIndicator(
                    name="CandleColor" + ("_Inverted" if invert else ""),
                    invert=invert
                )
                indicators_to_test.append(('CandleColor' + ('_Inverted' if invert else ''), ind))
            elif ind_type == 'opening' or ind_type == 'opening-position':
                invert = (parts[1].lower() == 'invert') if len(parts) > 1 else False
                ind = OpeningPositionIndicator(
                    name="OpeningPosition" + ("_Inverted" if invert else ""),
                    invert=invert
                )
                indicators_to_test.append(('OpeningPosition' + ('_Inverted' if invert else ''), ind))
            elif ind_type == 'weekly-pattern' or ind_type == 'weekly':
                use_adaptive = (parts[1].lower() == 'adaptive') if len(parts) > 1 else False

                # Create a preliminary backtester for adaptive mode
                if use_adaptive:
                    preliminary_backtester = TaiwanFuturesBacktest(
                        start_date=args.start_date,
                        end_date=args.end_date,
                        counting_period=args.counting_period,
                        opening_price_calc=args.opening_price_calc,
                        prev_close_calc=args.prev_close_calc,
                        trend_indicator=None
                    )
                    preliminary_backtester.get_taiwan_futures_data()
                    preliminary_backtester.calculate_settlement_dates()
                else:
                    preliminary_backtester = None

                ind = WeeklyPatternIndicator(
                    name="WeeklyPattern" + ("_Adaptive" if use_adaptive else ""),
                    opening_price_calc=args.opening_price_calc,
                    prev_close_calc=args.prev_close_calc,
                    use_adaptive=use_adaptive,
                    backtester=preliminary_backtester
                )
                indicators_to_test.append(('WeeklyPattern' + ('_Adaptive' if use_adaptive else ''), ind))
            else:
                print(f"Warning: Unknown indicator type '{ind_type}', skipping")

    # If no indicators specified, use default
    if not indicators_to_test:
        indicators_to_test.append((
            'Default (Price Difference)',
            PriceDifferenceIndicator(
                opening_price_calc=args.opening_price_calc,
                prev_close_calc=args.prev_close_calc
            )
        ))

    print(f"Will run {len(indicators_to_test)} individual backtest(s)", end='')
    if len(indicators_to_test) > 1:
        print(f" + 1 combined backtest")
    else:
        print()
    print()

    # If benchmark mode is enabled, use the benchmark tester
    if args.benchmark:
        from utils.benchmark_test import FixedDayBenchmarkTest

        try:
            # Use the first indicator for benchmark testing (or None for default)
            indicator = indicators_to_test[0][1] if indicators_to_test else None
            indicator_name = indicators_to_test[0][0] if indicators_to_test else "Default"

            print(f"Running benchmark with indicator: {indicator_name}")

            # Initialize benchmark tester
            benchmark_tester = FixedDayBenchmarkTest(
                start_date=args.start_date,
                end_date=args.end_date,
                opening_price_calc=args.opening_price_calc,
                prev_close_calc=args.prev_close_calc,
                trend_indicator=indicator
            )

            print("1. Loading data...")
            benchmark_tester.load_data()

            print("2. Running settlement day backtest...")
            benchmark_tester.run_settlement_backtest()

            print("3. Running benchmark tests (comparing other weekdays)...")
            max_dates = args.benchmark_max_dates if hasattr(args, 'benchmark_max_dates') else 500
            verbose = args.benchmark_verbose if hasattr(args, 'benchmark_verbose') else False
            benchmark_tester.run_all_benchmarks(max_dates_per_weekday=max_dates, verbose=verbose)

            if not args.no_plots:
                print("4. Creating comparison plots...")
                benchmark_tester.create_comparison_plots()

            print("5. Generating benchmark report...")
            benchmark_tester.generate_benchmark_report()

            print("\n" + "="*80)
            print("✓ Benchmark test completed successfully!")
            print("="*80)

        except Exception as e:
            print(f"\n✗ Error during benchmark test: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # Regular backtest mode
        all_backtests = []

        try:
            # Run backtest for each individual indicator
            for i, (ind_name, indicator) in enumerate(indicators_to_test, 1):
                print("="*80)
                print(f"Running Backtest {i}/{len(indicators_to_test)}: {ind_name}")
                print("="*80)

                backtester = TaiwanFuturesBacktest(
                    start_date=args.start_date,
                    end_date=args.end_date,
                    counting_period=args.counting_period,
                    opening_price_calc=args.opening_price_calc,
                    prev_close_calc=args.prev_close_calc,
                    trend_indicator=indicator
                )

                print("1. Loading data...")
                backtester.get_taiwan_futures_data()

                print("2. Calculating settlement dates...")
                backtester.calculate_settlement_dates()

                print("3. Running backtest...")
                backtester.run_backtest()

                print("4. Generating report...")
                backtester.generate_report()

                if not args.no_plots:
                    print("5. Creating visualizations...")
                    backtester.create_performance_plots(indicator_name=ind_name)
                    print("5.1. Creating indicator analysis plot...")
                    backtester.create_indicator_analysis_plot(indicator_name=ind_name)

                print("6. Saving results...")
                backtester.save_detailed_results(indicator_name=ind_name)

                if not args.no_markdown:
                    print("7. Saving markdown report...")
                    backtester.save_results_summary_to_md(indicator_name=ind_name)

                all_backtests.append((ind_name, backtester))
                print()

            # If multiple indicators, run combined backtest
            if len(indicators_to_test) > 1:
                print("="*80)
                print(f"Running Combined Backtest ({len(indicators_to_test)} indicators)")
                print("="*80)

                # Create a preliminary backtester for training
                preliminary_backtester = TaiwanFuturesBacktest(
                    start_date=args.start_date,
                    end_date=args.end_date,
                    counting_period=args.counting_period,
                    opening_price_calc=args.opening_price_calc,
                    prev_close_calc=args.prev_close_calc,
                    trend_indicator=None  # Will be set later
                )
                preliminary_backtester.get_taiwan_futures_data()
                preliminary_backtester.calculate_settlement_dates()

                # Create combined indicator with ADAPTIVE_QUADRANT mode
                combined_indicators = [(ind, 1.0) for _, ind in indicators_to_test]
                combined = IndicatorCombiner(
                    indicators=combined_indicators,
                    mode=CombinationMode.ADAPTIVE_QUADRANT,
                    name="Combined_Adaptive_Quadrant",
                    backtester=preliminary_backtester
                )

                backtester = TaiwanFuturesBacktest(
                    start_date=args.start_date,
                    end_date=args.end_date,
                    counting_period=args.counting_period,
                    opening_price_calc=args.opening_price_calc,
                    prev_close_calc=args.prev_close_calc,
                    trend_indicator=combined
                )

                print("1. Loading data...")
                backtester.get_taiwan_futures_data()

                print("2. Calculating settlement dates...")
                backtester.calculate_settlement_dates()

                print("3. Running backtest...")
                backtester.run_backtest()

                print("4. Generating report...")
                backtester.generate_report()

                if not args.no_plots:
                    print("5. Creating visualizations...")
                    backtester.create_performance_plots(indicator_name='Combined_Adaptive_Quadrant')
                    print("5.1. Creating indicator analysis plot...")
                    backtester.create_indicator_analysis_plot(indicator_name='Combined_Adaptive_Quadrant')

                print("6. Saving results...")
                backtester.save_detailed_results(indicator_name='Combined_Adaptive_Quadrant')

                if not args.no_markdown:
                    print("7. Saving markdown report...")
                    backtester.save_results_summary_to_md(indicator_name='Combined_Adaptive_Quadrant')

                all_backtests.append(('Combined (Adaptive Quadrant)', backtester))
                print()

            # Print summary comparison
            if len(all_backtests) > 1:
                print("\n" + "="*80)
                print("BACKTEST COMPARISON SUMMARY")
                print("="*80)
                for ind_name, bt in all_backtests:
                    stats = bt.calculate_performance_stats()
                    print(f"\n{ind_name}:")
                    print(f"  勝率: {stats.get('勝率', 'N/A')}")
                    print(f"  筆均: {stats.get('筆均', 0):.2f}%")
                    print(f"  淨利: {stats.get('淨利', 0):.2f}%")

            print("\n" + "="*80)
            print("✓ All backtests completed successfully!")
            print("="*80)

        except Exception as e:
            print(f"\n✗ Error during backtest: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def run_maxpain(args):
    """Run TXO Max Pain analysis"""
    from txo_max_pain_backtest import TXOMaxPainBacktest

    print("="*80)
    print("TXO Max Pain Analysis")
    print("="*80)
    print(f"Date range: {args.start_date} to {args.end_date}")
    print()

    # Initialize analyzer
    analyzer = TXOMaxPainBacktest(
        start_date=args.start_date,
        end_date=args.end_date
    )

    # Run analysis
    try:
        print("1. Loading data...")
        analyzer.load_txo_data()
        analyzer.load_tx_futures_data()
        analyzer.get_settlement_dates()

        print("2. Running max pain analysis...")
        results = analyzer.run_max_pain_analysis()

        if results is not None and len(results) > 0:
            print("3. Generating report...")
            analyzer.generate_report()

            if not args.no_plots:
                print("4. Creating visualizations...")
                analyzer.create_visualizations()

            print("5. Saving results...")
            analyzer.save_results()

            print("\n" + "="*80)
            print("✓ Max pain analysis completed successfully!")
            print("="*80)
        else:
            print("✗ No valid results obtained from analysis")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error during max pain analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def generate_report(args):
    """Generate comprehensive analysis report"""
    from generate_report import generate_comprehensive_report, save_report_to_file

    print("="*80)
    print("Generating Comprehensive Analysis Report")
    print("="*80)
    print()

    try:
        report_content = generate_comprehensive_report()
        report_file = save_report_to_file(report_content)

        if report_file:
            print("\n" + "="*80)
            print("✓ Report generated successfully!")
            print("="*80)
            print(f"📝 Report: {report_file}")
        else:
            print("✗ Failed to generate report")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def calculate_maxpain(args):
    """Calculate max pain from CSV file"""
    from max_pain_calculator import calculate_max_pain

    print("="*80)
    print("Max Pain Calculator")
    print("="*80)
    print(f"File: {args.file}")
    print()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"✗ Error: File not found: {args.file}")
        sys.exit(1)

    try:
        max_pain_price = calculate_max_pain(str(file_path))

        if max_pain_price:
            print("\n" + "="*80)
            print(f"✓ Max Pain Price: {max_pain_price:,.0f}")
            print("="*80)
        else:
            print("✗ Could not calculate max pain")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error calculating max pain: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Taiwan Futures Analysis Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run backtest with default settings
  python cli.py backtest

  # Run backtest with monthly settlements only
  python cli.py backtest --counting-period monthly

  # Run backtest with night session prices
  python cli.py backtest --opening-price-calc night --prev-close-calc night

  # Run backtest with a single indicator (Moving Average, period 5)
  python cli.py backtest --indicators ma:5:close

  # Run backtest with two indicators (runs 3 backtests: MA5, MA10, Combined)
  python cli.py backtest --indicators ma:5 ma:10

  # Run with multiple different indicators
  python cli.py backtest --indicators price-diff ma:5:close momentum:10

  # Run with candle color and opening position indicators
  python cli.py backtest --indicators candle opening

  # Run with inverted candle color indicator
  python cli.py backtest --indicators candle:invert

  # Run with weekly pattern indicator (rule-based)
  python cli.py backtest --indicators weekly-pattern

  # Run with weekly pattern indicator (adaptive mode)
  python cli.py backtest --indicators weekly-pattern:adaptive

  # Run backtest with benchmark comparison (settlement vs other weekdays)
  python cli.py backtest --benchmark

  # Run benchmark with custom date limit per weekday
  python cli.py backtest --benchmark --benchmark-max-dates 1000

  # Run max pain analysis
  python cli.py maxpain

  # Generate comprehensive report
  python cli.py report

  # Calculate max pain from CSV file
  python cli.py calc data/TXO_20250923.csv
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # ========== Backtest Command ==========
    backtest_parser = subparsers.add_parser(
        'backtest',
        help='Run Taiwan Futures backtest',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    backtest_parser.add_argument(
        '--counting-period',
        choices=['weekly', 'monthly'],
        default='weekly',
        help='Settlement counting period'
    )
    backtest_parser.add_argument(
        '--opening-price-calc',
        choices=['standard', 'night'],
        default='standard',
        help='Opening price calculation method'
    )
    backtest_parser.add_argument(
        '--prev-close-calc',
        choices=['standard', 'night', 'settlement_open'],
        default='standard',
        help='Previous close calculation method'
    )
    backtest_parser.add_argument(
        '--start-date',
        default='2017-05-16',
        help='Start date (YYYY-MM-DD)'
    )
    backtest_parser.add_argument(
        '--end-date',
        default='2024-12-31',
        help='End date (YYYY-MM-DD)'
    )
    backtest_parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip generating plots'
    )
    backtest_parser.add_argument(
        '--no-markdown',
        action='store_true',
        help='Skip generating markdown report'
    )
    backtest_parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Enable benchmark mode: compare settlement day with other weekdays'
    )
    backtest_parser.add_argument(
        '--benchmark-max-dates',
        type=int,
        default=500,
        help='Maximum dates to test per weekday in benchmark mode (default: 500)'
    )
    backtest_parser.add_argument(
        '--benchmark-verbose',
        action='store_true',
        help='Print detailed trade information in benchmark mode'
    )
    backtest_parser.add_argument(
        '--indicators',
        nargs='+',
        help='Indicator(s) to use. Format: TYPE[:PARAM]. '
             'Types: price-diff, ma, momentum, candle, opening, weekly-pattern. '
             'Examples: ma:5:close, momentum:10, candle, opening:invert, weekly-pattern, weekly-pattern:adaptive. '
             'Multiple indicators run separately plus one combined backtest.'
    )
    backtest_parser.set_defaults(func=run_backtest)

    # ========== Max Pain Command ==========
    maxpain_parser = subparsers.add_parser(
        'maxpain',
        help='Run TXO max pain analysis',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    maxpain_parser.add_argument(
        '--start-date',
        default='2017-01-01',
        help='Start date (YYYY-MM-DD)'
    )
    maxpain_parser.add_argument(
        '--end-date',
        default='2024-12-31',
        help='End date (YYYY-MM-DD)'
    )
    maxpain_parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip generating plots'
    )
    maxpain_parser.set_defaults(func=run_maxpain)

    # ========== Report Command ==========
    report_parser = subparsers.add_parser(
        'report',
        help='Generate comprehensive analysis report'
    )
    report_parser.set_defaults(func=generate_report)

    # ========== Calculate Max Pain Command ==========
    calc_parser = subparsers.add_parser(
        'calc',
        help='Calculate max pain from TXO CSV file'
    )
    calc_parser.add_argument(
        'file',
        help='Path to TXO CSV file'
    )
    calc_parser.set_defaults(func=calculate_maxpain)

    # Parse arguments
    args = parser.parse_args()

    # Show help if no command specified
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute the command
    args.func(args)


if __name__ == '__main__':
    main()
