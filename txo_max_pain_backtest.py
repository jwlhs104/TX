#!/usr/bin/env python3
"""
TXO (Taiwan Options) Max Pain Point Backtesting System
台指選擇權最大痛點回測系統

This system analyzes Taiwan Options (TXO) max pain point patterns
and validates whether TAIEX futures are "attracted" to max pain levels on settlement days
as specified in the requirements.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import argparse
from scipy import stats
warnings.filterwarnings('ignore')

# Set Chinese font for matplotlib
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class TXOMaxPainBacktest:
    def __init__(self, start_date='2017-01-01', end_date='2024-12-31'):
        self.start_date = start_date
        self.end_date = end_date
        self.txo_data = None
        self.tx_data = None
        self.settlement_dates = None
        self.results = []

    def load_txo_data(self):
        """
        Load TXO (Taiwan Options) open interest data
        Expected format: Date, Strike_Price, Call_OI, Put_OI
        """
        # This would typically load from a CSV file with TXO data
        # For now, creating a placeholder structure
        print("Loading TXO open interest data...")

        # Placeholder - in real implementation, load from CSV
        # Expected columns: Date, Strike_Price, Call_OI, Put_OI, Expiry_Date
        try:
            # Try to load TXO data from a CSV file
            csv_path = '/Users/johnny/Desktop/JQC/TX/data/txo_open_interest.csv'
            self.txo_data = pd.read_csv(csv_path, encoding='utf-8')
            self.txo_data['Date'] = pd.to_datetime(self.txo_data['Date'])
            print(f"Successfully loaded TXO data: {len(self.txo_data)} records")
        except FileNotFoundError:
            print("TXO data file not found. Creating sample data for demonstration.")
            self.create_sample_txo_data()

        return self.txo_data

    def create_sample_txo_data(self):
        """
        Create sample TXO data for demonstration purposes
        """
        print("Creating sample TXO open interest data...")

        # Generate sample dates (every Wednesday from start to end date)
        dates = []
        current_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)

        while current_date <= end_date:
            if current_date.weekday() == 2:  # Wednesday
                dates.append(current_date)
            current_date += timedelta(days=1)

        # Generate sample data
        sample_data = []
        np.random.seed(42)

        for date in dates:
            # Assume index around 15000-20000 range
            base_price = 17000 + np.random.normal(0, 1000)

            # Generate strike prices around the base price
            strikes = range(int(base_price - 2000), int(base_price + 2000), 100)

            for strike in strikes:
                # Generate realistic OI data
                distance_from_atm = abs(strike - base_price)
                base_oi = max(1000 - distance_from_atm / 10, 10)

                call_oi = max(int(base_oi * np.random.exponential(1)), 1)
                put_oi = max(int(base_oi * np.random.exponential(1)), 1)

                sample_data.append({
                    'Date': date,
                    'Strike_Price': strike,
                    'Call_OI': call_oi,
                    'Put_OI': put_oi,
                    'Expiry_Date': date  # Same day settlement for simplicity
                })

        self.txo_data = pd.DataFrame(sample_data)
        print(f"Created sample TXO data: {len(self.txo_data)} records")
        return self.txo_data

    def load_tx_futures_data(self):
        """
        Load TX (Taiwan Futures) price data
        """
        print("Loading TX futures data...")

        try:
            csv_path = '/Users/johnny/Desktop/JQC/TX/data/filtered_tx_all_years.csv'
            df = pd.read_csv(csv_path, encoding='utf-8')

            # Create DataFrame with proper column names
            data = pd.DataFrame()
            data['Date'] = pd.to_datetime(df['交易日期'])
            data['Type'] = df['交易時段']
            data['Open'] = df['開盤價']
            data['High'] = df['最高價']
            data['Low'] = df['最低價']
            data['Close'] = df['收盤價']
            data['Volume'] = df['成交量'].fillna(0)

            # Filter to regular session data only
            self.tx_data = data[data['Type'] == '一般'].copy()
            self.tx_data = self.tx_data.dropna()

            print(f"Successfully loaded TX futures data: {len(self.tx_data)} trading days")
            print(f"Date range: {self.tx_data['Date'].min().strftime('%Y-%m-%d')} to {self.tx_data['Date'].max().strftime('%Y-%m-%d')}")

        except FileNotFoundError:
            print("TX futures data file not found. Please ensure the file exists.")
            self.tx_data = None

        return self.tx_data

    def get_settlement_dates(self):
        """
        Get settlement dates (every Wednesday) from the data
        """
        if self.txo_data is None:
            return None

        # Get unique settlement dates from TXO data
        settlement_dates = self.txo_data['Date'].unique()
        settlement_dates = pd.DataFrame({
            'date': pd.to_datetime(settlement_dates),
            'type': 'weekly'
        }).sort_values('date')

        # Filter by date range
        start_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)
        settlement_dates = settlement_dates[
            (settlement_dates['date'] >= start_date) &
            (settlement_dates['date'] <= end_date)
        ]

        self.settlement_dates = settlement_dates
        print(f"Found {len(self.settlement_dates)} settlement dates")

        return self.settlement_dates

    def calculate_max_pain(self, settlement_date):
        """
        Calculate max pain point for a given settlement date

        Max Pain is the strike price where option holders lose the most money
        (i.e., where the total value of CALL and PUT open interest is minimized)
        """
        # Get TXO data for the settlement date
        day_data = self.txo_data[self.txo_data['Date'] == settlement_date].copy()

        if len(day_data) == 0:
            return None, None

        # Calculate total pain for each strike price
        strike_pain = {}
        strikes = day_data['Strike_Price'].unique()

        for strike in strikes:
            total_pain = 0

            # Calculate pain from all strikes
            for _, row in day_data.iterrows():
                current_strike = row['Strike_Price']
                call_oi = row['Call_OI']
                put_oi = row['Put_OI']

                # If settlement price is above current strike
                if strike > current_strike:
                    # CALL options are ITM, PUT options are OTM
                    call_pain = call_oi * (strike - current_strike)
                    put_pain = 0
                else:
                    # PUT options are ITM, CALL options are OTM
                    call_pain = 0
                    put_pain = put_oi * (current_strike - strike)

                total_pain += call_pain + put_pain

            strike_pain[strike] = total_pain

        # Find strike with minimum total pain (max pain point)
        if strike_pain:
            max_pain_strike = min(strike_pain, key=strike_pain.get)
            return max_pain_strike, strike_pain

        return None, None

    def calculate_simplified_max_pain(self, settlement_date):
        """
        Simplified version: Find strike with maximum total open interest
        """
        day_data = self.txo_data[self.txo_data['Date'] == settlement_date].copy()

        if len(day_data) == 0:
            return None

        # Calculate total OI for each strike
        day_data['Total_OI'] = day_data['Call_OI'] + day_data['Put_OI']

        # Find strike with maximum total OI
        max_oi_row = day_data.loc[day_data['Total_OI'].idxmax()]
        return max_oi_row['Strike_Price']

    def run_max_pain_analysis(self):
        """
        Run the complete max pain analysis
        """
        if self.txo_data is None:
            self.load_txo_data()

        if self.tx_data is None:
            self.load_tx_futures_data()

        if self.settlement_dates is None:
            self.get_settlement_dates()

        if self.tx_data is None or self.settlement_dates is None:
            print("Required data not available for analysis")
            return None

        results = []
        print(f"\nRunning max pain analysis on {len(self.settlement_dates)} settlement dates...")

        for idx, settlement_row in self.settlement_dates.iterrows():
            settlement_date = settlement_row['date']

            # Get TX futures data for settlement date
            tx_settlement_data = self.tx_data[self.tx_data['Date'] == settlement_date]

            if len(tx_settlement_data) == 0:
                print(f"No TX data for settlement date: {settlement_date}")
                continue

            tx_data_row = tx_settlement_data.iloc[0]
            settlement_open = tx_data_row['Open']
            settlement_close = tx_data_row['Close']

            # Calculate max pain point
            max_pain_complex, strike_pain_dict = self.calculate_max_pain(settlement_date)
            max_pain_simple = self.calculate_simplified_max_pain(settlement_date)

            if max_pain_complex is None and max_pain_simple is None:
                print(f"Could not calculate max pain for {settlement_date}")
                continue

            # Use complex calculation if available, otherwise simple
            max_pain_price = max_pain_complex if max_pain_complex is not None else max_pain_simple

            # Calculate distances
            distance_open_to_max_pain = abs(settlement_open - max_pain_price)
            distance_close_to_max_pain = abs(settlement_close - max_pain_price)

            # Indicator A: Opening distance to max pain
            # Indicator B: Closing distance to max pain
            # Validation: Is B < A? (closer to max pain at close)
            attracted_to_max_pain = distance_close_to_max_pain < distance_open_to_max_pain

            # Calculate percentage distances
            pct_distance_open = (distance_open_to_max_pain / max_pain_price) * 100
            pct_distance_close = (distance_close_to_max_pain / max_pain_price) * 100

            # Store result
            result = {
                'settlement_date': settlement_date,
                'settlement_open': settlement_open,
                'settlement_close': settlement_close,
                'max_pain_price': max_pain_price,
                'distance_open_to_max_pain': distance_open_to_max_pain,
                'distance_close_to_max_pain': distance_close_to_max_pain,
                'pct_distance_open': pct_distance_open,
                'pct_distance_close': pct_distance_close,
                'attracted_to_max_pain': attracted_to_max_pain,
                'daily_move': settlement_close - settlement_open,
                'daily_move_pct': ((settlement_close - settlement_open) / settlement_open) * 100
            }

            results.append(result)

        self.results = pd.DataFrame(results)
        print(f"Completed max pain analysis with {len(self.results)} valid dates")

        return self.results

    def calculate_statistics(self):
        """
        Calculate statistical significance of max pain attraction
        """
        if self.results is None or len(self.results) == 0:
            return {}

        total_dates = len(self.results)
        attracted_count = self.results['attracted_to_max_pain'].sum()
        attracted_rate = (attracted_count / total_dates) * 100

        # Statistical test: binomial test (H0: p = 0.5)
        # If max pain has no effect, we expect 50% attraction rate
        p_value = stats.binom_test(attracted_count, total_dates, 0.5, alternative='greater')

        # Calculate average distances
        avg_distance_open = self.results['distance_open_to_max_pain'].mean()
        avg_distance_close = self.results['distance_close_to_max_pain'].mean()

        avg_pct_distance_open = self.results['pct_distance_open'].mean()
        avg_pct_distance_close = self.results['pct_distance_close'].mean()

        # Calculate distance improvement
        distance_improvement = avg_distance_open - avg_distance_close
        pct_distance_improvement = avg_pct_distance_open - avg_pct_distance_close

        stats_dict = {
            'total_settlement_dates': total_dates,
            'attracted_to_max_pain_count': attracted_count,
            'attracted_to_max_pain_rate': attracted_rate,
            'statistical_significance_p_value': p_value,
            'is_statistically_significant': p_value < 0.05,
            'avg_distance_open': avg_distance_open,
            'avg_distance_close': avg_distance_close,
            'distance_improvement': distance_improvement,
            'avg_pct_distance_open': avg_pct_distance_open,
            'avg_pct_distance_close': avg_pct_distance_close,
            'pct_distance_improvement': pct_distance_improvement
        }

        return stats_dict

    def analyze_by_year(self):
        """
        Analyze max pain attraction by year
        """
        if self.results is None or len(self.results) == 0:
            return {}

        results_copy = self.results.copy()
        results_copy['year'] = results_copy['settlement_date'].dt.year

        yearly_stats = {}
        for year in results_copy['year'].unique():
            year_data = results_copy[results_copy['year'] == year]

            total_dates = len(year_data)
            attracted_count = year_data['attracted_to_max_pain'].sum()
            attracted_rate = (attracted_count / total_dates) * 100 if total_dates > 0 else 0

            # Statistical test for this year
            if total_dates >= 5:  # Minimum sample size
                p_value = stats.binom_test(attracted_count, total_dates, 0.5, alternative='greater')
            else:
                p_value = 1.0

            yearly_stats[year] = {
                'total_dates': total_dates,
                'attracted_count': attracted_count,
                'attracted_rate': attracted_rate,
                'p_value': p_value,
                'is_significant': p_value < 0.05,
                'avg_distance_improvement': (year_data['distance_open_to_max_pain'].mean() -
                                           year_data['distance_close_to_max_pain'].mean())
            }

        return yearly_stats

    def create_visualizations(self):
        """
        Create comprehensive visualization plots
        """
        if self.results is None or len(self.results) == 0:
            print("No results available for plotting.")
            return

        fig = plt.figure(figsize=(20, 12))

        # 1. Max Pain Attraction Rate Over Time
        ax1 = plt.subplot(2, 3, 1)

        # Calculate monthly attraction rate
        results_copy = self.results.copy()
        results_copy['year_month'] = results_copy['settlement_date'].dt.to_period('M')
        monthly_stats = results_copy.groupby('year_month').agg({
            'attracted_to_max_pain': ['sum', 'count']
        }).reset_index()

        monthly_stats.columns = ['year_month', 'attracted_count', 'total_count']
        monthly_stats['attraction_rate'] = (monthly_stats['attracted_count'] / monthly_stats['total_count']) * 100
        monthly_stats['date'] = monthly_stats['year_month'].dt.to_timestamp()

        ax1.plot(monthly_stats['date'], monthly_stats['attraction_rate'], 'b-', linewidth=2)
        ax1.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='Random (50%)')
        ax1.set_title('Max Pain Attraction Rate Over Time', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Attraction Rate (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Distance Distribution
        ax2 = plt.subplot(2, 3, 2)

        ax2.hist(self.results['distance_open_to_max_pain'], bins=30, alpha=0.5,
                label='Opening Distance', color='red')
        ax2.hist(self.results['distance_close_to_max_pain'], bins=30, alpha=0.5,
                label='Closing Distance', color='blue')
        ax2.set_title('Distance to Max Pain Distribution', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Distance (Points)')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Yearly Attraction Rate
        ax3 = plt.subplot(2, 3, 3)

        yearly_stats = self.analyze_by_year()
        years = list(yearly_stats.keys())
        rates = [yearly_stats[year]['attracted_rate'] for year in years]
        colors = ['green' if yearly_stats[year]['is_significant'] else 'orange' for year in years]

        bars = ax3.bar(years, rates, color=colors, alpha=0.7)
        ax3.axhline(y=50, color='red', linestyle='--', alpha=0.7)
        ax3.set_title('Yearly Max Pain Attraction Rate', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Attraction Rate (%)')
        ax3.set_ylim(0, 100)

        # Add value labels on bars
        for bar, rate in zip(bars, rates):
            ax3.text(bar.get_x() + bar.get_width()/2., rate + 1,
                    f'{rate:.1f}%', ha='center', va='bottom')

        # 4. Distance Improvement Scatter Plot
        ax4 = plt.subplot(2, 3, 4)

        distance_improvement = (self.results['distance_open_to_max_pain'] -
                              self.results['distance_close_to_max_pain'])

        colors = ['green' if x > 0 else 'red' for x in distance_improvement]
        ax4.scatter(range(len(distance_improvement)), distance_improvement,
                   c=colors, alpha=0.6)
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax4.set_title('Distance Improvement by Settlement Date', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Settlement Date Index')
        ax4.set_ylabel('Distance Improvement (Points)')
        ax4.grid(True, alpha=0.3)

        # 5. Max Pain vs Settlement Price
        ax5 = plt.subplot(2, 3, 5)

        ax5.scatter(self.results['max_pain_price'], self.results['settlement_close'],
                   alpha=0.6, color='blue')

        # Add diagonal line (perfect correlation)
        min_price = min(self.results['max_pain_price'].min(), self.results['settlement_close'].min())
        max_price = max(self.results['max_pain_price'].max(), self.results['settlement_close'].max())
        ax5.plot([min_price, max_price], [min_price, max_price], 'r--', alpha=0.7)

        ax5.set_title('Max Pain vs Settlement Close Price', fontsize=12, fontweight='bold')
        ax5.set_xlabel('Max Pain Price')
        ax5.set_ylabel('Settlement Close Price')
        ax5.grid(True, alpha=0.3)

        # 6. Statistical Summary Text
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')

        stats = self.calculate_statistics()
        summary_text = f"""
