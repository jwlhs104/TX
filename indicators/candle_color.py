"""
Candle Color Indicator

This indicator determines the signal based on the previous day's candle color.
Red candle (Close > Open) indicates bullish sentiment.
Black candle (Close < Open) indicates bearish sentiment.
"""

import pandas as pd
from datetime import timedelta
from .base import TrendIndicator, IndicatorResult


class CandleColorIndicator(TrendIndicator):
    """
    Calculate trend based on previous day's candle color (red/black K-line)

    Red candle (Close > Open) = Long signal (value = 1)
    Black candle (Close < Open) = Short signal (value = -1)
    Doji (Close == Open) = No trade signal (value = 0)
    """

    def __init__(
        self,
        name: str = "CandleColor",
        invert: bool = False
    ):
        """
        Initialize the candle color indicator

        Args:
            name: Custom name for this indicator
            invert: If True, invert the signal (red K -> short, black K -> long)
        """
        super().__init__(name)
        self.invert = invert

    def calculate(
        self,
        opening_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        data: pd.DataFrame,
        **kwargs
    ) -> IndicatorResult:
        """
        Calculate the candle color indicator

        Args:
            opening_date: The opening date of the trading period
            settlement_date: The settlement date
            data: DataFrame with market data
            **kwargs: Not used

        Returns:
            IndicatorResult with the candle color signal
        """
        # Find previous day (day before settlement)
        prev_day = settlement_date - timedelta(days=1)
        while not (data['Date'] == prev_day).any() and prev_day >= data['Date'].min():
            prev_day -= timedelta(days=1)

        # Get previous day data
        prev_day_data = data[(data['Date'] == prev_day) & (data['Type'] == '一般')]

        if len(prev_day_data) == 0:
            # If no data available, return neutral signal
            return IndicatorResult(
                value=0,
                signal=0,
                strength=0,
                metadata={
                    'prev_day': prev_day,
                    'error': 'No previous day data available'
                }
            )

        prev_day_row = prev_day_data.iloc[0]
        prev_open = prev_day_row['Open']
        prev_close = prev_day_row['Close']
        prev_high = prev_day_row['High']
        prev_low = prev_day_row['Low']

        # Calculate candle body and total range
        body_size = prev_close - prev_open
        total_range = prev_high - prev_low

        # Determine signal based on candle color
        if body_size > 0:
            # Red candle
            value = 1
            signal = 1 if not self.invert else -1
        elif body_size < 0:
            # Black candle
            value = -1
            signal = -1 if not self.invert else 1
        else:
            # Doji
            value = 0
            signal = 0

        # Calculate strength based on body ratio
        if total_range > 0:
            strength = abs(body_size) / total_range
        else:
            strength = 0

        # Cap strength at 1.0
        strength = min(strength, 1.0)

        return IndicatorResult(
            value=value,
            signal=signal,
            strength=strength,
            metadata={
                'prev_day': prev_day,
                'prev_open': prev_open,
                'prev_close': prev_close,
                'body_size': body_size,
                'total_range': total_range,
                'is_red_candle': body_size > 0,
                'body_ratio': strength
            }
        )

    def __str__(self):
        invert_str = " (Inverted)" if self.invert else ""
        return f"{self.name}{invert_str}"
