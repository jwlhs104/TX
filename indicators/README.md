# Trend Indicators Framework

The indicator framework allows you to use multiple trend indicators (individually or combined) to determine trade direction in the Taiwan Futures backtest system.

## Overview

Instead of relying solely on a single trend indicator (the original `prev_close - opening_price`), you can now:

1. **Use different individual indicators** (Moving Average, Momentum, Price Difference, etc.)
2. **Combine multiple indicators** using various strategies (ALL_AGREE, MAJORITY, WEIGHTED, etc.)
3. **Create custom indicators** by extending the base `TrendIndicator` class

## Architecture

### Base Classes

#### `TrendIndicator`
Abstract base class for all trend indicators. Each indicator must implement:
- `calculate(opening_date, settlement_date, data, **kwargs)` -> `IndicatorResult`

#### `IndicatorResult`
Data class containing:
- `value`: The calculated indicator value (float)
- `signal`: Trading signal (-1 for short, 0 for no trade, 1 for long)
- `strength`: Optional signal strength (0 to 1)
- `metadata`: Optional dictionary with additional information

## Built-in Indicators

### 1. PriceDifferenceIndicator

The original trend indicator from the backtest system.

```python
from indicators import PriceDifferenceIndicator

indicator = PriceDifferenceIndicator(
    name="PriceDiff",
    opening_price_calc="standard",  # or "night"
    prev_close_calc="standard"       # or "night", "settlement_open"
)
```

**Signal Logic:**
- `prev_close > opening_price` → Long (signal = 1)
- `prev_close < opening_price` → Short (signal = -1)
- `prev_close == opening_price` → No trade (signal = 0)

### 2. MovingAverageIndicator

Determines trend based on price position relative to its moving average.

```python
from indicators import MovingAverageIndicator

indicator = MovingAverageIndicator(
    name="MA5",
    period=5,              # Number of periods for MA
    price_type="close"     # "open", "close", "high", or "low"
)
```

**Signal Logic:**
- `current_price > MA` → Long (signal = 1)
- `current_price < MA` → Short (signal = -1)
- `current_price == MA` → No trade (signal = 0)

### 3. MomentumIndicator

Calculates price momentum over a period.

```python
from indicators import MomentumIndicator

indicator = MomentumIndicator(
    name="Momentum5",
    period=5,              # Look-back period
    price_type="close"     # "open", "close", "high", or "low"
)
```

**Signal Logic:**
- `current_price > price_N_periods_ago` → Long (signal = 1)
- `current_price < price_N_periods_ago` → Short (signal = -1)
- `current_price == price_N_periods_ago` → No trade (signal = 0)

## Combining Indicators

Use `IndicatorCombiner` to combine multiple indicators with different strategies.

### Combination Modes

#### 1. ALL_AGREE
All indicators must agree on the signal direction.

```python
from indicators import IndicatorCombiner, CombinationMode, PriceDifferenceIndicator, MovingAverageIndicator

combined = IndicatorCombiner(
    indicators=[
        (PriceDifferenceIndicator(), 1.0),
        (MovingAverageIndicator(period=5), 1.0),
        (MovingAverageIndicator(period=10), 1.0)
    ],
    mode=CombinationMode.ALL_AGREE,
    name="AllAgree"
)
```

**Logic:** Signal is generated only when ALL indicators agree.
- Example: If Price Diff = Long, MA5 = Long, MA10 = Long → Signal = Long
- Example: If Price Diff = Long, MA5 = Long, MA10 = Short → Signal = No Trade

#### 2. MAJORITY
Majority of indicators determine the signal.

```python
combined = IndicatorCombiner(
    indicators=[
        (PriceDifferenceIndicator(), 1.0),
        (MovingAverageIndicator(period=5), 1.0),
        (MovingAverageIndicator(period=10), 1.0),
        (MomentumIndicator(period=5), 1.0),
        (MomentumIndicator(period=10), 1.0)
    ],
    mode=CombinationMode.MAJORITY,
    name="Majority"
)
```

**Logic:** The signal with the most votes wins.
- Example: 3 Long, 2 Short → Signal = Long
- Example: 2 Long, 2 Short, 1 Neutral → Signal = No Trade (no clear majority)

#### 3. WEIGHTED
Weighted combination based on indicator strength and weights.

```python
combined = IndicatorCombiner(
    indicators=[
        (PriceDifferenceIndicator(), 0.5),    # 50% weight
        (MovingAverageIndicator(period=5), 0.3),   # 30% weight
        (MomentumIndicator(period=5), 0.2)         # 20% weight
    ],
    mode=CombinationMode.WEIGHTED,
    name="Weighted"
)
```

**Logic:** Weighted sum of (signal × strength × weight).
- Positive sum → Long
- Negative sum → Short
- Zero sum → No Trade

Weights are automatically normalized to sum to 1.0.

