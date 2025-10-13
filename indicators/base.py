"""
Base classes for trend indicators
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass
class IndicatorResult:
    """
    Result from a trend indicator calculation

    Attributes:
        value: The calculated indicator value (can be any numeric value)
        signal: Trading signal (-1 for short, 0 for no trade, 1 for long)
        strength: Signal strength (0 to 1), optional
        metadata: Additional metadata about the calculation
    """
    value: float
    signal: int  # -1 (short), 0 (no trade), 1 (long)
    strength: Optional[float] = None  # 0 to 1
    metadata: Optional[dict] = None

    def __post_init__(self):
        """Validate the indicator result"""
        if self.signal not in [-1, 0, 1]:
            raise ValueError(f"Signal must be -1, 0, or 1, got {self.signal}")

        if self.strength is not None:
            if not 0 <= self.strength <= 1:
                raise ValueError(f"Strength must be between 0 and 1, got {self.strength}")


class TrendIndicator(ABC):
    """
    Base class for all trend indicators

    Each indicator calculates a value and determines a trading signal
    (long, short, or no trade) based on market data.
    """

    def __init__(self, name: str = None):
        """
        Initialize the indicator

        Args:
            name: Optional custom name for the indicator
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    def calculate(
        self,
        opening_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        data: pd.DataFrame,
        **kwargs
    ) -> IndicatorResult:
        """
        Calculate the indicator value and determine trading signal

        Args:
            opening_date: The opening date of the trading period
            settlement_date: The settlement date
            data: DataFrame with market data (columns: Date, Open, High, Low, Close, Volume, Type)
            **kwargs: Additional parameters specific to each indicator

        Returns:
            IndicatorResult with value, signal, and optional strength/metadata
        """
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"
