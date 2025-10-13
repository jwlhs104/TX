"""
Momentum Indicator

Calculates momentum over a period to determine trend direction
"""

import pandas as pd
from datetime import timedelta
from .base import TrendIndicator, IndicatorResult


class MomentumIndicator(TrendIndicator):
    """
    Calculate trend based on price momentum over a period

    Momentum = Current Price - Price N periods ago
    Positive momentum = Long signal
    Negative momentum = Short signal
    """

    def __init__(
        self,
        name: str = "Momentum",
        period: int = 5,
        price_type: str = "close"
    ):
        """
        Initialize the momentum indicator

        Args:
            name: Custom name for this indicator
            period: Number of periods to look back (default: 5)
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
        Calculate the momentum indicator

        Args:
            opening_date: The opening date of the trading period
            settlement_date: The settlement date
            data: DataFrame with market data
            **kwargs: Not used

        Returns:
            IndicatorResult with momentum value and trading signal
        """
        # Get previous day (day before settlement)
        prev_day = settlement_date - timedelta(days=1)
        while not (data['Date'] == prev_day).any() and prev_day >= opening_date:
            prev_day -= timedelta(days=1)

        # Get data up to and including previous day (一般 session only)
        historical_data = data[
            (data['Date'] <= prev_day) &
            (data['Type'] == '一般')
        ].sort_values('Date')

        if len(historical_data) <= self.period:
            # Not enough data, return neutral signal
            return IndicatorResult(
                value=0,
                signal=0,
                strength=0,
                metadata={
                    'error': f'Not enough data for momentum calculation (need {self.period + 1}, have {len(historical_data)})'
                }
            )

        # Get current price and price N periods ago
        current_price = historical_data.iloc[-1][self.price_type]
        past_price = historical_data.iloc[-(self.period + 1)][self.price_type]

        # Calculate momentum
        value = current_price - past_price

        # Determine signal
        if value > 0:
            signal = 1  # Long (positive momentum)
        elif value < 0:
            signal = -1  # Short (negative momentum)
        else:
            signal = 0  # No trade

        # Calculate strength based on percentage change
        strength = abs(value) / past_price if past_price != 0 else 0
        strength = min(strength, 1.0)  # Cap at 1.0

        return IndicatorResult(
            value=value,
            signal=signal,
            strength=strength,
            metadata={
                'current_price': current_price,
                'past_price': past_price,
                'period': self.period,
                'price_type': self.price_type
            }
        )