#### 4. ANY_SIGNAL
Any indicator with a non-zero signal triggers it.

```python
combined = IndicatorCombiner(
    indicators=[
        (PriceDifferenceIndicator(), 1.0),
        (MovingAverageIndicator(period=5), 1.0)
    ],
    mode=CombinationMode.ANY_SIGNAL,
    name="AnySignal"
)
```

**Logic:** First non-zero signal is used (OR logic).

## Using Indicators in Backtesting

### Basic Usage

```python
from taiwan_futures_backtest import TaiwanFuturesBacktest
from indicators import MovingAverageIndicator

# Create your indicator
indicator = MovingAverageIndicator(period=5)

# Pass it to the backtester
backtester = TaiwanFuturesBacktest(
    start_date='2017-05-16',
    end_date='2024-12-31',
    counting_period='weekly',
    trend_indicator=indicator  # Pass your custom indicator
)

# Run the backtest
backtester.get_taiwan_futures_data()
backtester.calculate_settlement_dates()
backtester.run_backtest()
backtester.generate_report()
```

### Default Behavior

If you don't specify a `trend_indicator`, the system uses the original `PriceDifferenceIndicator`:

```python
# This uses the original indicator (backward compatible)
backtester = TaiwanFuturesBacktest(
    start_date='2017-05-16',
    end_date='2024-12-31',
    counting_period='weekly'
)
```

## Creating Custom Indicators

You can create your own indicators by extending `TrendIndicator`:

```python
from indicators.base import TrendIndicator, IndicatorResult
import pandas as pd

class MyCustomIndicator(TrendIndicator):
    def __init__(self, name="MyCustom", my_param=10):
        super().__init__(name)
        self.my_param = my_param

    def calculate(
        self,
        opening_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        data: pd.DataFrame,
        **kwargs
    ) -> IndicatorResult:
        # Your custom logic here
        # Access data, calculate your indicator value

        # Example: Simple logic
        recent_data = data[data['Date'] <= settlement_date].tail(self.my_param)
        avg_close = recent_data['Close'].mean()
        current_close = data[data['Date'] == settlement_date].iloc[0]['Close']

        value = current_close - avg_close

        # Determine signal
        if value > 0:
            signal = 1
        elif value < 0:
            signal = -1
        else:
            signal = 0

        # Calculate strength (optional)
        strength = abs(value) / avg_close if avg_close != 0 else 0
        strength = min(strength, 1.0)

        return IndicatorResult(
            value=value,
            signal=signal,
            strength=strength,
            metadata={
                'avg_close': avg_close,
                'current_close': current_close,
                'my_param': self.my_param
            }
        )
```

## Examples

See `examples/indicator_examples.py` for complete working examples including:

1. Using the original price difference indicator
2. Using moving average indicator
3. Using momentum indicator
4. Combining indicators with ALL_AGREE mode
5. Combining indicators with MAJORITY mode
6. Combining indicators with WEIGHTED mode
7. Multiple moving averages with custom weights

## Results and Analysis

When using indicators, the backtest results DataFrame includes:

- `trend_indicator`: The indicator value
- `trend_signal`: The signal (-1, 0, or 1)
- `trend_strength`: The signal strength (0 to 1)
- `direction`: The trade direction ('long', 'short', or 'no_trade')

All existing filter analysis and reporting functions continue to work with the new indicator system.

## Best Practices

1. **Start simple**: Test individual indicators first before combining
2. **Validate indicators**: Check indicator results on known data to ensure correctness
3. **Compare performance**: Run backtests with different indicators to compare performance
4. **Use appropriate weights**: In weighted mode, assign higher weights to more reliable indicators
5. **Consider signal strength**: Indicators with higher strength should have more influence
6. **Handle edge cases**: Ensure your indicators handle insufficient data gracefully

## Performance Considerations

- Indicators are calculated once per settlement date
- Combined indicators calculate all sub-indicators (computational cost scales with number of indicators)
- Historical data lookups are optimized using pandas operations
- For very large datasets, consider caching indicator results

## Troubleshooting

### Indicator returns no signal (signal = 0)

Possible causes:
- Not enough historical data for the indicator period
- All indicators disagree (in ALL_AGREE mode)
- No clear majority (in MAJORITY mode)
- Weighted sum equals zero (in WEIGHTED mode)

Check the `metadata` field in `IndicatorResult` for diagnostic information.

### Backtest results differ from original

If you're using `PriceDifferenceIndicator` with default parameters and getting different results:
- Ensure `opening_price_calc` and `prev_close_calc` match your original settings
- Check that the indicator is being passed correctly to the backtester

### Custom indicator not working

Common issues:
- Not returning `IndicatorResult` from `calculate()`
- Signal not in [-1, 0, 1]
- Strength not in [0, 1]
- Not handling exceptions properly

Add error handling and logging to your custom indicator's `calculate()` method.
