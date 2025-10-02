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

    print("="*80)
    print("Taiwan Futures Settlement Day Backtest")
    print("="*80)
    print(f"Counting period: {args.counting_period}")
    print(f"Opening price calc: {args.opening_price_calc}")
    print(f"Previous close calc: {args.prev_close_calc}")
    print(f"Date range: {args.start_date} to {args.end_date}")
    print()

    # Initialize backtester
    backtester = TaiwanFuturesBacktest(
        start_date=args.start_date,
        end_date=args.end_date,
        counting_period=args.counting_period,
        opening_price_calc=args.opening_price_calc,
        prev_close_calc=args.prev_close_calc
    )

    # Run analysis
    try:
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
            backtester.create_performance_plots()

        print("6. Saving results...")
        backtester.save_detailed_results()

        if args.markdown:
            print("7. Saving markdown report...")
            backtester.save_results_summary_to_md()

        print("\n" + "="*80)
        print("✓ Backtest completed successfully!")
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
        '--markdown',
        action='store_true',
        help='Generate markdown report'
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
