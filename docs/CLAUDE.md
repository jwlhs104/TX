# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Note**: This file is now located in `docs/CLAUDE.md`. All documentation has been organized into the `docs/` directory.

## Project Overview

Taiwan Futures (TX) and Options (TXO) backtesting and analysis system. The project analyzes settlement day patterns for Taiwan futures and validates max pain theory for Taiwan options.

## Key Commands

### Run Main Backtest
```bash
# Default parameters (weekly settlements, standard pricing)
python taiwan_futures_backtest.py

# Custom parameters
python taiwan_futures_backtest.py \
  --counting_period weekly \
  --opening_price_calc standard \
  --prev_close_calc standard \
  --start_date 2017-05-16 \
  --end_date 2024-12-31
```

### Parameter Options
- `--counting_period`: `weekly` (all settlements) or `monthly` (only monthly settlements)
- `--opening_price_calc`: `standard` (一般 regular session) or `night` (夜盤 after-hours)
- `--prev_close_calc`: `standard` (regular close), `night` (after-hours close), or `settlement_open` (settlement day open)

### Run TXO Max Pain Analysis
```bash
python txo_max_pain_backtest.py --start_date 2017-01-01 --end_date 2024-12-31
```

### Generate Comprehensive Report
```bash
python generate_report.py
```

### Calculate Max Pain from CSV
```bash
python max_pain_calculator.py
```

## Code Architecture

### Core Backtesting Engine: `taiwan_futures_backtest.py`

**Main Class**: `TaiwanFuturesBacktest`

**Strategy Logic**:
- Trend indicator = Previous day close - Opening day open
- If trend > 0: Go long; if trend < 0: Go short
- Entry: Settlement day open; Exit: Settlement day close

**Key Methods**:
- `get_taiwan_futures_data()`: Loads TX data from `/data/filtered_tx_all_years.csv`
- `calculate_settlement_dates()`: Loads settlement dates from `/data/taifex.csv` (preferred) or calculates manually
- `calculate_opening_date()`: Finds first trading day after previous settlement
- `run_backtest()`: Executes full backtest with trend-following logic
- `calculate_performance_stats()`: Computes win rate, profit/loss ratio, Kelly criterion, max drawdown
- `analyze_filters()`: Performs multi-dimensional analysis (trend, candle color, open position, settlement type)
- `create_performance_plots()`: Generates 9-panel visualization dashboard
- `save_results_summary_to_md()`: Delegates to `ReportGenerator` for markdown output

**Calculation Variations**:
The system supports different calculation methods via constructor parameters:
- Opening price can use regular session or night session
- Previous close can use regular close, night close, or settlement open
- This flexibility allows testing different strategy variations

### TXO Max Pain Analysis: `txo_max_pain_backtest.py`

**Main Class**: `TXOMaxPainBacktest`

**Purpose**: Validates whether Taiwan futures are "attracted" to max pain levels on settlement days

**Key Methods**:
- `calculate_max_pain()`: Computes max pain strike price where option holders lose most money
- `run_max_pain_analysis()`: Compares settlement open vs close distance to max pain
- `calculate_statistics()`: Statistical significance testing (binomial test, p-value)
- `analyze_by_year()`: Yearly breakdown of max pain attraction rate

**Max Pain Logic**:
- For each strike price, calculate total pain = sum of all ITM option losses
- Max pain = strike price with minimum total pain
- Validation: Does closing price move closer to max pain than opening price?

### Report Generation: `report_generator.py`

**Main Class**: `ReportGenerator`

**Purpose**: Creates comprehensive markdown reports with performance statistics, filter analysis, and recommendations

**Key Method**: `save_results_summary_to_md()` - Generates detailed markdown report with:
- Overall performance stats (win rate, P&L, Kelly, max drawdown)
- Multi-dimensional filter analysis (trend, candle, opening, settlement type)
- Two-factor and three-factor combination analysis
- Strategy optimization recommendations

### Max Pain Calculator: `max_pain_calculator.py`

**Function**: `calculate_max_pain(csv_file)`

**Purpose**: Standalone utility to calculate max pain from TXO CSV data

**Logic**:
- Filters for regular trading session (一般) with non-zero open interest
- Generates strike range using 100-point intervals
- For each potential settlement price, calculates total pain across all strikes
- Returns strike with minimum total pain

## Data Files

### Required Data Structure

**TX Futures Data**: `/data/filtered_tx_all_years.csv`
- Columns: 交易日期, 交易時段, 開盤價, 最高價, 最低價, 收盤價, 成交量
- Sessions: '一般' (regular), '盤後' (after-hours)

**Settlement Dates**: `/data/taifex.csv`
- Columns: 最後結算日, 契約月份
- Contract format: YYYYMM (monthly), YYYYMMWN (weekly, e.g., 202509W1)

**TXO Options Data**: `/data/TXO_YYYYMMDD.csv` or `/data/txo_open_interest.csv`
- Columns: 交易日期, 交易時段, 履約價, 買賣權, 未沖銷契約數
- Used for max pain calculations

## Output Files

- `taiwan_futures_backtest_results.csv`: Detailed trade-by-trade records
- `result.md`: Comprehensive markdown analysis report
- `performance_analysis.png`: 9-panel visualization dashboard
- `txo_max_pain_results.csv`: Max pain analysis results
- `txo_max_pain_analysis.png`: Max pain visualization

## Important Implementation Details

### Settlement Date Calculation
The system prioritizes loading settlement dates from `taifex.csv` over manual calculation. Manual calculation (fallback) identifies Wednesdays from trading data and determines if they're the 3rd Wednesday of the month for monthly settlements.

### Price Calculation Variations
When modifying or testing strategies:
1. `opening_price_calc` affects which session's open price is used for entry
2. `prev_close_calc` affects trend indicator calculation and can dramatically change results
3. Using `settlement_open` for prev_close essentially creates a same-day open-to-close strategy

### Filter Analysis Architecture
The `analyze_filters()` method performs three levels of analysis:
1. Single-factor: Trend, candle color, opening position, settlement type
2. Two-factor combinations: Trend+candle, trend+opening, candle+opening
3. Three-factor combinations: All combinations of trend+candle+opening

This allows identifying which market conditions produce the best results.

### Performance Metrics
Key metrics follow specific formats per requirements:
- Percentages: 2 decimal places (96.8%)
- Ratios: 3 decimal places (1.303)
- Drawdowns: Shown as negative (-17%)

## Testing New Strategies

To test a new variation:
1. Modify `TaiwanFuturesBacktest.__init__()` to accept new parameters
2. Update `get_opening_price()` or `get_prev_close()` for new calculation methods
3. Add new filter conditions in `run_backtest()` result dictionary
4. Extend `analyze_filters()` to analyze new dimensions
5. Run backtest and generate report to evaluate results

## Dependencies

```bash
pip install pandas numpy yfinance matplotlib seaborn scipy
```

- `pandas`: Data manipulation and CSV handling
- `numpy`: Numerical calculations
- `yfinance`: Historical market data (fallback for sample data)
- `matplotlib` + `seaborn`: Visualization
- `scipy`: Statistical testing (binomial test for max pain)

## File Paths

All hardcoded paths use absolute paths to `/Users/johnny/Desktop/JQC/TX/`. When deploying to different environments, these need to be updated or made configurable.
