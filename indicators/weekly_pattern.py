"""
Weekly Pattern Indicator

This indicator analyzes the weekly K-bar pattern formed during the holding period
(from opening_date to settlement_date - 1 day) to determine trade direction.

The weekly K-bar consists of:
- Open: opening_date's opening price
- Close: (settlement_date - 1 day)'s closing price
- High: highest price during the period
- Low: lowest price during the period

The indicator classifies the weekly pattern into 11 types and determines
the optimal trading signal based on either technical analysis rules or
historical statistics (adaptive mode).
"""

import pandas as pd
from datetime import timedelta
from .base import TrendIndicator, IndicatorResult


class WeeklyPatternIndicator(TrendIndicator):
    """
    Calculate trend based on weekly K-bar pattern analysis

    Pattern Types:
    - BIG_BULLISH: Large bullish body (>60% of total range)
    - BIG_BEARISH: Large bearish body (>60% of total range)
    - LONG_UPPER_BULLISH: Bullish with long upper shadow (>2x body)
    - LONG_UPPER_BEARISH: Bearish with long upper shadow (>2x body)
    - LONG_LOWER_BULLISH: Bullish with long lower shadow (>2x body)
    - LONG_LOWER_BEARISH: Bearish with long lower shadow (>2x body)
    - MEDIUM_BULLISH: Medium bullish body (30-60%)
    - MEDIUM_BEARISH: Medium bearish body (30-60%)
    - SMALL_BODY_BULLISH: Small bullish body (<30%)
    - SMALL_BODY_BEARISH: Small bearish body (<30%)
    - DOJI: No body (open == close)
    """

    # Default signal mapping based on technical analysis
    DEFAULT_SIGNALS = {
        "BIG_BULLISH": 1,           # Strong bullish -> Long
        "BIG_BEARISH": -1,          # Strong bearish -> Short
        "LONG_UPPER_BULLISH": -1,   # Bullish exhaustion -> Short
        "LONG_UPPER_BEARISH": -1,   # Bearish continuation -> Short
        "LONG_LOWER_BULLISH": 1,    # Bullish continuation -> Long
        "LONG_LOWER_BEARISH": 1,    # Bearish exhaustion -> Long
        "MEDIUM_BULLISH": 1,        # Moderate bullish -> Long
        "MEDIUM_BEARISH": -1,       # Moderate bearish -> Short
        "SMALL_BODY_BULLISH": 1,    # Small bullish body -> Long
        "SMALL_BODY_BEARISH": -1,   # Small bearish body -> Short
        "DOJI": 0,                  # Indecision -> No trade
    }

    def __init__(
        self,
        name: str = "WeeklyPattern",
        opening_price_calc: str = "standard",
        prev_close_calc: str = "standard",
        use_adaptive: bool = False,
        backtester = None,
        train_end_date: str = None
    ):
        """
        Initialize the weekly pattern indicator

        Args:
            name: Custom name for this indicator
            opening_price_calc: Method for calculating opening price ('standard' or 'night')
            prev_close_calc: Method for calculating previous close ('standard', 'night', or 'settlement_open')
            use_adaptive: If True, use historical statistics to determine signals
            backtester: TaiwanFuturesBacktest instance (required for adaptive mode)
            train_end_date: Optional cutoff date for training data (format: 'YYYY-MM-DD').
                          If specified, only data up to this date will be used for training.
        """
        super().__init__(name)
        self.opening_price_calc = opening_price_calc
        self.prev_close_calc = prev_close_calc
        self.use_adaptive = use_adaptive
        self.backtester = backtester
        self.train_end_date = pd.to_datetime(train_end_date) if train_end_date else None

        # For adaptive mode
        self.adaptive_signals = {}
        self.is_trained = False

        if use_adaptive and backtester is None:
            raise ValueError("WeeklyPatternIndicator with use_adaptive=True requires a backtester instance")

    def calculate(
        self,
        opening_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        data: pd.DataFrame,
        **kwargs
    ) -> IndicatorResult:
        """
        Calculate the weekly pattern indicator

        Args:
            opening_date: The opening date of the trading period
            settlement_date: The settlement date
            data: DataFrame with market data
            **kwargs: Not used

        Returns:
            IndicatorResult with the weekly pattern signal
        """
        # Train if using adaptive mode and not yet trained
        if self.use_adaptive and not self.is_trained:
            self._train_pattern_signals(data)

        # Get weekly K-bar data
        weekly_kbar = self._get_weekly_kbar(opening_date, settlement_date, data)

        if weekly_kbar is None:
            return IndicatorResult(
                value=0,
                signal=0,
                strength=0,
                metadata={
                    'error': 'Could not calculate weekly K-bar',
                    'opening_date': opening_date,
                    'settlement_date': settlement_date
                }
            )

        # Classify pattern
        pattern = self._classify_pattern(
            weekly_kbar['open'],
            weekly_kbar['close'],
            weekly_kbar['high'],
            weekly_kbar['low']
        )

        # Determine signal
        if self.use_adaptive:
            signal = self.adaptive_signals.get(pattern, 0)
        else:
            signal = self.DEFAULT_SIGNALS.get(pattern, 0)

        # Calculate value (close - open)
        value = weekly_kbar['close'] - weekly_kbar['open']

        # Calculate strength (body ratio)
        total_range = weekly_kbar['high'] - weekly_kbar['low']
        if total_range > 0:
            strength = abs(value) / total_range
        else:
            strength = 0

        return IndicatorResult(
            value=value,
            signal=signal,
            strength=strength,
            metadata={
                'pattern': pattern,
                'weekly_open': weekly_kbar['open'],
                'weekly_close': weekly_kbar['close'],
                'weekly_high': weekly_kbar['high'],
                'weekly_low': weekly_kbar['low'],
                'body_ratio': strength,
                'opening_date': opening_date,
                'settlement_date': settlement_date
            }
        )

    def _get_weekly_kbar(
        self,
        opening_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        data: pd.DataFrame
    ) -> dict:
        """
        Calculate weekly K-bar using the same logic as taiwan_futures_backtest.get_date_range_data

        The range includes:
        - opening_date data (based on opening_price_calc)
        - all data between opening_date and settlement_date (exclusive)
        - prev_close data (based on prev_close_calc)

        Returns:
            dict with keys: open, close, high, low
        """
        try:
            # Get opening price (weekly Open)
            opening_price = self._get_opening_price(opening_date, data)

            # Get previous close (weekly Close)
            prev_close = self._get_prev_close(settlement_date, data)

            # Get date range data using the same logic as taiwan_futures_backtest
            date_range_data = self._get_date_range_data(opening_date, settlement_date, data)

            if len(date_range_data) == 0:
                return None

            # Calculate High and Low from the combined data
            weekly_high = date_range_data['High'].max()
            weekly_low = date_range_data['Low'].min()

            return {
                'open': opening_price,
                'close': prev_close,
                'high': weekly_high,
                'low': weekly_low
            }

        except Exception as e:
            return None

    def _get_date_range_data(
        self,
        opening_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get date range data using the same logic as taiwan_futures_backtest.get_date_range_data

        This ensures High/Low calculations match the backtest system exactly.
        """
        # 1. Between data (exclusive of both ends)
        between_data = data[
            (data['Date'] > opening_date) &
            (data['Date'] < settlement_date)
        ]

        # 2. Opening data
        if self.opening_price_calc == "standard":
            open_data = data[
                (data['Date'] == opening_date) &
                (data['Type'] == '一般')
            ]
        elif self.opening_price_calc == "night":
            open_data = data[
                (data['Date'] == opening_date)
            ]
        else:
            raise ValueError(f"Unsupported opening_price_calc: {self.opening_price_calc}")

        # 3. Close data
        if self.prev_close_calc == "standard":
            close_data = pd.DataFrame()
        elif self.prev_close_calc == "night":
            close_data = data[
                (data['Date'] == settlement_date) &
                (data['Type'] == '盤後')
            ]
        elif self.prev_close_calc == "settlement_open":
            close_data = data[
                (data['Date'] == settlement_date)
            ]
            # When using settlement_open, High/Low/Close should equal Open
            open_values = close_data.loc[
                close_data['Type'] == '一般',
                'Open'
            ].values
            if len(open_values) > 0:
                close_data = close_data.copy()
                close_data.loc[
                    close_data['Type'] == '一般',
                    ['High', 'Low', 'Close']
                ] = open_values[:, None] * [1, 1, 1]
        else:
            raise ValueError(f"Unsupported prev_close_calc: {self.prev_close_calc}")

        # 4. Combine all data
        date_range_data = pd.concat([open_data, between_data, close_data])

        return date_range_data

    def _get_opening_price(self, opening_date: pd.Timestamp, data: pd.DataFrame) -> float:
        """Get opening price based on calculation method"""
        if self.opening_price_calc == "standard":
            return data[(data['Date'] == opening_date) & (data['Type'] == '一般')].iloc[0]['Open']
        elif self.opening_price_calc == "night":
            return data[(data['Date'] == opening_date) & (data['Type'] == '盤後')].iloc[0]['Open']
        else:
            raise ValueError(f"Unsupported opening_price_calc: {self.opening_price_calc}")

    def _get_prev_close(self, settlement_date: pd.Timestamp, data: pd.DataFrame) -> float:
        """Get previous close price based on calculation method"""
        # Find previous day
        prev_day = settlement_date - timedelta(days=1)
        while not (data['Date'] == prev_day).any() and prev_day >= data['Date'].min():
            prev_day -= timedelta(days=1)

        if self.prev_close_calc == "standard":
            return data[(data['Date'] == prev_day) & (data['Type'] == '一般')].iloc[0]['Close']
        elif self.prev_close_calc == "night":
            return data[(data['Date'] == settlement_date) & (data['Type'] == '盤後')].iloc[0]['Close']
        elif self.prev_close_calc == "settlement_open":
            return data[(data['Date'] == settlement_date) & (data['Type'] == '一般')].iloc[0]['Open']
        else:
            raise ValueError(f"Unsupported prev_close_calc: {self.prev_close_calc}")

    def _classify_pattern(
        self,
        open_price: float,
        close_price: float,
        high_price: float,
        low_price: float
    ) -> str:
        """
        Classify the weekly K-bar into one of 11 pattern types

        Fixed thresholds:
        - Big body: body_ratio > 0.6
        - Small body: body_ratio < 0.3
        - Long shadow: shadow_length > body_length * 2
        """
        body = close_price - open_price
        total_range = high_price - low_price

        # Handle edge case
        if total_range == 0:
            return "DOJI"

        body_ratio = abs(body) / total_range
        upper_shadow = high_price - max(open_price, close_price)
        lower_shadow = min(open_price, close_price) - low_price

        # Check for DOJI first
        if body == 0:
            return "DOJI"

        # Determine direction
        is_bullish = body > 0

        # Big body (>60%)
        if body_ratio > 0.6:
            return "BIG_BULLISH" if is_bullish else "BIG_BEARISH"

        # Long upper shadow (upper shadow > 2x body)
        if upper_shadow > abs(body) * 2:
            return "LONG_UPPER_BULLISH" if is_bullish else "LONG_UPPER_BEARISH"

        # Long lower shadow (lower shadow > 2x body)
        if lower_shadow > abs(body) * 2:
            return "LONG_LOWER_BULLISH" if is_bullish else "LONG_LOWER_BEARISH"

        # Small body (<30%)
        if body_ratio < 0.3:
            return "SMALL_BODY_BULLISH" if is_bullish else "SMALL_BODY_BEARISH"

        # Medium body (30-60%)
        return "MEDIUM_BULLISH" if is_bullish else "MEDIUM_BEARISH"

    def _train_pattern_signals(self, data: pd.DataFrame):
        """
        Train the pattern signals based on historical data

        This method analyzes all historical trades, classifies each weekly pattern,
        and determines the optimal trading direction based on actual settlement day returns.
        """
        if self.backtester is None:
            raise ValueError("Adaptive mode requires a backtester instance")

        if self.train_end_date:
            print(f"Training weekly pattern strategy (training data up to {self.train_end_date.strftime('%Y-%m-%d')})...")
        else:
            print(f"Training weekly pattern strategy...")

        # Get settlement dates from backtester
        if not hasattr(self.backtester, 'settlement_dates') or self.backtester.settlement_dates is None:
            raise ValueError("Backtester must have settlement dates calculated")

        settlement_dates = self.backtester.settlement_dates

        # Filter settlement dates if train_end_date is specified
        if self.train_end_date:
            settlement_dates = settlement_dates[settlement_dates['date'] <= self.train_end_date]
            print(f"  Using {len(settlement_dates)} settlement dates for training (up to {self.train_end_date.strftime('%Y-%m-%d')})")

        # Collect historical data for all patterns
        pattern_data = {}

        for _, settlement_row in settlement_dates.iterrows():
            settlement_date = settlement_row['date']

            # Calculate opening date
            opening_date = self.backtester.calculate_opening_date(settlement_date)
            if opening_date is None:
                continue

            try:
                # Get weekly K-bar
                weekly_kbar = self._get_weekly_kbar(opening_date, settlement_date, data)
                if weekly_kbar is None:
                    continue

                # Classify pattern
                pattern = self._classify_pattern(
                    weekly_kbar['open'],
                    weekly_kbar['close'],
                    weekly_kbar['high'],
                    weekly_kbar['low']
                )

                # Get actual price change on settlement day
                settlement_day_data = data[data['Date'] == settlement_date]
                if len(settlement_day_data) == 0:
                    continue

                settlement_row_data = settlement_day_data.iloc[0]
                actual_change_pct = (settlement_row_data['Close'] - settlement_row_data['Open']) / settlement_row_data['Open'] * 100

                # Store in pattern data
                if pattern not in pattern_data:
                    pattern_data[pattern] = []
                pattern_data[pattern].append(actual_change_pct)

            except Exception as e:
                # Skip this trade if there's an error
                continue

        # Analyze each pattern and determine optimal signal
        print("\nWeekly Pattern Analysis:")
        print("=" * 80)

        for pattern, changes in pattern_data.items():
            if len(changes) == 0:
                continue

            # Calculate statistics
            total_change = sum(changes)
            count = len(changes)
            avg_change = total_change / count

            # Determine optimal signal based on cumulative direction
            if total_change > 0:
                optimal_signal = 1  # Go long
                direction = "LONG"
            elif total_change < 0:
                optimal_signal = -1  # Go short
                direction = "SHORT"
            else:
                optimal_signal = 0  # No trade
                direction = "NEUTRAL"

            # Store optimal signal
            self.adaptive_signals[pattern] = optimal_signal

            # Store statistics
            self.adaptive_signals[f"{pattern}_stats"] = {
                'total_change': total_change,
                'count': count,
                'avg_change': avg_change,
                'direction': direction
            }

            print(f"{pattern:25} | Count: {count:3} | Avg: {avg_change:7.2f}% | Total: {total_change:8.2f}% | Signal: {direction:7}")

        print("=" * 80)
        print(f"Training complete! {len(pattern_data)} patterns analyzed.\n")

        self.is_trained = True

    def __str__(self):
        mode_str = " (Adaptive)" if self.use_adaptive else " (Rule-based)"
        return f"{self.name}{mode_str}"
