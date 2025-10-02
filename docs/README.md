# Documentation Index

Welcome to the Taiwan Futures Backtesting System documentation!

## 📚 Documentation Files

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
  - Setup instructions
  - Basic commands
  - Common workflows
  - Troubleshooting

### Features & Changes
- **[NEW_FEATURES.md](NEW_FEATURES.md)** - Overview of new developer-friendly features
  - Quick feature list
  - Usage examples
  - Comparison tables
  - Best practices

- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Detailed technical improvements
  - What changed and why
  - Before/after comparisons
  - Migration guide
  - Productivity gains

- **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - File organization changes
  - Removed files
  - Moved files
  - New structure
  - Benefits

### Technical Reference
- **[CLAUDE.md](CLAUDE.md)** - Code architecture and internal documentation
  - Core classes and methods
  - Data structures
  - Implementation details
  - Testing strategies

---

## 📖 Reading Guide

### For New Users
1. Start with [QUICKSTART.md](QUICKSTART.md) (5 minutes)
2. Browse [NEW_FEATURES.md](NEW_FEATURES.md) to see what's available
3. Check [CLAUDE.md](CLAUDE.md) when you need code details

### For Existing Users
1. Read [IMPROVEMENTS.md](IMPROVEMENTS.md) to see what changed
2. Check [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md) for file changes
3. Refer to [QUICKSTART.md](QUICKSTART.md) for new workflows

### For Developers
1. Review [CLAUDE.md](CLAUDE.md) for architecture
2. Read [IMPROVEMENTS.md](IMPROVEMENTS.md) for design decisions
3. Use [QUICKSTART.md](QUICKSTART.md) as a reference

---

## 🗂️ Other Documentation

### Data Documentation
- **[../data/README.md](../data/README.md)** - Data format specifications
  - Required data files
  - Column definitions
  - Data sources
  - Validation methods

### API Documentation
For detailed API documentation, see the docstrings in the Python files:
- `taiwan_futures_backtest.py` - Main backtesting engine
- `txo_max_pain_backtest.py` - Max pain analysis
- `config.py` - Configuration management
- `logger.py` - Logging utilities

---

## 📊 Quick Reference

### File Organization
```
docs/
├── README.md              # This file - Documentation index
├── QUICKSTART.md          # Quick start guide (start here!)
├── NEW_FEATURES.md        # Feature overview
├── IMPROVEMENTS.md        # Technical details
├── CLEANUP_SUMMARY.md     # File organization
└── CLAUDE.md              # Code architecture
```

### Common Tasks
```bash
# Get started
bash setup.sh

# Run backtest
make backtest

# Generate report
make report

# Get help
make help
python cli.py --help
```

### Key Commands
| Task | Command |
|------|---------|
| Setup environment | `bash setup.sh` |
| Run backtest | `make backtest` |
| Monthly only | `make backtest-monthly` |
| Max pain analysis | `make maxpain` |
| Generate report | `make report` |
| Run tests | `make test` |
| Clean outputs | `make clean` |
| Show help | `make help` |

---

## 🔗 External Resources

- Project Root: [../README.md](../README.md)
- Data Documentation: [../data/README.md](../data/README.md)
- Test Suite: [../tests/](../tests/)

---

## 💡 Tips

- **First time?** Read [QUICKSTART.md](QUICKSTART.md) first
- **Need help?** Check the troubleshooting sections in each doc
- **Want details?** [IMPROVEMENTS.md](IMPROVEMENTS.md) has in-depth explanations
- **Writing code?** [CLAUDE.md](CLAUDE.md) explains the architecture

---

**Last Updated**: 2025-10-02
