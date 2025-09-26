#!/usr/bin/env python3
"""
Fixed Day Patterns Benchmark Test System
固定日期型態基準測試系統

This system compares settlement day patterns with fixed weekday patterns
to determine if the settlement day effect is unique or if other days show similar behavior.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
from taiwan_futures_backtest import TaiwanFuturesBacktest

warnings.filterwarnings('ignore')

# Set Chinese font for matplotlib
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class FixedDayBenchmarkTest:
    def __init__(self, start_date='2017-05-16', end_date='2024-12-31',
                 opening_price_calc="standard", prev_close_calc="standard"):
        self.start_date = start_date
        self.end_date = end_date
        self.opening_price_calc = opening_price_calc
        self.prev_close_calc = prev_close_calc
        self.data = None
        self.settlement_results = None
        self.benchmark_results = {}

        # Initialize the settlement day backtester
        self.settlement_backtester = TaiwanFuturesBacktest(
            start_date=start_date,
            end_date=end_date,
            counting_period="weekly",
            opening_price_calc=opening_price_calc,
            prev_close_calc=prev_close_calc
        )

        # Weekday mapping for readable names
        self.weekday_names = {
            0: 'Monday',
            1: 'Tuesday',
            3: 'Thursday',
            4: 'Friday'
        }

    def load_data(self):
        """Load Taiwan futures data"""
        print("Loading Taiwan futures data...")
        self.settlement_backtester.get_taiwan_futures_data()
        self.data = self.settlement_backtester.data
        return self.data

    def run_settlement_backtest(self):
        """Run the original settlement day backtest"""
        print("Running settlement day backtest...")
        self.settlement_results = self.settlement_backtester.run_backtest()
        return self.settlement_results

    def get_fixed_day_dates(self, weekday):
        """
        Get all dates for a specific weekday (0=Monday, 1=Tuesday, 3=Thursday, 4=Friday)
        Excludes settlement dates to avoid overlap
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Get all settlement dates to exclude them
        if self.settlement_backtester.settlement_dates is None:
            self.settlement_backtester.calculate_settlement_dates()
        settlement_dates = set(self.settlement_backtester.settlement_dates['date'])

        # Find all trading days for the specified weekday
        weekday_dates = []
        trading_dates = self.data['Date'].unique()

        for date in trading_dates:
            if date.weekday() == weekday and date not in settlement_dates:
                weekday_dates.append(date)

        return sorted(weekday_dates)

    def calculate_opening_day_for_date(self, target_date):
        """
        Calculate the opening day for a given target date
        Uses the same logic as settlement day calculation
        """
        # Look for previous trading days to find the opening day
        # Use a similar period as settlement days (approximately weekly)

        # Go back 7 days to find the opening day
        opening_date = target_date - timedelta(days=7)

        # Find the next available trading day after the 7-day lookback
        while not (self.data['Date'] == opening_date).any() and opening_date < target_date:
            opening_date += timedelta(days=1)

        # If we can't find a valid opening day within the range, try a shorter lookback
        if not (self.data['Date'] == opening_date).any():
            opening_date = target_date - timedelta(days=3)
            while not (self.data['Date'] == opening_date).any() and opening_date < target_date:
                opening_date += timedelta(days=1)

        return opening_date if (self.data['Date'] == opening_date).any() else None

    def get_opening_price(self, opening_day):
        """Get opening price based on calculation variation"""
        if self.opening_price_calc == "standard":
            return self.data[(self.data['Date'] == opening_day) & (self.data['Type'] == '一般')].iloc[0]['Open']
        elif self.opening_price_calc == "night":
            return self.data[(self.data['Date'] == opening_day) & (self.data['Type'] == '盤後')].iloc[0]['Open']
        else:
            raise Exception(f"opening_price_calc: {self.opening_price_calc} not supported")

    def get_prev_close(self, prev_day, target_date):
        """Get previous close price based on calculation variation"""
        if self.prev_close_calc == "standard":
            return self.data[(self.data['Date'] == prev_day) & (self.data['Type'] == '一般')].iloc[0]['Close']
        elif self.prev_close_calc == "night":
            return self.data[(self.data['Date'] == target_date) & (self.data['Type'] == '盤後')].iloc[0]['Close']
        elif self.prev_close_calc == "settlement_open":
            return self.data[(self.data['Date'] == target_date) & (self.data['Type'] == '一般')].iloc[0]['Open']
        else:
            raise Exception(f"prev_close_calc: {self.prev_close_calc} not supported")

    def run_fixed_day_backtest(self, weekday, max_dates=None):
        """
        Run backtest for a specific weekday using the same strategy as settlement days

        Args:
            weekday: 0=Monday, 1=Tuesday, 3=Thursday, 4=Friday
            max_dates: Maximum number of dates to test (for faster execution)
        """
        weekday_name = self.weekday_names[weekday]
        print(f"Running {weekday_name} backtest...")

        # Get all dates for this weekday
        weekday_dates = self.get_fixed_day_dates(weekday)

        if max_dates and len(weekday_dates) > max_dates:
            # Sample evenly across the time period
            indices = np.linspace(0, len(weekday_dates)-1, max_dates, dtype=int)
            weekday_dates = [weekday_dates[i] for i in indices]

        print(f"Testing {len(weekday_dates)} {weekday_name} dates...")

        results = []

        for target_date in weekday_dates:
            # Calculate opening day
            opening_day = self.calculate_opening_day_for_date(target_date)

            if opening_day is None or not (self.data['Date'] == opening_day).any():
                continue

            # Get previous day (day before target)
            prev_day = target_date - timedelta(days=1)
            while not (self.data['Date'] == prev_day).any() and prev_day >= opening_day:
                prev_day -= timedelta(days=1)

            if not (self.data['Date'] == prev_day).any():
                continue

            # Calculate trend indicator using the same logic as settlement days
            opening_price = self.get_opening_price(opening_day)
            prev_close = self.get_prev_close(prev_day, target_date)
            trend_indicator = prev_close - opening_price

            # Get target day data
            target_row = self.data[self.data['Date'] == target_date].iloc[0]
            target_open = target_row['Open']
            target_close = target_row['Close']
            target_high = target_row['High']
            target_low = target_row['Low']

            # Apply the same trading strategy
            if trend_indicator > 0:
                direction = 'long'
                pnl = target_close - target_open
                pnl_pct = pnl / target_open * 100
            elif trend_indicator < 0:
                direction = 'short'
                pnl = target_open - target_close
                pnl_pct = pnl / target_open * 100
            else:
                direction = 'no_trade'
                pnl = 0
                pnl_pct = 0

            # Calculate additional indicators
            prev_day_data = self.data[self.data['Date'] == prev_day].iloc[0]
            is_red_candle = prev_day_data['Close'] > prev_day_data['Open']
            is_high_open = target_open > prev_day_data['Close']

            # Calculate K-line body size
            body_size = abs(prev_day_data['Close'] - prev_day_data['Open'])
            total_range = prev_day_data['High'] - prev_day_data['Low']
            body_ratio = body_size / total_range if total_range > 0 else 0

            # Store result
            result = {
                'target_date': target_date,
                'weekday': weekday,
                'weekday_name': weekday_name,
                'opening_day': opening_day,
                'prev_day': prev_day,
                'opening_price': opening_price,
                'prev_close': prev_close,
                'trend_indicator': trend_indicator,
                'direction': direction,
                'target_open': target_open,
                'target_close': target_close,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'is_red_candle': is_red_candle,
                'is_high_open': is_high_open,
                'body_ratio': body_ratio,
                'trend_direction': 'up' if trend_indicator > 0 else 'down'
            }

            results.append(result)

        results_df = pd.DataFrame(results)
        print(f"Completed {weekday_name} backtest with {len(results_df)} trades")

        return results_df

    def run_all_benchmarks(self, max_dates_per_weekday=None):
        """Run benchmarks for all weekdays"""
        print("Running all fixed day pattern benchmarks...")

        # Test each weekday (Monday=0, Tuesday=1, Thursday=3, Friday=4)
        # Skip Wednesday=2 as that's settlement day
        for weekday in [0, 1, 3, 4]:
            weekday_name = self.weekday_names[weekday]
            try:
                results = self.run_fixed_day_backtest(weekday, max_dates=max_dates_per_weekday)
                self.benchmark_results[weekday_name] = results
            except Exception as e:
                print(f"Error running {weekday_name} benchmark: {e}")
                self.benchmark_results[weekday_name] = pd.DataFrame()

        return self.benchmark_results

    def calculate_performance_stats(self, results_df):
        """Calculate performance statistics (same as settlement day calculation)"""
        if results_df is None or len(results_df) == 0:
            return {}

        # Filter out no_trade entries
        trades = results_df[results_df['direction'] != 'no_trade'].copy()

        if len(trades) == 0:
            return {}

        # Basic statistics
        total_trades = len(trades)
        winning_trades = trades[trades['pnl_pct'] > 0]
        losing_trades = trades[trades['pnl_pct'] < 0]
        breakeven_trades = trades[trades['pnl_pct'] == 0]

        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        breakeven_count = len(breakeven_trades)

        # Performance calculations
        total_return = trades['pnl_pct'].sum()
        total_profit = winning_trades['pnl_pct'].sum() if win_count > 0 else 0
        total_loss = losing_trades['pnl_pct'].sum() if loss_count > 0 else 0

        max_profit = trades['pnl_pct'].max() if total_trades > 0 else 0
        max_loss = trades['pnl_pct'].min() if total_trades > 0 else 0

        avg_profit = total_profit / win_count if win_count > 0 else 0
        avg_loss = total_loss / loss_count if loss_count > 0 else 0
        avg_trade = total_return / total_trades if total_trades > 0 else 0

        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        profit_loss_ratio = abs(avg_profit / avg_loss) if avg_loss != 0 else 0

        # Event rate (percentage of days with signals)
        total_unique_days = len(self.data['Date'].unique()) if self.data is not None else total_trades
        event_rate = (total_trades / total_unique_days * 100) if total_unique_days > 0 else 0

        # Kelly Criterion
        if profit_loss_ratio > 0 and win_rate > 0:
            p = win_rate / 100
            q = 1 - p
            b = profit_loss_ratio
            kelly = (b * p - q) / b * 100
        else:
            kelly = 0

        # Maximum Drawdown
        cumulative_returns = trades['pnl_pct'].cumsum()
        running_max = cumulative_returns.expanding().max()
        drawdown = cumulative_returns - running_max
        max_drawdown = drawdown.min()

        stats = {
            '淨利': round(total_return, 2),
            '總獲利': round(total_profit, 2),
            '總虧損': round(total_loss, 2),
            '最大獲利': round(max_profit, 2),
            '最大虧損': round(max_loss, 2),
            '勝次': win_count,
            '敗次': loss_count,
            '總次': total_trades,
            '勝均': round(avg_profit, 2),
            '敗均': round(avg_loss, 2),
            '無歸類': breakeven_count,
            '筆均': round(avg_trade, 2),
            'EventRate': f"{event_rate:.1f}%",
            '盈虧比': round(profit_loss_ratio, 3),
            '勝率': f"{win_rate:.1f}%",
            '凱利': f"{kelly:.1f}%",
            '最大回撤': f"{max_drawdown:.1f}%"
        }

        return stats

    def compare_performance(self):
        """Compare performance between settlement days and fixed day patterns"""
        print("\nComparing performance across all patterns...")

        # Get settlement day performance
        settlement_stats = self.settlement_backtester.calculate_performance_stats()

        # Create comparison table
        comparison_data = []

        # Add settlement days
        comparison_data.append({
            'Pattern': 'Settlement Days (Wednesday)',
            **settlement_stats
        })

        # Add each weekday benchmark
        for weekday_name, results in self.benchmark_results.items():
            stats = self.calculate_performance_stats(results)
            comparison_data.append({
                'Pattern': weekday_name,
                **stats
            })

        comparison_df = pd.DataFrame(comparison_data)

        return comparison_df

    def create_comparison_plots(self):
        """Create comprehensive comparison plots"""
        if not self.benchmark_results:
            print("No benchmark results available for plotting.")
            return

        # Set up the plotting style
        plt.style.use('default')
        fig = plt.figure(figsize=(20, 12))

        # Prepare data for plotting
        all_stats = []

        # Settlement days
        settlement_stats = self.settlement_backtester.calculate_performance_stats()
        settlement_stats['Pattern'] = 'Settlement Days'
        all_stats.append(settlement_stats)

        # Benchmark days
        for weekday_name, results in self.benchmark_results.items():
            stats = self.calculate_performance_stats(results)
            stats['Pattern'] = weekday_name
            all_stats.append(stats)

        # Convert to DataFrame for easier plotting
        stats_df = pd.DataFrame(all_stats)

        # 1. Net Profit Comparison
        ax1 = plt.subplot(2, 3, 1)
        net_profits = [float(str(stat.get('淨利', 0)).replace('%', '')) for stat in all_stats]
        patterns = [stat['Pattern'] for stat in all_stats]

        bars = ax1.bar(patterns, net_profits, color=['red' if x < 0 else 'green' for x in net_profits], alpha=0.7)
        ax1.set_title('Net Profit Comparison', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Net Profit (%)')
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.xticks(rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, net_profits):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + (0.1 if height >= 0 else -0.5),
                    f'{value:.1f}%', ha='center', va='bottom' if height >= 0 else 'top')

        # 2. Win Rate Comparison
        ax2 = plt.subplot(2, 3, 2)
        win_rates = [float(str(stat.get('勝率', '0%')).replace('%', '')) for stat in all_stats]

        bars = ax2.bar(patterns, win_rates, color='skyblue', alpha=0.7)
        ax2.set_title('Win Rate Comparison', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Win Rate (%)')
        ax2.set_ylim(0, 100)
        plt.xticks(rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, win_rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom')

        # 3. Average Trade Comparison
        ax3 = plt.subplot(2, 3, 3)
        avg_trades = [float(str(stat.get('筆均', 0)).replace('%', '')) for stat in all_stats]

        bars = ax3.bar(patterns, avg_trades, color=['red' if x < 0 else 'orange' for x in avg_trades], alpha=0.7)
        ax3.set_title('Average Trade Comparison', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Average Trade (%)')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.xticks(rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, avg_trades):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + (0.01 if height >= 0 else -0.03),
                    f'{value:.2f}%', ha='center', va='bottom' if height >= 0 else 'top')

        # 4. Profit/Loss Ratio Comparison
        ax4 = plt.subplot(2, 3, 4)
        pl_ratios = [float(str(stat.get('盈虧比', 0))) for stat in all_stats]

        bars = ax4.bar(patterns, pl_ratios, color='purple', alpha=0.7)
        ax4.set_title('Profit/Loss Ratio Comparison', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Profit/Loss Ratio')
        ax4.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='Break-even')
        plt.xticks(rotation=45)
        ax4.legend()

        # Add value labels on bars
        for bar, value in zip(bars, pl_ratios):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{value:.2f}', ha='center', va='bottom')

        # 5. Total Trades Comparison
        ax5 = plt.subplot(2, 3, 5)
        total_trades = [stat.get('總次', 0) for stat in all_stats]

        bars = ax5.bar(patterns, total_trades, color='lightcoral', alpha=0.7)
        ax5.set_title('Total Trades Comparison', fontsize=12, fontweight='bold')
        ax5.set_ylabel('Number of Trades')
        plt.xticks(rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, total_trades):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + max(total_trades) * 0.01,
                    f'{value}', ha='center', va='bottom')

        # 6. Kelly Criterion Comparison
        ax6 = plt.subplot(2, 3, 6)
        kellys = [float(str(stat.get('凱利', '0%')).replace('%', '')) for stat in all_stats]

        bars = ax6.bar(patterns, kellys, color=['red' if x < 0 else 'green' for x in kellys], alpha=0.7)
        ax6.set_title('Kelly Criterion Comparison', fontsize=12, fontweight='bold')
        ax6.set_ylabel('Kelly Criterion (%)')
        ax6.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.xticks(rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, kellys):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height >= 0 else -1),
                    f'{value:.1f}%', ha='center', va='bottom' if height >= 0 else 'top')

        plt.tight_layout()

        # Save the plot
        plot_filename = '/Users/johnny/Desktop/JQC/TX/benchmark_comparison.png'
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"\nBenchmark comparison plots saved to: {plot_filename}")

        return plot_filename

    def generate_benchmark_report(self):
        """Generate comprehensive benchmark comparison report"""
        print("\n" + "="*80)
        print("固定日期型態基準測試報告")
        print("Fixed Day Patterns Benchmark Test Report")
        print("="*80)

        # Overall comparison
        comparison_df = self.compare_performance()

        print(f"\n【整體績效比較 Overall Performance Comparison】")
        print(f"分析期間: {self.data['Date'].min().strftime('%Y-%m-%d')} 至 {self.data['Date'].max().strftime('%Y-%m-%d')}")

        # Display comparison table
        print(f"\n{'Pattern':<25} {'淨利(%)':<10} {'勝率':<10} {'筆均(%)':<10} {'盈虧比':<10} {'總次':<10} {'凱利':<10}")
        print("-" * 85)

        for _, row in comparison_df.iterrows():
            pattern = row['Pattern']
            net_profit = row.get('淨利', 0)
            win_rate = row.get('勝率', 'N/A')
            avg_trade = row.get('筆均', 0)
            pl_ratio = row.get('盈虧比', 0)
            total_trades = row.get('總次', 0)
            kelly = row.get('凱利', 'N/A')

            print(f"{pattern:<25} {net_profit:<10.2f} {win_rate:<10} {avg_trade:<10.2f} {pl_ratio:<10.3f} {total_trades:<10} {kelly:<10}")

        # Analysis and insights
        print(f"\n【分析洞察 Analysis Insights】")

        # Find best performing pattern
        settlement_net_profit = comparison_df[comparison_df['Pattern'] == 'Settlement Days (Wednesday)']['淨利'].iloc[0]
        best_pattern = comparison_df.loc[comparison_df['淨利'].idxmax(), 'Pattern']
        best_net_profit = comparison_df['淨利'].max()

        print(f"最佳表現型態: {best_pattern} (淨利: {best_net_profit:.2f}%)")
        print(f"結算日表現: Settlement Days (淨利: {settlement_net_profit:.2f}%)")

        if best_pattern == 'Settlement Days (Wednesday)':
            print("✅ 結算日效應確實存在 - Settlement day effect is confirmed")
        else:
            print(f"⚠️  {best_pattern} 表現優於結算日 - {best_pattern} outperforms settlement days")

        # Compare win rates
        settlement_win_rate = float(str(comparison_df[comparison_df['Pattern'] == 'Settlement Days (Wednesday)']['勝率'].iloc[0]).replace('%', ''))
        avg_benchmark_win_rate = comparison_df[comparison_df['Pattern'] != 'Settlement Days (Wednesday)']['勝率'].apply(
            lambda x: float(str(x).replace('%', ''))
        ).mean()

        print(f"結算日勝率: {settlement_win_rate:.1f}%")
        print(f"其他日期平均勝率: {avg_benchmark_win_rate:.1f}%")

        if settlement_win_rate > avg_benchmark_win_rate:
            print("✅ 結算日勝率高於其他日期 - Settlement day win rate is higher than other days")
        else:
            print("⚠️  結算日勝率未明顯優於其他日期 - Settlement day win rate is not significantly better")

        print("\n" + "="*80)
        print("基準測試完成 Benchmark Test Complete")
        print("="*80)

