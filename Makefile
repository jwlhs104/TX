.PHONY: help setup install test backtest maxpain report clean lint format check

# Default target
.DEFAULT_GOAL := help

# Python interpreter
PYTHON := python3
PIP := pip

# Directories
DATA_DIR := data
OUTPUT_DIR := output
TESTS_DIR := tests

help:  ## Show this help message
	@echo "Taiwan Futures Backtesting Toolkit"
	@echo "==================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make setup       # First-time setup"
	@echo "  make backtest    # Run backtest"
	@echo "  make report      # Generate report"
	@echo "  make clean       # Clean output files"

setup:  ## Setup development environment
	@echo "Setting up environment..."
	@bash setup.sh

install:  ## Install dependencies
	@echo "Installing dependencies..."
	@$(PIP) install -r requirements.txt
	@echo "✓ Dependencies installed"

test:  ## Run unit tests
	@echo "Running tests..."
	@$(PYTHON) -m pytest $(TESTS_DIR)/ -v

backtest:  ## Run TX futures backtest (default settings)
	@echo "Running TX futures backtest..."
	@$(PYTHON) cli.py backtest

backtest-monthly:  ## Run backtest with monthly settlements only
	@echo "Running monthly settlements backtest..."
	@$(PYTHON) cli.py backtest --counting-period monthly

backtest-night:  ## Run backtest with night session pricing
	@echo "Running night session backtest..."
	@$(PYTHON) cli.py backtest --opening-price-calc night --prev-close-calc night

backtest-quick:  ## Run quick backtest without plots
	@echo "Running quick backtest..."
	@$(PYTHON) cli.py backtest --no-plots

maxpain:  ## Run TXO max pain analysis
	@echo "Running max pain analysis..."
	@$(PYTHON) cli.py maxpain

maxpain-quick:  ## Run max pain analysis without plots
	@echo "Running quick max pain analysis..."
	@$(PYTHON) cli.py maxpain --no-plots

report:  ## Generate comprehensive analysis report
	@echo "Generating comprehensive report..."
	@$(PYTHON) cli.py report

calc:  ## Calculate max pain from CSV (usage: make calc FILE=data/TXO.csv)
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify FILE=<path>"; \
		echo "Example: make calc FILE=data/TXO_20250923.csv"; \
		exit 1; \
	fi
	@echo "Calculating max pain from $(FILE)..."
	@$(PYTHON) cli.py calc $(FILE)

clean:  ## Clean output files
	@echo "Cleaning output files..."
	@rm -rf $(OUTPUT_DIR)/*
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@rm -rf *.pyc
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Output files cleaned"

clean-all: clean  ## Clean everything including virtual environment
	@echo "Cleaning virtual environment..."
	@rm -rf venv
	@echo "✓ Everything cleaned"

lint:  ## Run code linting (requires pylint)
	@echo "Running linter..."
	@$(PYTHON) -m pylint *.py --disable=C0103,C0114,C0115,C0116 || true

format:  ## Format code with black (requires black)
	@echo "Formatting code..."
	@$(PYTHON) -m black *.py || echo "Install black: pip install black"

check:  ## Check code quality
	@echo "Checking code quality..."
	@$(PYTHON) -m flake8 *.py --max-line-length=120 --ignore=E501,W503 || echo "Install flake8: pip install flake8"

data-check:  ## Check if required data files exist
	@echo "Checking data files..."
	@if [ ! -f "$(DATA_DIR)/filtered_tx_all_years.csv" ]; then \
		echo "✗ Missing: $(DATA_DIR)/filtered_tx_all_years.csv"; \
	else \
		echo "✓ Found: $(DATA_DIR)/filtered_tx_all_years.csv"; \
	fi
	@if [ ! -f "$(DATA_DIR)/taifex.csv" ]; then \
		echo "✗ Missing: $(DATA_DIR)/taifex.csv"; \
	else \
		echo "✓ Found: $(DATA_DIR)/taifex.csv"; \
	fi

init-dirs:  ## Initialize directory structure
	@echo "Creating directories..."
	@mkdir -p $(DATA_DIR)
	@mkdir -p $(OUTPUT_DIR)/results
	@mkdir -p $(OUTPUT_DIR)/reports
	@mkdir -p $(OUTPUT_DIR)/plots
	@mkdir -p $(TESTS_DIR)
	@mkdir -p logs
	@echo "✓ Directories created"

demo:  ## Run a demo backtest with sample output
	@echo "Running demo backtest..."
	@$(PYTHON) cli.py backtest --counting-period weekly --markdown
	@echo ""
	@echo "Demo complete! Check output/ directory for results."

all: clean backtest report  ## Run full analysis pipeline
	@echo ""
	@echo "================================================"
	@echo "Full analysis complete!"
	@echo "================================================"
	@echo "Results:"
	@echo "  - CSV: $(OUTPUT_DIR)/results/"
	@echo "  - Plots: $(OUTPUT_DIR)/plots/"
	@echo "  - Reports: $(OUTPUT_DIR)/reports/"

# Development shortcuts
dev-setup: setup install init-dirs  ## Complete development setup
	@echo "✓ Development environment ready!"

dev-test: clean test  ## Run tests after cleaning

dev-all: dev-test backtest report  ## Run tests and full analysis
