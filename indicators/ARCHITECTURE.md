# Indicator System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TaiwanFuturesBacktest                        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ run_backtest()                                            │ │
│  │                                                           │ │
│  │  For each settlement date:                               │ │
│  │    1. Get market data                                    │ │
│  │    2. Call: indicator.calculate()  ←──────────┐          │ │
│  │    3. Receive: IndicatorResult     │          │          │ │
│  │    4. Execute trade based on signal           │          │ │
│  │    5. Record results                          │          │ │
│  └───────────────────────────────────────────────┼──────────┘ │
└────────────────────────────────────────────────────┼────────────┘
                                                     │
                                                     │
                  ┌──────────────────────────────────┼──────────┐
                  │         Indicator Interface      │          │
                  │                                  ▼          │
                  │     ┌──────────────────────────────────┐   │
                  │     │  TrendIndicator (Base Class)     │   │
                  │     │  - calculate() → IndicatorResult│   │
                  │     └──────────────────────────────────┘   │
                  │                       │                     │
                  │        ┌──────────────┼──────────────┐     │
                  │        │              │              │     │
                  │        ▼              ▼              ▼     │
                  │  ┌─────────┐   ┌─────────┐   ┌─────────┐ │
                  │  │ Price   │   │ Moving  │   │Momentum │ │
                  │  │  Diff   │   │ Average │   │         │ │
                  │  └─────────┘   └─────────┘   └─────────┘ │
                  │                                            │
                  │              ▼                             │
                  │       ┌──────────────┐                     │
                  │       │  Indicator   │                     │
                  │       │  Combiner    │                     │
                  │       │              │                     │
                  │       │ - ALL_AGREE  │                     │
                  │       │ - MAJORITY   │                     │
                  │       │ - WEIGHTED   │                     │
                  │       │ - ANY_SIGNAL │                     │
                  │       └──────────────┘                     │
                  └────────────────────────────────────────────┘
```

## Data Flow

### 1. Single Indicator Flow

```
Market Data → PriceDifferenceIndicator → IndicatorResult → Trade Decision
              - opening_price              - value: 91.0
              - prev_close                 - signal: 1 (long)
              - calculates difference      - strength: 0.009
```

### 2. Combined Indicator Flow (Weighted)

```
                                      ┌──→ PriceDifferenceIndicator
                                      │    Result: signal=1, strength=0.009, weight=0.5
                                      │
Market Data → IndicatorCombiner  ─────┼──→ MovingAverageIndicator (period=5)
                                      │    Result: signal=1, strength=0.002, weight=0.3
                                      │
                                      └──→ MomentumIndicator (period=5)
                                           Result: signal=-1, strength=0.001, weight=0.2

                                      ↓
                          Weighted Sum Calculation:
                          (1 × 0.009 × 0.5) + (1 × 0.002 × 0.3) + (-1 × 0.001 × 0.2)
                          = 0.0045 + 0.0006 - 0.0002 = 0.0049
                                      ↓
                          Combined IndicatorResult:
                          - value: weighted average of values
                          - signal: 1 (positive weighted sum → long)
                          - strength: min(|0.0049|, 1.0) = 0.0049
```

## Class Hierarchy

```
TrendIndicator (ABC)
│
├── PriceDifferenceIndicator
│   └── calculate() → prev_close - opening_price
│
├── MovingAverageIndicator
│   └── calculate() → current_price - MA(period)
│
├── MomentumIndicator
│   └── calculate() → current_price - price[t-period]
│
└── IndicatorCombiner (also a TrendIndicator!)
    ├── indicators: List[(TrendIndicator, weight)]
    ├── mode: CombinationMode
    │
    └── calculate()
        ├─→ calls each indicator.calculate()
        └─→ combines results based on mode
```

## Combination Modes Explained

### ALL_AGREE Mode
```
Indicators:  [Long, Long, Long]  → Signal: Long  ✓
Indicators:  [Long, Long, Short] → Signal: No Trade ✗
Indicators:  [Short, Short]      → Signal: Short ✓
```

### MAJORITY Mode
```
Indicators:  [Long, Long, Long, Short, Short] → 3 Long, 2 Short → Signal: Long
Indicators:  [Long, Long, Short, Short]       → 2 Long, 2 Short → Signal: No Trade
Indicators:  [Long, Short, Neutral]           → No majority → Signal: No Trade
```

### WEIGHTED Mode
```
Indicator A: signal=1,  strength=0.8, weight=0.5 → 1 × 0.8 × 0.5 = 0.40
Indicator B: signal=1,  strength=0.6, weight=0.3 → 1 × 0.6 × 0.3 = 0.18
Indicator C: signal=-1, strength=0.4, weight=0.2 → -1 × 0.4 × 0.2 = -0.08
                                                    ──────────────────────
