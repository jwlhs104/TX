# Quick Start Guide

Get started with Taiwan Futures Backtesting in 5 minutes! 🚀

## 1. Initial Setup (One-time)

```bash
# Clone or navigate to the project
cd /path/to/TX

# Run setup script
bash setup.sh

# Activate virtual environment
source venv/bin/activate
```

**That's it!** The setup script handles everything:
- Creates virtual environment
- Installs dependencies
- Creates necessary directories

---

## 2. Prepare Your Data

Place your data files in the `data/` directory:

```bash
data/
├── filtered_tx_all_years.csv    # Required: TX futures OHLCV data
└── taifex.csv                   # Recommended: Settlement dates
```

Check if data files are ready:
```bash
make data-check
```

See [../data/README.md](../data/README.md) for detailed data format requirements.

---

## 3. Run Your First Backtest

### Option A: Using Makefile (Recommended)

```bash
# Run standard backtest
make backtest

# Or run specific variations
make backtest-monthly      # Monthly settlements only
make backtest-night        # Night session pricing
make backtest-quick        # Skip plots for faster results
```

### Option B: Using CLI directly

```bash
# Default settings
python cli.py backtest

# Custom parameters
python cli.py backtest --counting-period monthly --markdown
```

---

## 4. View Results

Results are saved to `output/` directory:

```
output/
├── results/
│   └── taiwan_futures_backtest_results.csv    # Detailed trade records
├── reports/
│   └── result.md                              # Analysis report
└── plots/
    └── performance_analysis.png               # Performance charts
```

---

## Common Commands

### Backtesting
```bash
make backtest              # Run standard backtest
make backtest-monthly      # Monthly settlements only
make backtest-night        # Night session pricing
```

### Max Pain Analysis
```bash
make maxpain               # Run TXO max pain analysis
make maxpain-quick         # Skip plots
```

### Reports
```bash
make report                # Generate comprehensive report
```

### Utilities
```bash
make clean                 # Clean output files
make data-check            # Verify data files
make help                  # Show all commands
```

---

## Advanced Usage

### Custom Parameters via CLI

```bash
# Run backtest with specific date range
python cli.py backtest \
  --start-date 2020-01-01 \
  --end-date 2024-12-31 \
  --counting-period monthly \
  --no-plots

# Run max pain analysis
python cli.py maxpain \
  --start-date 2023-01-01 \
  --end-date 2024-12-31

# Calculate max pain from specific CSV
python cli.py calc data/TXO_20250923.csv
```

### Using Configuration File

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` to set your preferences:
```bash
DEFAULT_COUNTING_PERIOD=monthly
START_DATE=2020-01-01
END_DATE=2024-12-31
```

---

## Full Analysis Pipeline

Run complete analysis with all steps:

```bash
make all
```

This will:
1. Clean previous results
2. Run backtest
3. Generate comprehensive report
4. Create visualizations

---

## Getting Help

### CLI Help
```bash
python cli.py --help              # Show all commands
python cli.py backtest --help     # Show backtest options
python cli.py maxpain --help      # Show max pain options
```

### Makefile Help
```bash
make help                         # Show all make commands
```

### Documentation
- [README.md](../README.md) - Project overview
- [CLAUDE.md](CLAUDE.md) - Code architecture guide
- [data/README.md](../data/README.md) - Data format documentation

---

## Troubleshooting

### Problem: "Data file not found"
**Solution**:
```bash
# Check if files exist
ls -la data/

# Verify required files
make data-check
```

### Problem: "Module not found"
**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
make install
```

### Problem: "No settlement dates found"
**Solution**: System will auto-calculate from trading data (every Wednesday). This is normal if `taifex.csv` is not available.

---

## Next Steps

1. **Customize Strategy**: Modify parameters in `.env` or use CLI flags
2. **Run Tests**: `make test` to verify everything works
3. **Explore Results**: Check `output/reports/result.md` for detailed analysis
4. **Read Documentation**: See [CLAUDE.md](CLAUDE.md) for code architecture

---

## Example Workflow

```bash
# 1. Setup (first time only)
bash setup.sh
source venv/bin/activate

# 2. Verify data
make data-check

# 3. Run quick test
make backtest-quick

# 4. Run full analysis
make all

# 5. View results
cat output/reports/result.md
open output/plots/performance_analysis.png
```

---

Happy backtesting! 📊✨

For questions or issues, check the documentation or open an issue on the repository.
