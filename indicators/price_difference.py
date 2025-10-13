"""
Price Difference Indicator

This is the original trend indicator: prev_close - opening_price
If the difference is positive, it signals long; if negative, it signals short.
"""

import pandas as pd
from datetime import timedelta
from .base import TrendIndicator, IndicatorResult


class PriceDifferenceIndicator(TrendIndicator):
    """
    Calculate trend based on price difference between previous close and opening price

    This is the original indicator from the backtest system.
    Positive difference (prev_close > opening_price) = Long signal
    Negative difference (prev_close < opening_price) = Short signal
    Zero difference = No trade signal
    """

    def __init__(
        self,
        name: str = "PriceDifference",
        opening_price_calc: str = "standard",
        prev_close_calc: str = "standard"
    ):
        """
        Initialize the price difference indicator

        Args:
            name: Custom name for this indicator
            opening_price_calc: Method for calculating opening price ('standard' or 'night')
            prev_close_calc: Method for calculating previous close ('standard', 'night', or 'settlement_open')
        """
        super().__init__(name)
        self.opening_price_calc = opening_price_calc
        self.prev_close_calc = prev_close_calc

    def calculate(
        self,
        opening_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        data: pd.DataFrame,
        **kwargs
    ) -> IndicatorResult:
        """
        Calculate the price difference indicator

        Args:
            opening_date: The opening date of the trading period
            settlement_date: The settlement date
            data: DataFrame with market data
            **kwargs: Not used

        Returns:
            IndicatorResult with the price difference value and trading signal
        """
        # Get opening price
        opening_price = self._get_opening_price(opening_date, data)

        # Get previous close price
        prev_close = self._get_prev_close(settlement_date, data)

        # Calculate the indicator value
        value = prev_close - opening_price

        # Determine signal
        if value > 0:
            signal = 1  # Long
        elif value < 0:
            signal = -1  # Short
        else:
            signal = 0  # No trade

        # Calculate strength based on absolute value (normalized by opening price)
        strength = abs(value) / opening_price if opening_price != 0 else 0
        # Cap strength at 1.0
        strength = min(strength, 1.0)

        return IndicatorResult(
            value=value,
            signal=signal,
            strength=strength,
            metadata={
                'opening_price': opening_price,
                'prev_close': prev_close,
                'opening_date': opening_date,
                'settlement_date': settlement_date
            }
        )

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
