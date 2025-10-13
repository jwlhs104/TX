"""
Configuration management for Taiwan Futures Backtesting System
Centralizes all file paths and configuration settings
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Data and output directories
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Create output directory structure if it doesn't exist
(OUTPUT_DIR / "results").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "reports").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "plots").mkdir(parents=True, exist_ok=True)

# Data file paths
PATHS = {
    # Input data files
    'tx_data': DATA_DIR / 'filtered_tx_all_years.csv',
    'taifex': DATA_DIR / 'taifex.csv',
    'txo_oi': DATA_DIR / 'txo_open_interest.csv',

    # Output files
    'tx_results': OUTPUT_DIR / 'results' / 'taiwan_futures_backtest_results.csv',
    'tx_report': OUTPUT_DIR / 'reports' / 'result.md',
    'tx_plots': OUTPUT_DIR / 'plots' / 'performance_analysis.png',
    'tx_analysis': OUTPUT_DIR / 'plots' / 'indicator_analysis.png',

    'txo_results': OUTPUT_DIR / 'results' / 'txo_max_pain_results.csv',
    'txo_plots': OUTPUT_DIR / 'plots' / 'txo_max_pain_analysis.png',
}

# Default configuration
DEFAULT_CONFIG = {
    'counting_period': 'weekly',
    'opening_price_calc': 'standard',
    'prev_close_calc': 'standard',
    'start_date': '2017-05-16',
    'end_date': '2024-12-31',
}

# Logging configuration
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}

def get_path(key):
    """
    Get a file path from the PATHS dictionary

    Args:
        key: Path key (e.g., 'tx_data', 'tx_results')

    Returns:
        Path object or string representation of the path
    """
    if key not in PATHS:
        raise KeyError(f"Path key '{key}' not found. Available keys: {list(PATHS.keys())}")
    return PATHS[key]

def get_path_str(key):
    """Get path as string"""
    return str(get_path(key))

def get_indicator_path(key, indicator_name=None):
    """
    Get a file path with indicator name suffix

    Args:
        key: Path key (e.g., 'tx_results', 'tx_plots')
        indicator_name: Name of the indicator to append to filename (optional)

    Returns:
        Path object with indicator name inserted before file extension
    """
    base_path = get_path(key)

    if indicator_name is None:
        return base_path

    # Sanitize indicator name for filename
    safe_name = indicator_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-'))

    # Insert indicator name before file extension
    stem = base_path.stem
    suffix = base_path.suffix
    new_name = f"{stem}_{safe_name}{suffix}"

    return base_path.parent / new_name

def get_indicator_path_str(key, indicator_name=None):
    """Get indicator path as string"""
    return str(get_indicator_path(key, indicator_name))

# Environment variable overrides (optional)
if os.getenv('TX_DATA_DIR'):
    DATA_DIR = Path(os.getenv('TX_DATA_DIR'))
if os.getenv('TX_OUTPUT_DIR'):
    OUTPUT_DIR = Path(os.getenv('TX_OUTPUT_DIR'))
