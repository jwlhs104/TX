"""
Logging configuration for Taiwan Futures Backtesting System
Provides centralized logging with consistent formatting
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname:8s}"
                f"{self.RESET}"
            )
        return super().format(record)


def setup_logger(
    name='tx_backtest',
    level=logging.INFO,
    log_to_file=False,
    log_dir='logs'
):
    """
    Setup and configure logger

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to also log to file
        log_dir: Directory for log files (if log_to_file=True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        log_filename = log_path / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(level)

        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {log_filename}")

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name='tx_backtest'):
    """
    Get an existing logger or create a new one

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        logger = setup_logger(name)

    return logger


# Pre-configured loggers for different modules
def get_backtester_logger():
    """Get logger for backtesting module"""
    return get_logger('tx_backtest')


def get_maxpain_logger():
    """Get logger for max pain module"""
    return get_logger('txo_maxpain')


def get_reporter_logger():
    """Get logger for reporting module"""
    return get_logger('tx_reporter')


# Example usage
if __name__ == "__main__":
    # Demo different log levels
    logger = setup_logger('demo', level=logging.DEBUG, log_to_file=True)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    print("\n--- Testing different loggers ---")
    bt_logger = get_backtester_logger()
    bt_logger.info("Backtester logger initialized")

    mp_logger = get_maxpain_logger()
    mp_logger.info("Max pain logger initialized")

    rp_logger = get_reporter_logger()
    rp_logger.info("Reporter logger initialized")
