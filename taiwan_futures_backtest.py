#!/usr/bin/env python3
"""
Taiwan Futures Settlement Day Pattern Backtesting System
台指期結算日傾向回測系統

This system analyzes Taiwan Futures (TAIEX Futures) settlement day price patterns
and implements corresponding trading strategies as specified in the requirements.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set Chinese font for matplotlib
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class TaiwanFuturesBacktest:
    def __init__(self, start_date='2024-01-01', end_date='2024-12-31'):
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.settlement_dates = None
        self.results = []

    def get_taiwan_futures_data(self):
        """
        Load Taiwan Futures data from filtered CSV file
        """
        try:
            csv_path = '/Users/johnny/Desktop/JQC/TX/data/filtered_tx_2024.csv'
            print(f"Loading Taiwan futures data from {csv_path}...")

            # Read CSV file
            df = pd.read_csv(csv_path, encoding='utf-8')

            # Check if data is empty
            if df.empty:
                raise ValueError("No data in CSV file")

            # Parse date from 到期月份(週別) column - need to infer actual trading dates
            # For now, create sequential trading dates for 2024
            start_date = pd.to_datetime('2024-01-01')

            # Filter data to remove rows with missing closing prices
            df = df.dropna(subset=['收盤價'])

            # Create date index - assuming daily trading data
            trading_dates = pd.bdate_range(start=start_date, periods=len(df), freq='B')

            # Create DataFrame with proper column names
            data = pd.DataFrame(index=trading_dates[:len(df)])
            data['Open'] = df['開盤價'].values
            data['High'] = df['最高價'].values
            data['Low'] = df['最低價'].values
            data['Close'] = df['收盤價'].values
            data['Volume'] = df['成交量'].fillna(0).values

            # Remove any rows with NaN values
            data = data.dropna()

            print(f"Successfully loaded {len(data)} trading days of data from CSV")
            print(f"Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")

            self.data = data
            return data

        except Exception as e:
            print(f"Error loading CSV data: {e}")
            print("Falling back to Yahoo Finance data...")
            return self.get_yahoo_finance_data()

    def get_yahoo_finance_data(self):
        """
        Get Taiwan Futures data using Taiwan Stock Exchange Index as proxy
        Since direct futures data might not be available, we'll use ^TWII (Taiwan Weighted Index)
        """
        try:
            # Use Taiwan Weighted Index as proxy for Taiwan Futures
            ticker = "^TWII"
            print(f"Fetching Taiwan market data for {ticker}...")

            # Download data
            data = yf.download(ticker, start=self.start_date, end=self.end_date, progress=False)

            if data.empty:
                raise ValueError("No data retrieved")

            # Clean column names
            data.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

            # Remove any rows with NaN values
            data = data.dropna()

            print(f"Successfully retrieved {len(data)} trading days of data")
            print(f"Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")

            self.data = data
            return data

        except Exception as e:
            print(f"Error fetching data: {e}")
            print("Generating sample data for demonstration...")
            return self.generate_sample_data()

    def generate_sample_data(self):
        """Generate sample data for demonstration purposes"""
        dates = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        # Filter to weekdays only (stock market trading days)
        dates = dates[dates.weekday < 5]

        np.random.seed(42)
        n = len(dates)

        # Generate realistic price data starting from around 10000 (typical Taiwan index level)
        base_price = 10000
        returns = np.random.normal(0.0005, 0.015, n)  # Daily returns with slight positive drift
        prices = [base_price]

        for i in range(1, n):
            prices.append(prices[-1] * (1 + returns[i]))

        prices = np.array(prices)

        # Generate OHLC data
        data = pd.DataFrame(index=dates)
        data['Open'] = prices * (1 + np.random.normal(0, 0.002, n))
        data['High'] = np.maximum(data['Open'], prices * (1 + np.abs(np.random.normal(0, 0.01, n))))
        data['Low'] = np.minimum(data['Open'], prices * (1 - np.abs(np.random.normal(0, 0.01, n))))
        data['Close'] = prices
        data['Volume'] = np.random.lognormal(15, 0.5, n).astype(int)

        # Ensure OHLC consistency
        for i in range(len(data)):
            high = max(data.iloc[i]['Open'], data.iloc[i]['High'], data.iloc[i]['Close'])
            low = min(data.iloc[i]['Open'], data.iloc[i]['Low'], data.iloc[i]['Close'])
            data.iloc[i, data.columns.get_loc('High')] = high
            data.iloc[i, data.columns.get_loc('Low')] = low

        print(f"Generated sample data with {len(data)} trading days")
        self.data = data
        return data

    def calculate_settlement_dates(self):
        """
        Calculate settlement dates for both weekly and monthly options
        Weekly: Every Wednesday
        Monthly: Third Wednesday of each month
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call get_taiwan_futures_data() first.")

        start_date = self.data.index[0]
        end_date = self.data.index[-1]

        settlement_dates = []

        # Generate all dates in the range
        current_date = start_date
        while current_date <= end_date:
            # Check if it's a Wednesday (weekday = 2)
            if current_date.weekday() == 2:
                # Check if this Wednesday exists in our trading data
                if current_date in self.data.index:
                    # Determine if it's weekly or monthly settlement
                    # Monthly: Third Wednesday of the month
                    month_start = current_date.replace(day=1)
                    wednesdays_in_month = []

                    # Find all Wednesdays in the month
                    temp_date = month_start
                    while temp_date.month == current_date.month:
                        if temp_date.weekday() == 2:
                            wednesdays_in_month.append(temp_date)
                        temp_date += timedelta(days=1)

                    # Check if current date is the third Wednesday
                    is_monthly = len(wednesdays_in_month) >= 3 and current_date == wednesdays_in_month[2]

                    settlement_dates.append({
                        'date': current_date,
                        'type': 'monthly' if is_monthly else 'weekly'
                    })

            current_date += timedelta(days=1)

        self.settlement_dates = pd.DataFrame(settlement_dates)
        print(f"Found {len(self.settlement_dates)} settlement dates:")
        print(f"  Weekly settlements: {len(self.settlement_dates[self.settlement_dates['type'] == 'weekly'])}")
        print(f"  Monthly settlements: {len(self.settlement_dates[self.settlement_dates['type'] == 'monthly'])}")

        return self.settlement_dates

    def calculate_opening_day(self, settlement_date):
        """
        Calculate the opening day (first trading day after previous settlement)
        """
        # Find the previous settlement date
        prev_settlements = self.settlement_dates[
            self.settlement_dates['date'] < settlement_date
        ].sort_values('date')

        if len(prev_settlements) == 0:
            # If no previous settlement, use a week before current settlement
            opening_date = settlement_date - timedelta(days=7)
        else:
            # Use the day after the previous settlement
            prev_settlement = prev_settlements.iloc[-1]['date']
            opening_date = prev_settlement + timedelta(days=1)

        # Find the next available trading day
        while opening_date not in self.data.index and opening_date <= settlement_date:
            opening_date += timedelta(days=1)

        return opening_date if opening_date in self.data.index else None

    def run_backtest(self):
        """
        Run the complete backtesting strategy
        """
        if self.data is None:
            print("Loading data...")
            self.get_taiwan_futures_data()

        if self.settlement_dates is None:
            print("Calculating settlement dates...")
            self.calculate_settlement_dates()

        results = []

        print(f"\nRunning backtest on {len(self.settlement_dates)} settlement dates...")

        for idx, settlement_row in self.settlement_dates.iterrows():
            settlement_date = settlement_row['date']
            settlement_type = settlement_row['type']

            # Calculate opening day
            opening_day = self.calculate_opening_day(settlement_date)

            if opening_day is None or opening_day not in self.data.index:
                continue

            # Get previous day (day before settlement)
            prev_day = settlement_date - timedelta(days=1)
            while prev_day not in self.data.index and prev_day > opening_day:
                prev_day -= timedelta(days=1)

            if prev_day not in self.data.index:
                continue

            # Calculate trend indicator
            opening_price = self.data.loc[opening_day, 'Open']
            prev_close = self.data.loc[prev_day, 'Close']
            trend_indicator = prev_close - opening_price

            # Get settlement day data
            settlement_open = self.data.loc[settlement_date, 'Open']
            settlement_close = self.data.loc[settlement_date, 'Close']
            settlement_high = self.data.loc[settlement_date, 'High']
            settlement_low = self.data.loc[settlement_date, 'Low']

            # Determine trade direction
            if trend_indicator > 0:
                direction = 'long'
                pnl_pct = (settlement_close - settlement_open) / settlement_open * 100
            elif trend_indicator < 0:
                direction = 'short'
                pnl_pct = (settlement_open - settlement_close) / settlement_open * 100
            else:
                direction = 'no_trade'
                pnl_pct = 0

            # Calculate additional indicators
            prev_day_data = self.data.loc[prev_day]
            is_red_candle = prev_day_data['Close'] > prev_day_data['Open']
            is_high_open = settlement_open > prev_close

            # Calculate K-line body size
            body_size = abs(prev_day_data['Close'] - prev_day_data['Open'])
            total_range = prev_day_data['High'] - prev_day_data['Low']
            body_ratio = body_size / total_range if total_range > 0 else 0

            # Store result
            result = {
                'settlement_date': settlement_date,
                'settlement_type': settlement_type,
                'opening_day': opening_day,
                'prev_day': prev_day,
                'opening_price': opening_price,
                'prev_close': prev_close,
                'trend_indicator': trend_indicator,
                'direction': direction,
                'settlement_open': settlement_open,
                'settlement_close': settlement_close,
                'pnl_pct': pnl_pct,
                'is_red_candle': is_red_candle,
                'is_high_open': is_high_open,
                'body_ratio': body_ratio,
                'trend_direction': 'up' if trend_indicator > 0 else 'down'
            }

            results.append(result)

        self.results = pd.DataFrame(results)
        print(f"Completed backtest with {len(self.results)} trades")
        return self.results

    def calculate_performance_stats(self, results_df=None):
        """
        Calculate comprehensive performance statistics as specified in requirements
        """
        if results_df is None:
            results_df = self.results

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
        total_settlement_days = len(self.settlement_dates) if self.settlement_dates is not None else total_trades
        event_rate = (total_trades / total_settlement_days * 100) if total_settlement_days > 0 else 0

        # Kelly Criterion: f = (bp - q) / b, where b = odds, p = win rate, q = loss rate
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
            # Basic trading statistics
            '淨利': round(total_return, 2),
            '總獲利': round(total_profit, 2),
            '總虧損': round(total_loss, 2),
            '最大獲利': round(max_profit, 2),
            '最大虧損': round(max_loss, 2),

            # Trade count statistics
            '勝次': win_count,
            '敗次': loss_count,
            '總次': total_trades,

            # Performance ratios
            '勝均': round(avg_profit, 2),
            '敗均': round(avg_loss, 2),
            '無歸類': breakeven_count,
            '筆均': round(avg_trade, 2),

            # Key performance indicators
            'EventRate': f"{event_rate:.1f}%",
            '盈虧比': round(profit_loss_ratio, 3),
            '勝率': f"{win_rate:.1f}%",
            '凱利': f"{kelly:.1f}%",
            '最大回撤': f"{max_drawdown:.1f}%"
        }

        return stats

    def analyze_filters(self, results_df=None):
        """
        Analyze performance by different filter conditions
        """
        if results_df is None:
            results_df = self.results

        if results_df is None or len(results_df) == 0:
            return {}

        # Filter out no_trade entries
        trades = results_df[results_df['direction'] != 'no_trade'].copy()

        filter_analysis = {}

        # 1. Trend Direction Analysis
        up_trend = trades[trades['trend_direction'] == 'up']
        down_trend = trades[trades['trend_direction'] == 'down']

        filter_analysis['趨勢方向'] = {
            '往上': self.calculate_performance_stats(up_trend),
            '往下': self.calculate_performance_stats(down_trend)
        }

        # 2. Previous Day Candle Color Analysis
        red_candle = trades[trades['is_red_candle'] == True]
        black_candle = trades[trades['is_red_candle'] == False]

        filter_analysis['昨日K線'] = {
            '紅K': self.calculate_performance_stats(red_candle),
            '黑K': self.calculate_performance_stats(black_candle)
        }

        # 3. Opening Position Analysis
        high_open = trades[trades['is_high_open'] == True]
        low_open = trades[trades['is_high_open'] == False]

        filter_analysis['開盤位置'] = {
            '高開': self.calculate_performance_stats(high_open),
            '低開': self.calculate_performance_stats(low_open)
        }

        # 4. Settlement Type Analysis
        weekly = trades[trades['settlement_type'] == 'weekly']
        monthly = trades[trades['settlement_type'] == 'monthly']

        filter_analysis['結算類型'] = {
            '週選': self.calculate_performance_stats(weekly),
            '月選': self.calculate_performance_stats(monthly)
        }

        return filter_analysis

    def analyze_volatility_patterns(self):
        """
        Analyze volatility patterns around settlement dates
        """
        if self.data is None or self.results is None:
            return {}

        volatility_analysis = {}

        # Calculate daily volatility (rolling 5-day standard deviation of returns)
        self.data['returns'] = self.data['Close'].pct_change()
        self.data['volatility'] = self.data['returns'].rolling(window=5).std() * np.sqrt(252) * 100

        # Analyze volatility before and after settlement dates
        settlement_vol_data = []

        for _, settlement_row in self.settlement_dates.iterrows():
            settlement_date = settlement_row['date']
            settlement_type = settlement_row['type']

            # Get volatility data around settlement date (-5 to +5 days)
            for offset in range(-5, 6):
                target_date = settlement_date + timedelta(days=offset)
                if target_date in self.data.index:
                    vol_data = {
                        'settlement_date': settlement_date,
                        'settlement_type': settlement_type,
                        'offset_days': offset,
                        'date': target_date,
                        'volatility': self.data.loc[target_date, 'volatility']
                    }
                    settlement_vol_data.append(vol_data)

        vol_df = pd.DataFrame(settlement_vol_data)

        # Calculate average volatility by offset
        if len(vol_df) > 0:
            vol_by_offset = vol_df.groupby('offset_days')['volatility'].mean()
            volatility_analysis['volatility_by_offset'] = vol_by_offset.to_dict()

            # Settlement day vs normal day volatility
            settlement_vol = vol_df[vol_df['offset_days'] == 0]['volatility'].mean()
            normal_vol = self.data['volatility'].mean()

            volatility_analysis['settlement_vs_normal'] = {
                'settlement_day_volatility': settlement_vol,
                'normal_day_volatility': normal_vol,
                'volatility_ratio': settlement_vol / normal_vol if normal_vol > 0 else 1
            }

        return volatility_analysis

    def analyze_seasonal_patterns(self):
        """
        Analyze seasonal patterns in settlement day performance
        """
        if self.results is None:
            return {}

        trades = self.results[self.results['direction'] != 'no_trade'].copy()
        if len(trades) == 0:
            return {}

        # Add time-based features
        trades['month'] = trades['settlement_date'].dt.month
        trades['quarter'] = trades['settlement_date'].dt.quarter
        trades['year'] = trades['settlement_date'].dt.year
        trades['day_of_week'] = trades['settlement_date'].dt.dayofweek

        seasonal_analysis = {}

        # Monthly performance
        monthly_stats = {}
        for month in range(1, 13):
            month_trades = trades[trades['month'] == month]
            if len(month_trades) > 0:
                monthly_stats[month] = {
                    'win_rate': (month_trades['pnl_pct'] > 0).sum() / len(month_trades) * 100,
                    'avg_pnl': month_trades['pnl_pct'].mean(),
                    'total_trades': len(month_trades)
                }

        seasonal_analysis['monthly'] = monthly_stats

        # Quarterly performance
        quarterly_stats = {}
        for quarter in range(1, 5):
            quarter_trades = trades[trades['quarter'] == quarter]
            if len(quarter_trades) > 0:
                quarterly_stats[quarter] = {
                    'win_rate': (quarter_trades['pnl_pct'] > 0).sum() / len(quarter_trades) * 100,
                    'avg_pnl': quarter_trades['pnl_pct'].mean(),
                    'total_trades': len(quarter_trades)
                }

        seasonal_analysis['quarterly'] = quarterly_stats

        # Yearly performance
        yearly_stats = {}
        for year in trades['year'].unique():
            year_trades = trades[trades['year'] == year]
            if len(year_trades) > 0:
                yearly_stats[year] = {
                    'win_rate': (year_trades['pnl_pct'] > 0).sum() / len(year_trades) * 100,
                    'avg_pnl': year_trades['pnl_pct'].mean(),
                    'total_trades': len(year_trades),
                    'total_pnl': year_trades['pnl_pct'].sum()
                }

        seasonal_analysis['yearly'] = yearly_stats

        return seasonal_analysis

    def calculate_risk_metrics(self):
        """
        Calculate advanced risk metrics
        """
        if self.results is None:
            return {}

        trades = self.results[self.results['direction'] != 'no_trade'].copy()
        if len(trades) == 0:
            return {}

        returns = trades['pnl_pct'].values / 100  # Convert to decimal

        risk_metrics = {}

        # Basic metrics
        risk_metrics['total_return'] = returns.sum() * 100
        risk_metrics['annualized_return'] = (np.mean(returns) * 52) * 100  # Weekly settlements
        risk_metrics['volatility'] = np.std(returns) * np.sqrt(52) * 100

        # Sharpe Ratio (assuming 0% risk-free rate)
        if risk_metrics['volatility'] > 0:
            risk_metrics['sharpe_ratio'] = risk_metrics['annualized_return'] / risk_metrics['volatility']
        else:
            risk_metrics['sharpe_ratio'] = 0

        # Sortino Ratio (using downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            downside_deviation = np.std(downside_returns) * np.sqrt(52) * 100
            if downside_deviation > 0:
                risk_metrics['sortino_ratio'] = risk_metrics['annualized_return'] / downside_deviation
            else:
                risk_metrics['sortino_ratio'] = 0
        else:
            risk_metrics['sortino_ratio'] = float('inf') if risk_metrics['annualized_return'] > 0 else 0

        # Value at Risk (95% confidence)
        if len(returns) > 0:
            risk_metrics['var_95'] = np.percentile(returns, 5) * 100
            risk_metrics['cvar_95'] = returns[returns <= np.percentile(returns, 5)].mean() * 100 if len(returns[returns <= np.percentile(returns, 5)]) > 0 else 0

        # Maximum consecutive losses
        consecutive_losses = 0
        max_consecutive_losses = 0
        for ret in returns:
            if ret < 0:
                consecutive_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            else:
                consecutive_losses = 0

        risk_metrics['max_consecutive_losses'] = max_consecutive_losses

        # Calmar Ratio (Annual Return / Max Drawdown)
        cumulative_returns = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = cumulative_returns - running_max
        max_drawdown = np.min(drawdown) * 100

        if max_drawdown < 0:
            risk_metrics['calmar_ratio'] = risk_metrics['annualized_return'] / abs(max_drawdown)
        else:
            risk_metrics['calmar_ratio'] = 0

        risk_metrics['max_drawdown'] = max_drawdown

        return risk_metrics

    def create_performance_plots(self):
        """
        Create comprehensive performance visualization plots
        """
        if self.results is None or len(self.results) == 0:
            print("No results available for plotting.")
            return

        trades = self.results[self.results['direction'] != 'no_trade'].copy()
        if len(trades) == 0:
            print("No trades available for plotting.")
            return

        # Set up the plotting style
        plt.style.use('default')
        fig = plt.figure(figsize=(20, 16))

        # 1. Cumulative PnL Chart
        ax1 = plt.subplot(3, 3, 1)
        cumulative_pnl = trades['pnl_pct'].cumsum()
        ax1.plot(trades['settlement_date'], cumulative_pnl, linewidth=2, color='blue')
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        ax1.set_title('Cumulative P&L Over Time', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Cumulative P&L (%)')
        ax1.grid(True, alpha=0.3)

        # 2. Monthly Performance Heatmap
        ax2 = plt.subplot(3, 3, 2)
        trades['year'] = trades['settlement_date'].dt.year
        trades['month'] = trades['settlement_date'].dt.month
        monthly_pnl = trades.groupby(['year', 'month'])['pnl_pct'].sum().unstack(fill_value=0)

        if not monthly_pnl.empty:
            sns.heatmap(monthly_pnl, annot=True, fmt='.2f', cmap='RdYlGn', center=0, ax=ax2)
            ax2.set_title('Monthly P&L Heatmap', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Year')
            ax2.set_xlabel('Month')

        # 3. Win Rate by Settlement Type
        ax3 = plt.subplot(3, 3, 3)
        settlement_stats = trades.groupby('settlement_type').agg({
            'pnl_pct': lambda x: (x > 0).sum() / len(x) * 100
        }).round(1)

        bars = ax3.bar(settlement_stats.index, settlement_stats['pnl_pct'],
                       color=['orange', 'green'], alpha=0.7)
        ax3.set_title('Win Rate by Settlement Type', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Win Rate (%)')
        ax3.set_ylim(0, 100)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')

        # 4. P&L Distribution
        ax4 = plt.subplot(3, 3, 4)
        ax4.hist(trades['pnl_pct'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax4.axvline(x=0, color='red', linestyle='--', alpha=0.7)
        ax4.axvline(x=trades['pnl_pct'].mean(), color='green', linestyle='-', alpha=0.7, label=f'Mean: {trades["pnl_pct"].mean():.2f}%')
        ax4.set_title('P&L Distribution', fontsize=12, fontweight='bold')
        ax4.set_xlabel('P&L (%)')
        ax4.set_ylabel('Frequency')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        # 5. Drawdown Chart
        ax5 = plt.subplot(3, 3, 5)
        cumulative_returns = trades['pnl_pct'].cumsum()
        running_max = cumulative_returns.expanding().max()
        drawdown = cumulative_returns - running_max

        ax5.fill_between(trades['settlement_date'], drawdown, 0, alpha=0.3, color='red')
        ax5.plot(trades['settlement_date'], drawdown, color='red', linewidth=1)
        ax5.set_title('Drawdown Over Time', fontsize=12, fontweight='bold')
        ax5.set_ylabel('Drawdown (%)')
        ax5.grid(True, alpha=0.3)

        # 6. Quarterly Performance
        ax6 = plt.subplot(3, 3, 6)
        trades['quarter'] = trades['settlement_date'].dt.quarter
        quarterly_stats = trades.groupby('quarter').agg({
            'pnl_pct': ['mean', lambda x: (x > 0).sum() / len(x) * 100]
        }).round(2)
        quarterly_stats.columns = ['Avg P&L', 'Win Rate']

        x = quarterly_stats.index
        width = 0.35
        ax6_twin = ax6.twinx()

        bars1 = ax6.bar([i - width/2 for i in x], quarterly_stats['Avg P&L'],
                       width, label='Avg P&L (%)', alpha=0.7, color='blue')
        bars2 = ax6_twin.bar([i + width/2 for i in x], quarterly_stats['Win Rate'],
                            width, label='Win Rate (%)', alpha=0.7, color='orange')

        ax6.set_title('Quarterly Performance', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Quarter')
        ax6.set_ylabel('Average P&L (%)', color='blue')
        ax6_twin.set_ylabel('Win Rate (%)', color='orange')
        ax6.set_xticks(x)
        ax6.legend(loc='upper left')
        ax6_twin.legend(loc='upper right')

        # 7. Filter Analysis - Trend Direction
        ax7 = plt.subplot(3, 3, 7)
        trend_stats = trades.groupby('trend_direction').agg({
            'pnl_pct': ['mean', lambda x: (x > 0).sum() / len(x) * 100, 'count']
        }).round(2)
        trend_stats.columns = ['Avg P&L', 'Win Rate', 'Count']

        bars = ax7.bar(trend_stats.index, trend_stats['Win Rate'], alpha=0.7,
                      color=['red' if x < 50 else 'green' for x in trend_stats['Win Rate']])
        ax7.set_title('Win Rate by Trend Direction', fontsize=12, fontweight='bold')
        ax7.set_ylabel('Win Rate (%)')
        ax7.set_ylim(0, 100)

        for i, (bar, count) in enumerate(zip(bars, trend_stats['Count'])):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%\n(n={count})', ha='center', va='bottom')

        # 8. Volatility Analysis
        if hasattr(self, 'data') and 'volatility' in self.data.columns:
            ax8 = plt.subplot(3, 3, 8)
            volatility_analysis = self.analyze_volatility_patterns()

            if 'volatility_by_offset' in volatility_analysis:
                vol_data = volatility_analysis['volatility_by_offset']
                offsets = sorted(vol_data.keys())
                volatilities = [vol_data[offset] for offset in offsets]

                ax8.plot(offsets, volatilities, marker='o', linewidth=2, color='purple')
                ax8.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Settlement Day')
                ax8.set_title('Volatility Around Settlement Dates', fontsize=12, fontweight='bold')
                ax8.set_xlabel('Days from Settlement')
                ax8.set_ylabel('Volatility (%)')
                ax8.legend()
                ax8.grid(True, alpha=0.3)

        # 9. Risk-Return Scatter
        ax9 = plt.subplot(3, 3, 9)
        seasonal_analysis = self.analyze_seasonal_patterns()

        if 'yearly' in seasonal_analysis:
            yearly_data = seasonal_analysis['yearly']
            years = list(yearly_data.keys())
            returns = [yearly_data[year]['total_pnl'] for year in years]
            win_rates = [yearly_data[year]['win_rate'] for year in years]

            scatter = ax9.scatter(win_rates, returns, s=60, alpha=0.7, c=years, cmap='viridis')
            ax9.axhline(y=0, color='red', linestyle='--', alpha=0.7)
            ax9.axvline(x=50, color='red', linestyle='--', alpha=0.7)
            ax9.set_title('Annual Risk-Return Profile', fontsize=12, fontweight='bold')
            ax9.set_xlabel('Win Rate (%)')
            ax9.set_ylabel('Total P&L (%)')
            ax9.grid(True, alpha=0.3)

            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax9)
            cbar.set_label('Year')

        plt.tight_layout()

        # Save the plot
        plot_filename = '/Users/johnny/Desktop/JQC/TX/performance_analysis.png'
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"\nPerformance plots saved to: {plot_filename}")

        return plot_filename

    def generate_report(self):
        """
        Generate comprehensive performance report
        """
        if self.results is None or len(self.results) == 0:
            print("No results available. Run backtest first.")
            return

        print("\n" + "="*80)
        print("台指期結算日傾向回測報告")
        print("Taiwan Futures Settlement Day Pattern Backtest Report")
        print("="*80)

        # Overall performance
        overall_stats = self.calculate_performance_stats()

        print(f"\n【整體策略績效 Overall Performance】")
        print(f"分析期間: {self.data.index[0].strftime('%Y-%m-%d')} 至 {self.data.index[-1].strftime('%Y-%m-%d')}")
        print(f"總交易次數: {overall_stats.get('總次', 0)}")
        print(f"事件發生率: {overall_stats.get('EventRate', 'N/A')}")

        print(f"\n【基礎交易統計 Basic Trading Statistics】")
        print(f"淨利: {overall_stats.get('淨利', 0):.2f}%")
        print(f"總獲利: {overall_stats.get('總獲利', 0):.2f}%")
        print(f"總虧損: {overall_stats.get('總虧損', 0):.2f}%")
        print(f"最大獲利: {overall_stats.get('最大獲利', 0):.2f}%")
        print(f"最大虧損: {overall_stats.get('最大虧損', 0):.2f}%")

        print(f"\n【交易次數統計 Trade Count Statistics】")
        print(f"勝次: {overall_stats.get('勝次', 0)}")
        print(f"敗次: {overall_stats.get('敗次', 0)}")
        print(f"總次: {overall_stats.get('總次', 0)}")

        print(f"\n【績效比率 Performance Ratios】")
        print(f"勝均: {overall_stats.get('勝均', 0):.2f}%")
        print(f"敗均: {overall_stats.get('敗均', 0):.2f}%")
        print(f"筆均: {overall_stats.get('筆均', 0):.2f}%")
        print(f"無歸類: {overall_stats.get('無歸類', 0)}")

        print(f"\n【關鍵績效指標 Key Performance Indicators】")
        print(f"盈虧比: {overall_stats.get('盈虧比', 0):.3f}")
        print(f"勝率: {overall_stats.get('勝率', 'N/A')}")
        print(f"凱利: {overall_stats.get('凱利', 'N/A')}")
        print(f"最大回撤: {overall_stats.get('最大回撤', 'N/A')}")

        # Filter analysis
        filter_analysis = self.analyze_filters()

        print(f"\n【濾網分析 Filter Analysis】")

        for filter_name, filter_data in filter_analysis.items():
            print(f"\n{filter_name}:")
            for condition, stats in filter_data.items():
                if stats and stats.get('總次', 0) > 0:
                    print(f"  {condition}: 勝率={stats.get('勝率', 'N/A')}, 筆均={stats.get('筆均', 0):.2f}%, 總次={stats.get('總次', 0)}")
                else:
                    print(f"  {condition}: 無交易數據")

        print("\n" + "="*80)
        print("報告生成完成 Report Generation Complete")
        print("="*80)

    def save_detailed_results(self, filename='taiwan_futures_backtest_results.csv'):
        """
        Save detailed results to CSV file
        """
        if self.results is not None and len(self.results) > 0:
            # Save to current directory
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
    print("台指期結算日傾向回測系統 Taiwan Futures Settlement Day Backtest System")
    print("="*80)

    # Initialize backtester
    backtester = TaiwanFuturesBacktest(
        start_date='2024-01-01',
        end_date='2024-12-31'
    )

    # Run complete analysis
    try:
        # Get data
        print("\n1. 載入資料 Loading Data...")
        backtester.get_taiwan_futures_data()

        # Calculate settlement dates
        print("\n2. 計算結算日 Calculating Settlement Dates...")
        backtester.calculate_settlement_dates()

        # Run backtest
        print("\n3. 執行回測 Running Backtest...")
        results = backtester.run_backtest()

        # Generate report
        print("\n4. 生成報告 Generating Report...")
        backtester.generate_report()

        # Generate enhanced analysis
        print("\n5. 進階分析 Advanced Analysis...")
        volatility_analysis = backtester.analyze_volatility_patterns()
        seasonal_analysis = backtester.analyze_seasonal_patterns()
        risk_metrics = backtester.calculate_risk_metrics()

        # Create visualizations
        print("\n6. 生成圖表 Creating Visualizations...")
        plot_filename = backtester.create_performance_plots()

        # Save results
        print("\n7. 儲存結果 Saving Results...")
        backtester.save_detailed_results()

        return {
            'backtester': backtester,
            'volatility_analysis': volatility_analysis,
            'seasonal_analysis': seasonal_analysis,
            'risk_metrics': risk_metrics,
            'plot_filename': plot_filename
        }

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()