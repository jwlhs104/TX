"""
Moving Average Trend Indicator

Determines trend based on price position relative to moving average
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from .base import TrendIndicator, IndicatorResult


class MovingAverageIndicator(TrendIndicator):
    """
    Calculate trend based on price position relative to moving average

    If current price > MA: Long signal
    If current price < MA: Short signal
    If current price = MA: No trade signal
    """

    def __init__(
        self,
        name: str = "MovingAverage",
        period: int = 5,
        price_type: str = "close"
    ):
        """
        Initialize the moving average indicator

        Args:
            name: Custom name for this indicator
            period: Number of periods for the moving average (default: 5)
            price_type: Which price to use ('open', 'close', 'high', 'low', default: 'close')
        """
        super().__init__(name)
        self.period = period
        self.price_type = price_type.capitalize()

    def calculate(
        self,
        opening_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        data: pd.DataFrame,
        **kwargs
    ) -> IndicatorResult:
        """
        Calculate the moving average indicator

        Args:
            opening_date: The opening date of the trading period
            settlement_date: The settlement date
            data: DataFrame with market data
            **kwargs: Not used

        Returns:
            IndicatorResult with MA comparison value and trading signal
        """
        # Get previous day (day before settlement)
        prev_day = settlement_date - timedelta(days=1)
        while not (data['Date'] == prev_day).any() and prev_day >= opening_date:
            prev_day -= timedelta(days=1)

        # Get data up to and including previous day (一般 session only for consistency)
        historical_data = data[
            (data['Date'] <= prev_day) &
            (data['Type'] == '一般')
        ].sort_values('Date')

        if len(historical_data) < self.period:
            # Not enough data, return neutral signal
            return IndicatorResult(
                value=0,
                signal=0,
                strength=0,
                metadata={
                    'error': f'Not enough data for MA calculation (need {self.period}, have {len(historical_data)})'
                }
            )

        # Calculate moving average
        prices = historical_data[self.price_type].values[-self.period:]
        ma_value = np.mean(prices)

        # Get current price (previous day's close for settlement day prediction)
        current_price = historical_data.iloc[-1][self.price_type]

        # Calculate the indicator value (difference from MA)
        value = current_price - ma_value

        # Determine signal
        if value > 0:
            signal = 1  # Long (price above MA)
        elif value < 0:
            signal = -1  # Short (price below MA)
        else:
            signal = 0  # No trade

        # Calculate strength based on percentage difference from MA
        strength = abs(value) / ma_value if ma_value != 0 else 0
        strength = min(strength, 1.0)  # Cap at 1.0

        return IndicatorResult(
            value=value,
            signal=signal,
            strength=strength,
            metadata={
                'ma_value': ma_value,
                'current_price': current_price,
                'period': self.period,
                'price_type': self.price_type
            }
        )