Weighted Sum = 0.40 + 0.18 - 0.08 = 0.50 > 0 → Signal: Long
```

### ANY_SIGNAL Mode
```
Indicators:  [No Trade, No Trade, Long]  → Signal: Long  (first non-zero)
Indicators:  [No Trade, Short, Long]     → Signal: Short (first non-zero)
Indicators:  [No Trade, No Trade]        → Signal: No Trade
```

## IndicatorResult Structure

```python
@dataclass
class IndicatorResult:
    value: float         # Raw indicator calculation
    signal: int          # -1 (short), 0 (no trade), 1 (long)
    strength: float      # 0.0 to 1.0 (confidence)
    metadata: dict       # Additional diagnostic info

# Example:
IndicatorResult(
    value=91.0,
    signal=1,
    strength=0.009,
    metadata={
        'opening_price': 10200,
        'prev_close': 10291,
        'opening_date': '2017-05-18',
        'settlement_date': '2017-05-24'
    }
)
```

## Integration Points

### 1. Backtester Constructor
```python
class TaiwanFuturesBacktest:
    def __init__(self, ..., trend_indicator=None):
        if trend_indicator is None:
            # Default to original behavior
            self.trend_indicator = PriceDifferenceIndicator(
                opening_price_calc=opening_price_calc,
                prev_close_calc=prev_close_calc
            )
        else:
            # Use custom indicator
            self.trend_indicator = trend_indicator
```

### 2. Backtest Loop
```python
def run_backtest(self):
    for settlement_date in self.settlement_dates:
        # ... setup ...

        # Calculate indicator (NEW)
        indicator_result = self.trend_indicator.calculate(
            opening_date=opening_date,
            settlement_date=settlement_date,
            data=self.data
        )

        # Use signal for trade direction (NEW)
        if indicator_result.signal == 1:
            direction = 'long'
        elif indicator_result.signal == -1:
            direction = 'short'
        else:
            direction = 'no_trade'

        # Store results with new fields (NEW)
        result = {
            'trend_indicator': indicator_result.value,
            'trend_signal': indicator_result.signal,
            'trend_strength': indicator_result.strength,
            'direction': direction,
            # ... other fields ...
        }
```

## Extensibility

### Adding a New Indicator

```python
# Step 1: Create class inheriting from TrendIndicator
from indicators.base import TrendIndicator, IndicatorResult
import pandas as pd

class RSIIndicator(TrendIndicator):
    def __init__(self, name="RSI", period=14, oversold=30, overbought=70):
        super().__init__(name)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    # Step 2: Implement calculate() method
    def calculate(self, opening_date, settlement_date, data, **kwargs):
        # Calculate RSI
        rsi_value = self._calculate_rsi(data, settlement_date)

        # Generate signal
        if rsi_value < self.oversold:
            signal = 1  # Oversold → Long
        elif rsi_value > self.overbought:
            signal = -1  # Overbought → Short
        else:
            signal = 0  # Neutral

        # Calculate strength
        if signal == 1:
            strength = (self.oversold - rsi_value) / self.oversold
        elif signal == -1:
            strength = (rsi_value - self.overbought) / (100 - self.overbought)
        else:
            strength = 0

        return IndicatorResult(
            value=rsi_value,
            signal=signal,
            strength=min(abs(strength), 1.0),
            metadata={'period': self.period}
        )

    def _calculate_rsi(self, data, settlement_date):
        # RSI calculation logic
        pass

# Step 3: Use it
backtester = TaiwanFuturesBacktest(
    trend_indicator=RSIIndicator(period=14)
)
```

## Performance Flow

```
Backtest Request
    ↓
Load Data (once)
    ↓
For each settlement date (426 dates):
    ↓
    Calculate Indicator (1ms - 10ms per indicator)
    ├─ Single indicator: ~1ms
    └─ Combined (3 indicators): ~3ms
    ↓
    Determine Direction
    ↓
    Calculate P&L
    ↓
    Store Result
    ↓
Generate Report
```

**Total time**: Similar to original (indicator calculation is minimal overhead)

## Error Handling

```
try:
    indicator_result = self.trend_indicator.calculate(...)
except Exception as e:
    print(f'Error calculating indicator: {e}')
    continue  # Skip this settlement date
```

Indicators should handle their own edge cases:
- Not enough data → return signal=0
- Invalid data → return signal=0
- Calculation error → raise exception with clear message

## Summary

The architecture provides:
1. **Clear separation of concerns**: Indicators calculate, backtester executes
2. **Extensibility**: Easy to add new indicators
3. **Composability**: Indicators can be combined
4. **Testability**: Each component can be tested independently
5. **Backward compatibility**: Default behavior matches original system
