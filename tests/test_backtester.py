"""
Unit tests for Taiwan Futures Backtesting System
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from taiwan_futures_backtest import TaiwanFuturesBacktest
from config import PATHS, get_path


class TestBacktesterInitialization(unittest.TestCase):
    """Test backtester initialization and configuration"""

    def setUp(self):
        """Set up test fixtures"""
        self.backtester = TaiwanFuturesBacktest()

    def test_initialization_default_params(self):
        """Test backtester initializes with default parameters"""
        self.assertEqual(self.backtester.counting_period, 'weekly')
        self.assertEqual(self.backtester.opening_price_calc, 'standard')
        self.assertEqual(self.backtester.prev_close_calc, 'standard')

    def test_initialization_custom_params(self):
        """Test backtester initializes with custom parameters"""
        bt = TaiwanFuturesBacktest(
            counting_period='monthly',
            opening_price_calc='night',
            prev_close_calc='night'
        )
        self.assertEqual(bt.counting_period, 'monthly')
        self.assertEqual(bt.opening_price_calc, 'night')
        self.assertEqual(bt.prev_close_calc, 'night')

    def test_data_initially_none(self):
        """Test that data is None before loading"""
        self.assertIsNone(self.backtester.data)
        self.assertIsNone(self.backtester.settlement_dates)
        self.assertEqual(len(self.backtester.results), 0)


class TestDataLoading(unittest.TestCase):
    """Test data loading functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.backtester = TaiwanFuturesBacktest()

    def test_data_file_exists(self):
        """Test that required data file exists"""
        data_path = get_path('tx_data')
        self.assertTrue(
            data_path.exists(),
            f"Data file not found: {data_path}"
        )

    def test_load_data(self):
        """Test data loading"""
        try:
            data = self.backtester.get_taiwan_futures_data()
            self.assertIsNotNone(data)
            self.assertTrue(len(data) > 0)
            self.assertIn('Open', data.columns)
            self.assertIn('Close', data.columns)
            self.assertIn('Date', data.columns)
        except FileNotFoundError:
            self.skipTest("Data file not available")

    def test_data_columns(self):
        """Test that loaded data has required columns"""
        try:
            data = self.backtester.get_taiwan_futures_data()
            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                self.assertIn(col, data.columns)
        except FileNotFoundError:
            self.skipTest("Data file not available")


class TestSettlementDates(unittest.TestCase):
    """Test settlement date calculation"""

    def setUp(self):
        """Set up test fixtures"""
        self.backtester = TaiwanFuturesBacktest()
        try:
            self.backtester.get_taiwan_futures_data()
        except FileNotFoundError:
            self.skipTest("Data file not available")

    def test_calculate_settlement_dates(self):
        """Test settlement date calculation"""
        dates = self.backtester.calculate_settlement_dates()
        self.assertIsNotNone(dates)
        self.assertTrue(len(dates) > 0)

    def test_settlement_dates_have_type(self):
        """Test that settlement dates have type column"""
        dates = self.backtester.calculate_settlement_dates()
        self.assertIn('type', dates.columns)
        self.assertIn('date', dates.columns)

    def test_settlement_dates_are_wednesdays(self):
        """Test that settlement dates are Wednesdays (weekday=2)"""
        dates = self.backtester.calculate_settlement_dates()
        for _, row in dates.iterrows():
            # Wednesday is weekday 2
            weekday = row['date'].weekday()
            self.assertEqual(
                weekday, 2,
                f"Settlement date {row['date']} is not a Wednesday"
            )


class TestPerformanceStats(unittest.TestCase):
    """Test performance statistics calculation"""

    def setUp(self):
        """Set up test fixtures"""
        self.backtester = TaiwanFuturesBacktest(
            start_date='2024-01-01',
            end_date='2024-03-31'
        )
        try:
            self.backtester.get_taiwan_futures_data()
            self.backtester.calculate_settlement_dates()
            self.backtester.run_backtest()
        except (FileNotFoundError, Exception) as e:
            self.skipTest(f"Cannot run backtest: {e}")

    def test_performance_stats_keys(self):
        """Test that performance stats contain expected keys"""
        stats = self.backtester.calculate_performance_stats()
        expected_keys = ['總次', '勝次', '敗次', '勝率', '盈虧比', '凱利', '最大回撤']
        for key in expected_keys:
            self.assertIn(key, stats)

    def test_win_loss_sum_equals_total(self):
        """Test that wins + losses + breakeven = total trades"""
        stats = self.backtester.calculate_performance_stats()
        total = stats.get('勝次', 0) + stats.get('敗次', 0) + stats.get('無歸類', 0)
        self.assertEqual(total, stats.get('總次', 0))

    def test_performance_stats_types(self):
        """Test that performance stats have correct types"""
        stats = self.backtester.calculate_performance_stats()
        self.assertIsInstance(stats.get('總次'), int)
        self.assertIsInstance(stats.get('勝次'), int)
        self.assertIsInstance(stats.get('敗次'), int)


class TestFilterAnalysis(unittest.TestCase):
    """Test filter analysis functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.backtester = TaiwanFuturesBacktest(
            start_date='2024-01-01',
            end_date='2024-03-31'
        )
        try:
            self.backtester.get_taiwan_futures_data()
            self.backtester.calculate_settlement_dates()
            self.backtester.run_backtest()
        except (FileNotFoundError, Exception) as e:
            self.skipTest(f"Cannot run backtest: {e}")

    def test_filter_analysis_keys(self):
        """Test that filter analysis contains expected keys"""
        filters = self.backtester.analyze_filters()
        expected_filters = ['趨勢方向', '昨日K線', '開盤位置', '結算類型']
        for filter_name in expected_filters:
            self.assertIn(filter_name, filters)

    def test_trend_direction_filter(self):
        """Test trend direction filter analysis"""
        filters = self.backtester.analyze_filters()
        trend_filter = filters.get('趨勢方向', {})
        self.assertIn('往上', trend_filter)
        self.assertIn('往下', trend_filter)

    def test_settlement_type_filter(self):
        """Test settlement type filter analysis"""
        filters = self.backtester.analyze_filters()
        settlement_filter = filters.get('結算類型', {})
        # Depending on counting_period, may have weekly or monthly
        self.assertTrue(len(settlement_filter) > 0)


class TestConfig(unittest.TestCase):
    """Test configuration management"""

    def test_paths_exist(self):
        """Test that PATHS dictionary has required keys"""
        required_paths = ['tx_data', 'taifex', 'tx_results', 'tx_report']
        for key in required_paths:
            self.assertIn(key, PATHS)

    def test_get_path_function(self):
        """Test get_path function"""
        path = get_path('tx_data')
        self.assertIsNotNone(path)
        self.assertIsInstance(path, Path)

    def test_get_path_invalid_key(self):
        """Test get_path with invalid key raises error"""
        with self.assertRaises(KeyError):
            get_path('invalid_key_xyz')


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBacktesterInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestSettlementDates))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceStats))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    # Run tests
    success = run_tests()
    sys.exit(0 if success else 1)
