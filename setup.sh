#!/bin/bash
# Taiwan Futures Backtesting Environment Setup Script

set -e  # Exit on error

echo "================================================"
echo "Taiwan Futures Backtesting Environment Setup"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

# Check if Python 3.7+ is installed
REQUIRED_VERSION="3.7"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
    echo "Error: Python 3.7 or higher is required"
    exit 1
fi
echo "✓ Python version OK"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Create necessary directories
echo "Creating directory structure..."
mkdir -p data
mkdir -p output/results
mkdir -p output/reports
mkdir -p output/plots
mkdir -p tests
echo "✓ Directories created"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "✓ .env file created (please edit if needed)"
    fi
fi
echo ""

# Make CLI executable
if [ -f "cli.py" ]; then
    chmod +x cli.py
    echo "✓ cli.py made executable"
fi
echo ""

echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Place your data files in the data/ directory:"
echo "     - data/filtered_tx_all_years.csv"
echo "     - data/taifex.csv"
echo ""
echo "  3. Run your first backtest:"
echo "     python cli.py backtest"
echo ""
echo "  4. Or use make commands (if Makefile exists):"
echo "     make backtest"
echo ""
echo "For help:"
echo "  python cli.py --help"
echo ""
echo "Happy backtesting! 📊"
