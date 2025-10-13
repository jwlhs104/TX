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
    ADAPTIVE_QUADRANT: Adaptive strategy based on historical performance of each quadrant
                       (2 indicators = 4 quadrants, 3 = 8, 4 = 16, max 5 = 32)
    """
    ALL_AGREE = "all_agree"
    MAJORITY = "majority"
    ANY_SIGNAL = "any_signal"
    WEIGHTED = "weighted"
    ADAPTIVE_QUADRANT = "adaptive_quadrant"


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
        name: str = "CombinedIndicator",
        backtester=None
    ):
        """
        Initialize the indicator combiner

        Args:
            indicators: List of (indicator, weight) tuples
                       Weights are used in WEIGHTED mode, ignored in others
            mode: How to combine the indicators
            name: Custom name for this combined indicator
            backtester: TaiwanFuturesBacktest instance (required for ADAPTIVE_QUADRANT mode)
        """
        super().__init__(name)
        self.indicators = indicators
        self.mode = mode
        self.backtester = backtester

        # For adaptive quadrant mode
        self.quadrant_signals = {}  # Maps quadrant tuple to optimal signal
        self.is_trained = False

        # Validate max indicators for adaptive quadrant mode
        if mode == CombinationMode.ADAPTIVE_QUADRANT:
            if len(indicators) > 5:
                raise ValueError(f"ADAPTIVE_QUADRANT mode supports maximum 5 indicators, got {len(indicators)}")
            if len(indicators) < 2:
                raise ValueError(f"ADAPTIVE_QUADRANT mode requires at least 2 indicators, got {len(indicators)}")

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
        elif self.mode == CombinationMode.ADAPTIVE_QUADRANT:
            return self._combine_adaptive_quadrant(results, opening_date, settlement_date, data)
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

    def _combine_adaptive_quadrant(
        self,
        results: List[Tuple[IndicatorResult, float]],
        opening_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        data: pd.DataFrame
    ) -> IndicatorResult:
        """
        Adaptive strategy based on historical performance of each quadrant

        This method uses historical data to determine the optimal trading direction
        for each combination of indicator states (quadrants).

        For 2 indicators: 4 quadrants (+A+B, +A-B, -A+B, -A-B)
        For 3 indicators: 8 quadrants
        For 4 indicators: 16 quadrants
        For 5 indicators: 32 quadrants
        """
        # Train the quadrant signals if not already done
        if not self.is_trained:
            self._train_quadrant_signals(data)

        # Get current quadrant based on indicator signals
        quadrant = tuple(result.signal for result, _ in results)

        # Look up the optimal signal for this quadrant
        optimal_signal = self.quadrant_signals.get(quadrant, 0)

        # Calculate average value and strength
        avg_value = sum(r.value for r, _ in results) / len(results)
        avg_strength = sum(r.strength or 0 for r, _ in results) / len(results)

        # Get quadrant statistics if available
        quadrant_stats = self.quadrant_signals.get(f"{quadrant}_stats", {})

        return IndicatorResult(
            value=avg_value,
            signal=optimal_signal,
            strength=avg_strength,
            metadata={
                'mode': 'adaptive_quadrant',
                'quadrant': quadrant,
                'quadrant_stats': quadrant_stats,
                'individual_signals': [r.signal for r, _ in results],
                'total_quadrants': 2 ** len(self.indicators)
            }
        )

    def _train_quadrant_signals(self, data: pd.DataFrame):
        """
        Train the quadrant signals based on historical data

        This method analyzes all historical trades, groups them by their
        indicator combination state (quadrant), and determines the optimal
        trading direction for each quadrant based on cumulative returns.
        """
        if self.backtester is None:
            raise ValueError("ADAPTIVE_QUADRANT mode requires a backtester instance")

        print(f"Training adaptive quadrant strategy with {len(self.indicators)} indicators...")
        print(f"Total quadrants: {2 ** len(self.indicators)}")

        # Get settlement dates from backtester
        if not hasattr(self.backtester, 'settlement_dates') or self.backtester.settlement_dates is None:
            raise ValueError("Backtester must have settlement dates calculated")

        settlement_dates = self.backtester.settlement_dates

        # Collect historical data for all trades
        quadrant_data = {}  # Maps quadrant tuple to list of actual price changes

        for _, settlement_row in settlement_dates.iterrows():
            settlement_date = settlement_row['date']

            # Calculate opening date
            opening_date = self.backtester.calculate_opening_date(settlement_date)
            if opening_date is None:
                continue

            try:
                # Calculate each indicator for this trade
                indicator_signals = []
                for indicator, _ in self.indicators:
                    result = indicator.calculate(opening_date, settlement_date, data)
                    indicator_signals.append(result.signal)

                # Create quadrant tuple
                quadrant = tuple(indicator_signals)

                # Get actual price change on settlement day
                settlement_day_data = data[data['Date'] == settlement_date]
                if len(settlement_day_data) == 0:
                    continue

                settlement_row_data = settlement_day_data.iloc[0]
                actual_change_pct = (settlement_row_data['Close'] - settlement_row_data['Open']) / settlement_row_data['Open'] * 100

                # Store in quadrant data
                if quadrant not in quadrant_data:
                    quadrant_data[quadrant] = []
                quadrant_data[quadrant].append(actual_change_pct)

            except Exception as e:
                # Skip this trade if there's an error
                continue

        # Analyze each quadrant and determine optimal signal
        print("\nQuadrant Analysis:")
        print("=" * 80)

        for quadrant, changes in quadrant_data.items():
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
            self.quadrant_signals[quadrant] = optimal_signal

            # Store statistics
            self.quadrant_signals[f"{quadrant}_stats"] = {
                'total_change': total_change,
                'count': count,
                'avg_change': avg_change,
                'direction': direction
            }

            # Format quadrant for display
            quadrant_str = ' '.join([
                f"{ind.name}:{'+'if sig==1 else '-' if sig==-1 else '0'}"
                for (ind, _), sig in zip(self.indicators, quadrant)
            ])

            print(f"{quadrant_str:50} | Count: {count:3} | Avg: {avg_change:7.2f}% | Total: {total_change:8.2f}% | Signal: {direction}")

        print("=" * 80)
        print(f"Training complete! {len(quadrant_data)} quadrants analyzed.\n")

        self.is_trained = True

    def __str__(self):
        indicator_names = [ind.name for ind, _ in self.indicators]
        return f"{self.name}({', '.join(indicator_names)}, mode={self.mode.value})"

    def __repr__(self):
        return f"IndicatorCombiner(indicators={len(self.indicators)}, mode={self.mode.value}, name='{self.name}')"
