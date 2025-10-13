# Multi-Indicator System - Quick Start Guide

## Overview

The system now supports multiple trend indicators and combinations for determining trade direction, instead of relying on a single `prev_close - opening_price` calculation.

## Quick Examples

### 1. Using the Default (Original) Indicator

No changes needed - backward compatible:

```python
from taiwan_futures_backtest import TaiwanFuturesBacktest

backtester = TaiwanFuturesBacktest(
    start_date='2017-05-16',
    end_date='2024-12-31',
    counting_period='weekly'
)
backtester.get_taiwan_futures_data()
backtester.calculate_settlement_dates()
backtester.run_backtest()
```

### 2. Using a Moving Average Indicator

```python
from taiwan_futures_backtest import TaiwanFuturesBacktest
from indicators import MovingAverageIndicator

# Create a 5-period moving average indicator
ma5 = MovingAverageIndicator(period=5, price_type='close')

backtester = TaiwanFuturesBacktest(
    start_date='2017-05-16',
    end_date='2024-12-31',
    counting_period='weekly',
    trend_indicator=ma5  # Pass your indicator
)
backtester.get_taiwan_futures_data()
backtester.calculate_settlement_dates()
backtester.run_backtest()
```

### 3. Using a Momentum Indicator

```python
from indicators import MomentumIndicator

momentum = MomentumIndicator(period=10, price_type='close')

backtester = TaiwanFuturesBacktest(
    trend_indicator=momentum,
    # ... other parameters
)
```

### 4. Combining Multiple Indicators (Weighted)

```python
from indicators import (
    PriceDifferenceIndicator,
    MovingAverageIndicator,
    MomentumIndicator,
    IndicatorCombiner,
    CombinationMode
)

# Create individual indicators
price_diff = PriceDifferenceIndicator()
ma5 = MovingAverageIndicator(period=5)
momentum = MomentumIndicator(period=5)

# Combine with weights
combined = IndicatorCombiner(
    indicators=[
        (price_diff, 0.5),   # 50% weight
        (ma5, 0.3),          # 30% weight
        (momentum, 0.2)      # 20% weight
    ],
    mode=CombinationMode.WEIGHTED,
    name="My_Combined_Strategy"
)

backtester = TaiwanFuturesBacktest(
    trend_indicator=combined,
    # ... other parameters
)
```

### 5. All Indicators Must Agree

```python
combined = IndicatorCombiner(
    indicators=[
        (PriceDifferenceIndicator(), 1.0),
        (MovingAverageIndicator(period=5), 1.0),
        (MovingAverageIndicator(period=10), 1.0)
    ],
    mode=CombinationMode.ALL_AGREE,
    name="Conservative_Strategy"
)
```

### 6. Majority Rules

```python
combined = IndicatorCombiner(
    indicators=[
        (PriceDifferenceIndicator(), 1.0),
        (MovingAverageIndicator(period=3), 1.0),
        (MovingAverageIndicator(period=5), 1.0),
        (MovingAverageIndicator(period=10), 1.0),
        (MomentumIndicator(period=5), 1.0)
    ],
    mode=CombinationMode.MAJORITY,
    name="Majority_Strategy"
)
```

## Built-in Indicators

| Indicator | Description | Parameters |
|-----------|-------------|------------|
| `PriceDifferenceIndicator` | Original indicator: `prev_close - opening_price` | `opening_price_calc`, `prev_close_calc` |
| `MovingAverageIndicator` | Price vs Moving Average | `period` (default: 5), `price_type` ('close', 'open', etc.) |
| `MomentumIndicator` | Price momentum over period | `period` (default: 5), `price_type` |

## Combination Modes

| Mode | Description | When to Use |
|------|-------------|-------------|
| `WEIGHTED` | Weighted average by strength & weight | Fine-grained control, trust some indicators more |
| `ALL_AGREE` | All indicators must agree | Conservative, reduce false signals |
| `MAJORITY` | Majority vote wins | Democratic approach, multiple similar indicators |
| `ANY_SIGNAL` | First signal triggers | Aggressive, catch any opportunity |

## Results

The backtest results now include:

- `trend_indicator`: The indicator value
- `trend_signal`: The signal (-1=short, 0=no trade, 1=long)
- `trend_strength`: Signal strength (0 to 1)
- `direction`: Trade direction ('long', 'short', 'no_trade')

All existing analysis and filter functions work with the new system.

## Testing

Run the test suite:

```bash
python test_indicators.py
```

## More Examples

See `examples/indicator_examples.py` for complete working examples.

## Full Documentation

See `indicators/README.md` for detailed documentation including:
- How to create custom indicators
- Detailed explanation of each indicator
- Combination mode details
- Best practices
- Troubleshooting

## Migration Guide

### Before (Single Indicator)

```python
backtester = TaiwanFuturesBacktest(
    start_date='2017-05-16',
    end_date='2024-12-31',
    counting_period='weekly',
    opening_price_calc='standard',
    prev_close_calc='standard'
)
```

The system calculated `trend_indicator = prev_close - opening_price` internally.

### After (Multiple Indicators)

```python
# Option 1: Keep using the original (no code changes)
backtester = TaiwanFuturesBacktest(
    start_date='2017-05-16',
    end_date='2024-12-31',
    counting_period='weekly'
)  # Uses PriceDifferenceIndicator by default

# Option 2: Use a different indicator
from indicators import MovingAverageIndicator
ma_indicator = MovingAverageIndicator(period=5)

backtester = TaiwanFuturesBacktest(
    start_date='2017-05-16',
    end_date='2024-12-31',
    counting_period='weekly',
    trend_indicator=ma_indicator
)

# Option 3: Combine multiple indicators
from indicators import IndicatorCombiner, CombinationMode

combined = IndicatorCombiner(
    indicators=[
        (PriceDifferenceIndicator(), 0.5),
        (MovingAverageIndicator(period=5), 0.3),
        (MomentumIndicator(period=5), 0.2)
    ],
    mode=CombinationMode.WEIGHTED
)

backtester = TaiwanFuturesBacktest(
    start_date='2017-05-16',
    end_date='2024-12-31',
    counting_period='weekly',
    trend_indicator=combined
)
```

## Key Benefits

1. **Flexibility**: Use any indicator or combination
2. **Extensibility**: Easy to create custom indicators
3. **Backward Compatibility**: Existing code continues to work
4. **Better Analysis**: Compare different indicators/strategies
5. **Reduced False Signals**: Combine indicators for confirmation

## Common Use Cases

### Conservative Trading
Use `ALL_AGREE` mode to only trade when all indicators align:
```python
combined = IndicatorCombiner(
    indicators=[(ind1, 1.0), (ind2, 1.0), (ind3, 1.0)],
    mode=CombinationMode.ALL_AGREE
)
```

### Trend Following
Weight trend indicators more heavily:
```python
combined = IndicatorCombiner(
    indicators=[
        (MomentumIndicator(period=10), 0.6),
        (MovingAverageIndicator(period=20), 0.4)
    ],
    mode=CombinationMode.WEIGHTED
)
```

### Multi-Timeframe Analysis
Combine indicators with different periods:
```python
combined = IndicatorCombiner(
    indicators=[
        (MovingAverageIndicator(period=5), 0.4),   # Short-term
        (MovingAverageIndicator(period=10), 0.3),  # Medium-term
        (MovingAverageIndicator(period=20), 0.3)   # Long-term
    ],
    mode=CombinationMode.WEIGHTED
)
```

## Questions?

- Full documentation: `indicators/README.md`
- Working examples: `examples/indicator_examples.py`
- Test suite: `test_indicators.py`