def main():
    """Main execution function for benchmark testing"""
    print("固定日期型態基準測試系統 Fixed Day Patterns Benchmark Test System")
    print("="*80)

    # Initialize benchmark tester
    benchmark_tester = FixedDayBenchmarkTest(
        start_date='2017-05-16',
        end_date='2024-12-31',
        opening_price_calc='standard',
        prev_close_calc='standard'
    )

    try:
        # Load data
        print("\n1. 載入資料 Loading Data...")
        benchmark_tester.load_data()

        # Run settlement day backtest
        print("\n2. 執行結算日回測 Running Settlement Day Backtest...")
        benchmark_tester.run_settlement_backtest()

        # Run all benchmark tests
        print("\n3. 執行基準測試 Running Benchmark Tests...")
        benchmark_tester.run_all_benchmarks(max_dates_per_weekday=200)  # Limit for faster execution

        # Create comparison plots
        print("\n4. 生成比較圖表 Creating Comparison Plots...")
        plot_filename = benchmark_tester.create_comparison_plots()

        # Generate report
        print("\n5. 生成基準測試報告 Generating Benchmark Report...")
        benchmark_tester.generate_benchmark_report()

        print(f"\n基準測試完成！圖表已儲存至: {plot_filename}")
        print("Benchmark test complete! Charts saved to:", plot_filename)

        return benchmark_tester

    except Exception as e:
        print(f"Error during benchmark testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()