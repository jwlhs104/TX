"""
Opening Position Indicator

This indicator determines the signal based on whether the settlement day
opens higher or lower than the previous day's close.
Opening higher (gap up) indicates bullish sentiment.
Opening lower (gap down) indicates bearish sentiment.
"""

import pandas as pd
from datetime import timedelta
from .base import TrendIndicator, IndicatorResult


class OpeningPositionIndicator(TrendIndicator):
    """
    Calculate trend based on opening position relative to previous close

    Gap Up (Open > Previous Close) = Long signal (value = 1)
    Gap Down (Open < Previous Close) = Short signal (value = -1)
    No Gap (Open == Previous Close) = No trade signal (value = 0)
    """

    def __init__(
        self,
        name: str = "OpeningPosition",
        invert: bool = False
    ):
        """
        Initialize the opening position indicator

        Args:
            name: Custom name for this indicator
            invert: If True, invert the signal (gap up -> short, gap down -> long)
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
        Calculate the opening position indicator

        Args:
            opening_date: The opening date of the trading period
            settlement_date: The settlement date
            data: DataFrame with market data
            **kwargs: Not used

        Returns:
            IndicatorResult with the opening position signal
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
                    'settlement_date': settlement_date,
                    'error': 'No previous day data available'
                }
            )

        # Get settlement day data
        settlement_day_data = data[(data['Date'] == settlement_date) & (data['Type'] == '一般')]

        if len(settlement_day_data) == 0:
            # If no settlement day data available, return neutral signal
            return IndicatorResult(
                value=0,
                signal=0,
                strength=0,
                metadata={
                    'prev_day': prev_day,
                    'settlement_date': settlement_date,
                    'error': 'No settlement day data available'
                }
            )

        prev_day_row = prev_day_data.iloc[0]
        settlement_day_row = settlement_day_data.iloc[0]

        prev_close = prev_day_row['Close']
        settlement_open = settlement_day_row['Open']
        settlement_high = settlement_day_row['High']
        settlement_low = settlement_day_row['Low']

        # Calculate gap size
        gap_size = settlement_open - prev_close
        gap_pct = (gap_size / prev_close) * 100 if prev_close > 0 else 0

        # Determine signal based on gap direction
        if gap_size > 0:
            # Gap up
            value = 1
            signal = 1 if not self.invert else -1
        elif gap_size < 0:
            # Gap down
            value = -1
            signal = -1 if not self.invert else 1
        else:
            # No gap
            value = 0
            signal = 0

        # Calculate strength based on gap size relative to the day's range
        day_range = settlement_high - settlement_low
        if day_range > 0:
            strength = abs(gap_size) / day_range
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
                'settlement_date': settlement_date,
                'prev_close': prev_close,
                'settlement_open': settlement_open,
                'gap_size': gap_size,
                'gap_pct': gap_pct,
                'day_range': day_range,
                'is_gap_up': gap_size > 0,
                'gap_ratio': strength
            }
        )

    def __str__(self):
        invert_str = " (Inverted)" if self.invert else ""
        return f"{self.name}{invert_str}"