Max Pain Analysis Summary

Total Settlement Dates: {stats.get('total_settlement_dates', 0)}
Attracted to Max Pain: {stats.get('attracted_to_max_pain_count', 0)}
Attraction Rate: {stats.get('attracted_to_max_pain_rate', 0):.1f}%

Statistical Significance:
p-value: {stats.get('statistical_significance_p_value', 0):.4f}
Significant: {stats.get('is_statistically_significant', False)}

Average Distances:
Opening: {stats.get('avg_distance_open', 0):.1f} points
Closing: {stats.get('avg_distance_close', 0):.1f} points
Improvement: {stats.get('distance_improvement', 0):.1f} points

Percentage Distances:
Opening: {stats.get('avg_pct_distance_open', 0):.2f}%
Closing: {stats.get('avg_pct_distance_close', 0):.2f}%
Improvement: {stats.get('pct_distance_improvement', 0):.2f}%
        """.strip()

        ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace')

        plt.tight_layout()

        # Save the plot
        plot_filename = '/Users/johnny/Desktop/JQC/TX/txo_max_pain_analysis.png'
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"\nMax pain analysis plots saved to: {plot_filename}")

        return plot_filename

    def generate_report(self):
        """
        Generate comprehensive max pain analysis report
        """
        if self.results is None or len(self.results) == 0:
            print("No results available. Run analysis first.")
            return

        print("\n" + "="*80)
        print("TXO 最大痛點分析報告")
        print("TXO Max Pain Point Analysis Report")
        print("="*80)

        # Overall statistics
        stats = self.calculate_statistics()

        print(f"\n【整體統計 Overall Statistics】")
        print(f"分析期間: {self.results['settlement_date'].min().strftime('%Y-%m-%d')} 至 {self.results['settlement_date'].max().strftime('%Y-%m-%d')}")
        print(f"總結算日數: {stats.get('total_settlement_dates', 0)}")
        print(f"被吸向最大痛點次數: {stats.get('attracted_to_max_pain_count', 0)}")
        print(f"吸引率: {stats.get('attracted_to_max_pain_rate', 0):.1f}%")

        print(f"\n【統計檢定 Statistical Test】")
        print(f"虛無假設 H0: 吸引率 = 50% (無效果)")
        print(f"對立假設 H1: 吸引率 > 50% (有效果)")
        print(f"p-值: {stats.get('statistical_significance_p_value', 0):.4f}")
        print(f"統計顯著性 (α=0.05): {'是' if stats.get('is_statistically_significant', False) else '否'}")

        print(f"\n【距離分析 Distance Analysis】")
        print(f"平均開盤距離: {stats.get('avg_distance_open', 0):.1f} 點")
        print(f"平均收盤距離: {stats.get('avg_distance_close', 0):.1f} 點")
        print(f"平均距離改善: {stats.get('distance_improvement', 0):.1f} 點")
        print(f"百分比距離改善: {stats.get('pct_distance_improvement', 0):.2f}%")

        # Yearly analysis
        yearly_stats = self.analyze_by_year()
        print(f"\n【年度分析 Yearly Analysis】")
        for year, year_stats in yearly_stats.items():
            significance = "顯著" if year_stats['is_significant'] else "不顯著"
            print(f"{year}: 吸引率={year_stats['attracted_rate']:.1f}% "
                  f"({year_stats['attracted_count']}/{year_stats['total_dates']}) "
                  f"統計={significance} (p={year_stats['p_value']:.3f})")

        print(f"\n【結論 Conclusion】")
        if stats.get('is_statistically_significant', False):
            if stats.get('attracted_to_max_pain_rate', 0) > 50:
                print("✓ 統計結果支持「大台被吸向最大痛點」的假設")
                print("✓ 結算日收盤價確實比開盤價更靠近最大痛點")
            else:
                print("✗ 統計結果不支持「大台被吸向最大痛點」的假設")
        else:
            print("? 統計結果無顯著性，無法確定是否存在最大痛點效應")

        print("\n" + "="*80)
        print("報告生成完成 Report Generation Complete")
        print("="*80)

    def save_results(self, filename='txo_max_pain_results.csv'):
        """
        Save detailed results to CSV file
        """
        if self.results is not None and len(self.results) > 0:
            filepath = f"/Users/johnny/Desktop/JQC/TX/{filename}"
            self.results.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"\nDetailed results saved to: {filepath}")
            return filepath
        else:
            print("No results to save.")
            return None

def main():
    """
    Main execution function
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='TXO 最大痛點分析系統 TXO Max Pain Analysis System')
    parser.add_argument('--start_date', default='2017-01-01',
                        help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end_date', default='2024-12-31',
                        help='End date in YYYY-MM-DD format')

    args = parser.parse_args()

    print("TXO 最大痛點分析系統 TXO Max Pain Analysis System")
    print("="*80)
    print(f"分析期間: {args.start_date} to {args.end_date}")

    # Initialize analyzer
    analyzer = TXOMaxPainBacktest(
        start_date=args.start_date,
        end_date=args.end_date
    )

    # Run complete analysis
    try:
        # Load data
        print("\n1. 載入資料 Loading Data...")
        analyzer.load_txo_data()
        analyzer.load_tx_futures_data()
        analyzer.get_settlement_dates()

        # Run analysis
        print("\n2. 執行最大痛點分析 Running Max Pain Analysis...")
        results = analyzer.run_max_pain_analysis()

        if results is not None and len(results) > 0:
            # Generate report
            print("\n3. 生成報告 Generating Report...")
            analyzer.generate_report()

            # Create visualizations
            print("\n4. 生成圖表 Creating Visualizations...")
            plot_filename = analyzer.create_visualizations()

            # Save results
            print("\n5. 儲存結果 Saving Results...")
            analyzer.save_results()

            return analyzer
        else:
            print("No valid results obtained from analysis.")
            return None

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()