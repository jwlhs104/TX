"""
Indicator Combiner

Combines multiple trend indicators using different strategies
"""

from enum import Enum
from typing import List, Tuple, Optional
import pandas as pd
from .base import TrendIndicator, IndicatorResult


class CombinationMode(Enum):
    """
    Modes for combining multiple indicators

    ALL_AGREE: All indicators must agree on the signal (AND logic)
    MAJORITY: Majority of indicators determine the signal
    ANY_SIGNAL: Any indicator with a signal triggers it (OR logic)
    WEIGHTED: Weighted average of indicator signals and strengths
    """
    ALL_AGREE = "all_agree"
    MAJORITY = "majority"
    ANY_SIGNAL = "any_signal"
    WEIGHTED = "weighted"


class IndicatorCombiner(TrendIndicator):
    """
    Combines multiple trend indicators into a single signal

    This allows for sophisticated multi-indicator strategies where
    trade direction is determined by a combination of indicators.
    """

    def __init__(
        self,
        indicators: List[Tuple[TrendIndicator, float]],
        mode: CombinationMode = CombinationMode.WEIGHTED,
        name: str = "CombinedIndicator"
    ):
        """
        Initialize the indicator combiner

        Args:
            indicators: List of (indicator, weight) tuples
                       Weights are used in WEIGHTED mode, ignored in others
            mode: How to combine the indicators
            name: Custom name for this combined indicator
        """
        super().__init__(name)
        self.indicators = indicators
        self.mode = mode

        # Normalize weights if using weighted mode
        if mode == CombinationMode.WEIGHTED:
            total_weight = sum(weight for _, weight in indicators)
            if total_weight == 0:
                raise ValueError("Total weight cannot be zero in weighted mode")
            self.indicators = [
                (ind, weight / total_weight)
                for ind, weight in indicators
            ]

    def calculate(
        self,
        opening_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        data: pd.DataFrame,
        **kwargs
    ) -> IndicatorResult:
        """
        Calculate the combined indicator

        Args:
            opening_date: The opening date of the trading period
            settlement_date: The settlement date
            data: DataFrame with market data
            **kwargs: Additional parameters passed to individual indicators

        Returns:
            IndicatorResult with combined signal
        """
        # Calculate all individual indicators
        results = []
        for indicator, weight in self.indicators:
            try:
                result = indicator.calculate(opening_date, settlement_date, data, **kwargs)
                results.append((result, weight))
            except Exception as e:
                # If an indicator fails, record it but continue
                results.append((
                    IndicatorResult(
                        value=0,
                        signal=0,
                        strength=0,
                        metadata={'error': str(e), 'indicator': str(indicator)}
                    ),
                    weight
                ))

        # Combine results based on mode
        if self.mode == CombinationMode.ALL_AGREE:
            return self._combine_all_agree(results)
        elif self.mode == CombinationMode.MAJORITY:
            return self._combine_majority(results)
        elif self.mode == CombinationMode.ANY_SIGNAL:
            return self._combine_any_signal(results)
        elif self.mode == CombinationMode.WEIGHTED:
            return self._combine_weighted(results)
        else:
            raise ValueError(f"Unsupported combination mode: {self.mode}")

    def _combine_all_agree(
        self,
        results: List[Tuple[IndicatorResult, float]]
    ) -> IndicatorResult:
        """All indicators must agree on the signal"""
        signals = [result.signal for result, _ in results]

        # Check if all non-zero signals agree
        non_zero_signals = [s for s in signals if s != 0]

        if len(non_zero_signals) == 0:
            # All signals are zero
            combined_signal = 0
        elif all(s == non_zero_signals[0] for s in non_zero_signals):
            # All non-zero signals agree
            combined_signal = non_zero_signals[0]
        else:
            # Signals disagree
            combined_signal = 0

        # Calculate average strength and value
        avg_strength = sum(r.strength or 0 for r, _ in results) / len(results)
        avg_value = sum(r.value for r, _ in results) / len(results)

        return IndicatorResult(
            value=avg_value,
            signal=combined_signal,
            strength=avg_strength,
            metadata={
                'mode': 'all_agree',
                'individual_signals': signals,
                'individual_results': [r.metadata for r, _ in results]
            }
        )

    def _combine_majority(
        self,
        results: List[Tuple[IndicatorResult, float]]
    ) -> IndicatorResult:
        """Majority of indicators determine the signal"""
        signals = [result.signal for result, _ in results]

        # Count votes
        long_votes = signals.count(1)
        short_votes = signals.count(-1)
        neutral_votes = signals.count(0)

        # Determine majority
        if long_votes > short_votes and long_votes > neutral_votes:
            combined_signal = 1
        elif short_votes > long_votes and short_votes > neutral_votes:
            combined_signal = -1
        else:
            combined_signal = 0

        # Calculate average strength and value
        avg_strength = sum(r.strength or 0 for r, _ in results) / len(results)
        avg_value = sum(r.value for r, _ in results) / len(results)

        return IndicatorResult(
            value=avg_value,
            signal=combined_signal,
            strength=avg_strength,
            metadata={
                'mode': 'majority',
                'long_votes': long_votes,
                'short_votes': short_votes,
                'neutral_votes': neutral_votes,
                'individual_signals': signals
            }
        )

    def _combine_any_signal(
        self,
        results: List[Tuple[IndicatorResult, float]]
    ) -> IndicatorResult:
        """Any indicator with a signal triggers it (OR logic)"""
        signals = [result.signal for result, _ in results]

        # If any signal is non-zero, use the first non-zero signal
        combined_signal = 0
        for signal in signals:
            if signal != 0:
                combined_signal = signal
                break

        # Calculate average strength and value
        avg_strength = sum(r.strength or 0 for r, _ in results) / len(results)
        avg_value = sum(r.value for r, _ in results) / len(results)

        return IndicatorResult(
            value=avg_value,
            signal=combined_signal,
            strength=avg_strength,
            metadata={
                'mode': 'any_signal',
                'individual_signals': signals
            }
        )

    def _combine_weighted(
        self,
        results: List[Tuple[IndicatorResult, float]]
    ) -> IndicatorResult:
        """Weighted average of indicator signals and strengths"""
        # Calculate weighted signal
        weighted_signal = sum(
            result.signal * (result.strength or 1.0) * weight
            for result, weight in results
        )

        # Determine final signal based on weighted sum
        if weighted_signal > 0:
            combined_signal = 1
        elif weighted_signal < 0:
            combined_signal = -1
        else:
            combined_signal = 0

        # Calculate weighted strength (absolute value of weighted signal, capped at 1)
        combined_strength = min(abs(weighted_signal), 1.0)

        # Calculate weighted value
        weighted_value = sum(result.value * weight for result, weight in results)

        return IndicatorResult(
            value=weighted_value,
            signal=combined_signal,
            strength=combined_strength,
            metadata={
                'mode': 'weighted',
                'weighted_signal': weighted_signal,
                'individual_signals': [r.signal for r, _ in results],
                'individual_weights': [w for _, w in results]
            }
        )

    def __str__(self):
        indicator_names = [ind.name for ind, _ in self.indicators]
        return f"{self.name}({', '.join(indicator_names)}, mode={self.mode.value})"

    def __repr__(self):
        return f"IndicatorCombiner(indicators={len(self.indicators)}, mode={self.mode.value}, name='{self.name}')"
