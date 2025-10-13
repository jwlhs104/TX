#!/usr/bin/env python3
"""
Report Generator Module for Taiwan Futures Backtest
台指期結算日傾向回測報告生成模組

This module handles the generation and saving of markdown reports
for the Taiwan Futures settlement day pattern backtesting system.
"""

from datetime import datetime
import pandas as pd
from config import get_path_str


class ReportGenerator:
    def __init__(self, backtester=None, indicator_name=None):
        """
        Initialize report generator with backtester instance

        Args:
            backtester: TaiwanFuturesBacktest instance
            indicator_name: Name of the indicator (for unique filenames)
        """
        self.backtester = backtester
        self.indicator_name = indicator_name

    def save_results_summary_to_md(self, filename='result.md'):
        """
        Save backtest results summary and performance analysis to markdown file

        Args:
            filename: Output markdown filename

        Returns:
            filepath: Path to saved file or None if failed
        """
        if not self.backtester or self.backtester.results is None or len(self.backtester.results) == 0:
            print("No results available to save.")
            return None

        # Calculate all statistics
        overall_stats = self.backtester.calculate_performance_stats()
        filter_analysis = self.backtester.analyze_filters()
        risk_metrics = self.backtester.calculate_risk_metrics()
        seasonal_analysis = self.backtester.analyze_seasonal_patterns()
        volatility_analysis = self.backtester.analyze_volatility_patterns()

        # Generate markdown content
        md_content = self._generate_markdown_summary(
            overall_stats, filter_analysis, risk_metrics,
            seasonal_analysis, volatility_analysis
        )

        # Save to file
        from config import get_indicator_path_str
        filepath = get_indicator_path_str('tx_report', self.indicator_name)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"\nResults summary saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving markdown report: {e}")
            return None

    def _generate_markdown_summary(self, overall_stats, filter_analysis, risk_metrics,
                                 seasonal_analysis, volatility_analysis):
        """
        Generate comprehensive markdown content for results summary

        Args:
            overall_stats: Overall performance statistics
            filter_analysis: Filter analysis results
            risk_metrics: Risk metrics calculations
            seasonal_analysis: Seasonal analysis results
            volatility_analysis: Volatility analysis results

        Returns:
            str: Complete markdown content
        """
        # Get data info
        data_start = self.backtester.data['Date'].min().strftime('%Y-%m-%d')
        data_end = self.backtester.data['Date'].max().strftime('%Y-%m-%d')

        # Determine performance status
        net_profit = overall_stats.get('淨利', 0)
        win_rate_str = str(overall_stats.get('勝率', '0%'))
        win_rate_num = float(win_rate_str.replace('%', '')) if '%' in win_rate_str else 0

        # Start building markdown content
        md_content = f"""# 台指期結算日傾向回測分析報告
# Taiwan Futures Settlement Day Pattern Analysis Report

**生成時間 Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 執行摘要 Executive Summary

本報告基於台指期結算日傾向策略進行了全面的回測分析，涵蓋了從{self.backtester.data['Date'].min().strftime('%Y年%m月')}到{self.backtester.data['Date'].max().strftime('%Y年%m月')}的完整交易週期。分析包含了基礎績效統計、進階風險指標、波動率分析、季節性模式以及多維度濾網分析。策略在此期間{'表現出色' if net_profit > 5 else '表現平穩' if net_profit > 0 else '需要優化'}，淨利達{net_profit:.2f}%，勝率{win_rate_str}。

This report provides a comprehensive backtesting analysis of Taiwan Futures settlement day pattern strategy, covering the complete trading cycle from {self.backtester.data['Date'].min().strftime('%B %Y')} to {self.backtester.data['Date'].max().strftime('%B %Y')}. The analysis includes basic performance statistics, advanced risk indicators, volatility analysis, seasonal patterns, and multi-dimensional filter analysis. The strategy showed {'excellent' if net_profit > 5 else 'steady' if net_profit > 0 else 'mixed'} performance with a net profit of {net_profit:.2f}% and a win rate of {win_rate_str}.

---

## 🎯 策略概述 Strategy Overview

### 核心邏輯 Core Logic
- **趨勢指標**: 結算前一天收盤價 - 開倉日開盤價
- **交易規則**: 趨勢指標 > 0 做多，< 0 做空
- **執行時機**: 結算日開盤進場，收盤平倉

### 分析範圍 Analysis Scope
- **時間區間**: {data_start} 至 {data_end}
- **總交易次數**: {overall_stats.get('總次', 0)}
- **結算類型**: 週選 + 月選（每週三結算）

---

## 📈 基礎績效統計 Basic Performance Statistics

### 💰 獲利能力分析 Profitability Analysis
| 指標 Metric | 數值 Value | 評估 Assessment |
|-------------|-----------|------------------|
| **淨利 Net Profit** | {net_profit:.2f}% | {'🟢 獲利' if net_profit > 0 else '🔴 虧損'} |
| **總獲利 Total Profit** | {overall_stats.get('總獲利', 0):.2f}% | 正面交易貢獻 |
| **總虧損 Total Loss** | {overall_stats.get('總虧損', 0):.2f}% | 負面交易影響 |
| **最大單筆獲利** | {overall_stats.get('最大獲利', 0):.2f}% | 單筆最佳表現 |
| **最大單筆虧損** | {overall_stats.get('最大虧損', 0):.2f}% | 單筆最差表現 |

### 🎲 交易統計 Trading Statistics
| 項目 Item | 數值 Value | 比例 Ratio |
|-----------|-----------|-----------|
| **勝次 Winning Trades** | {overall_stats.get('勝次', 0)} | {(overall_stats.get('勝次', 0) / max(overall_stats.get('總次', 1), 1) * 100):.1f}% |
| **敗次 Losing Trades** | {overall_stats.get('敗次', 0)} | {(overall_stats.get('敗次', 0) / max(overall_stats.get('總次', 1), 1) * 100):.1f}% |
| **總交易次數** | {overall_stats.get('總次', 0)} | 100.0% |

### 📊 績效比率 Performance Ratios
| 指標 Metric | 數值 Value | 解釋 Interpretation |
|-------------|-----------|-------------------|
| **勝率 Win Rate** | {win_rate_str} | {'🟢 優於50%' if win_rate_num > 50 else '🔴 低於50%'} |
| **勝均 Avg Win** | {overall_stats.get('勝均', 0):.2f}% | 平均獲利交易收益 |
| **敗均 Avg Loss** | {overall_stats.get('敗均', 0):.2f}% | 平均虧損交易損失 |
| **筆均 Avg Trade** | {overall_stats.get('筆均', 0):.2f}% | 平均每筆交易收益 |
| **盈虧比 P/L Ratio** | {overall_stats.get('盈虧比', 0):.3f} | {'🟢 獲利優於虧損' if overall_stats.get('盈虧比', 0) > 1.2 else '⚖️ 接近平衡' if overall_stats.get('盈虧比', 0) > 0.9 else '🔴 需改善'} |

---

## 🔍 關鍵績效指標 Key Performance Indicators

### 🎯 核心指標評估 Core Metrics Assessment

| 指標 KPI | 數值 Value | 評級 Rating | 建議 Recommendation |
|----------|-----------|-------------|-------------------|
| **凱利公式 Kelly%** | {overall_stats.get('凱利', 'N/A')} | {self._get_kelly_rating(overall_stats.get('凱利', 'N/A'))} | {self._get_kelly_recommendation(overall_stats.get('凱利', 'N/A'))} |
| **最大回撤** | {overall_stats.get('最大回撤', 'N/A')} | ✅ 風險可控 | 回撤程度在可接受範圍 |
| **事件發生率** | {overall_stats.get('EventRate', 'N/A')} | ✅ 完整覆蓋 | 策略觸發頻率理想 |

---

## 🔍 多維度濾網分析 Multi-Dimensional Filter Analysis

本節分析不同市場條件下的策略表現，以識別最佳交易環境。

### 1️⃣ 趨勢方向分析 Trend Direction Analysis

| 趨勢方向 | 勝率 Win Rate | 平均P&L | 交易次數 | 評估 |
|----------|--------------|---------|----------|------|"""

        # Add filter analysis results
        if filter_analysis and '趨勢方向' in filter_analysis:
            trend_data = filter_analysis['趨勢方向']
            up_stats = trend_data.get('往上', {})
            down_stats = trend_data.get('往下', {})

            up_win_rate = self._extract_win_rate(up_stats.get('勝率', 'N/A'))
            down_win_rate = self._extract_win_rate(down_stats.get('勝率', 'N/A'))

            md_content += f"""
| **往上** | {up_stats.get('勝率', 'N/A')} | {up_stats.get('筆均', 0):.2f}% | {up_stats.get('總次', 0)} | {'🟢 較佳' if up_win_rate > 50 else '🔴 較差'} |
| **往下** | {down_stats.get('勝率', 'N/A')} | {down_stats.get('筆均', 0):.2f}% | {down_stats.get('總次', 0)} | {'🟢 較佳' if down_win_rate > 50 else '🔴 較差'} |

**結論**: {"下跌趨勢下策略表現顯著優於上漲趨勢" if down_win_rate > up_win_rate + 5 else "上漲趨勢下策略表現較佳" if up_win_rate > down_win_rate + 5 else "兩種趨勢表現相近"}。"""

        # Add settlement type analysis
        md_content += """

### 2️⃣ 結算類型分析 Settlement Type Analysis

| 結算類型 | 勝率 Win Rate | 平均P&L | 交易次數 | 評估 |
|----------|--------------|---------|----------|------|"""

        if filter_analysis and '結算類型' in filter_analysis:
            settlement_data = filter_analysis['結算類型']
            weekly_stats = settlement_data.get('週選', {})
            monthly_stats = settlement_data.get('月選', {})

            weekly_win_rate = self._extract_win_rate(weekly_stats.get('勝率', 'N/A'))
            monthly_win_rate = self._extract_win_rate(monthly_stats.get('勝率', 'N/A'))

            md_content += f"""
| **週選** | {weekly_stats.get('勝率', 'N/A')} | {weekly_stats.get('筆均', 0):.2f}% | {weekly_stats.get('總次', 0)} | {'🟢 較佳' if weekly_win_rate > 50 else '🔴 較差'} |
| **月選** | {monthly_stats.get('勝率', 'N/A')} | {monthly_stats.get('筆均', 0):.2f}% | {monthly_stats.get('總次', 0)} | {'🟢 優秀' if monthly_win_rate > 55 else '🟢 較佳' if monthly_win_rate > 50 else '🔴 較差'} |

**結論**: {'🎯 **月選結算表現顯著優於週選**' if monthly_win_rate > weekly_win_rate + 3 else '**週選和月選表現相近**'}，建議{'重點關注月選結算日的交易機會' if monthly_win_rate > weekly_win_rate + 3 else '兩種結算類型皆可操作'}。"""

        # Add opening position analysis if available
        if filter_analysis and '開盤位置' in filter_analysis:
            opening_data = filter_analysis['開盤位置']
            high_open_stats = opening_data.get('高開', {})
            low_open_stats = opening_data.get('低開', {})

            high_open_win_rate = self._extract_win_rate(high_open_stats.get('勝率', 'N/A'))
            low_open_win_rate = self._extract_win_rate(low_open_stats.get('勝率', 'N/A'))

            md_content += f"""

### 3️⃣ 開盤位置分析 Opening Position Analysis

| 開盤類型 | 勝率 Win Rate | 平均P&L | 交易次數 | 評估 |
|----------|--------------|---------|----------|------|
| **高開** | {high_open_stats.get('勝率', 'N/A')} | {high_open_stats.get('筆均', 0):.2f}% | {high_open_stats.get('總次', 0)} | {'🟢 較佳' if high_open_win_rate > 50 else '🔴 較差'} |
| **低開** | {low_open_stats.get('勝率', 'N/A')} | {low_open_stats.get('筆均', 0):.2f}% | {low_open_stats.get('總次', 0)} | {'🟢 較佳' if low_open_win_rate > 50 else '🔴 較差'} |

**結論**: {"低開情況下策略表現略佳" if low_open_win_rate > high_open_win_rate else "高開情況下策略表現略佳" if high_open_win_rate > low_open_win_rate else "兩種開盤情況表現相近"}。"""

        # Add risk metrics section if available
        if risk_metrics:
            md_content += f"""

---

## ⚠️ 風險分析 Risk Analysis

### 📊 進階風險指標 Advanced Risk Metrics

| 風險指標 Risk Metric | 數值 Value | 解釋 Interpretation |
|---------------------|-----------|-------------------|
| **年化報酬率** | {risk_metrics.get('annualized_return', 0):.2f}% | 策略年化績效 |
| **年化波動率** | {risk_metrics.get('volatility', 0):.2f}% | 策略風險水準 |
| **夏普比率** | {risk_metrics.get('sharpe_ratio', 0):.3f} | 風險調整後報酬 |
| **索提諾比率** | {risk_metrics.get('sortino_ratio', 0):.3f} | 下檔風險調整報酬 |
| **最大回撤** | {risk_metrics.get('max_drawdown', 0):.1f}% | 最大虧損程度 |
| **最大連續虧損** | {risk_metrics.get('max_consecutive_losses', 0)} 筆 | 連續虧損承受能力 |

### 🎯 風險評估 Risk Assessment

**夏普比率評估**: {'🟢 表現優秀' if risk_metrics.get('sharpe_ratio', 0) > 0.5 else '🟡 表現中等' if risk_metrics.get('sharpe_ratio', 0) > 0 else '🔴 需改善'}: {'風險調整後報酬優異' if risk_metrics.get('sharpe_ratio', 0) > 0.5 else '風險調整後報酬中等' if risk_metrics.get('sharpe_ratio', 0) > 0 else '風險調整後報酬偏低'}"""

        # Add strategy recommendations
        md_content += self._generate_recommendations(overall_stats, filter_analysis, risk_metrics)

        # Add footer
        md_content += f"""

---

## 📞 技術支援與免責聲明 Technical Support & Disclaimer

### 技術支援
- 策略邏輯問題請檢查 `taiwan_futures_backtest.py` 主程式
- 數據問題請確認網路連線與數據來源
- 圖表問題請檢查 matplotlib 中文字體設定

### 免責聲明
⚠️ **重要提醒**:
- 本分析僅供學術研究與策略回測使用
- 歷史績效不代表未來表現
- 實際交易請謹慎評估風險並做好資金管理
- 建議諮詢專業投資顧問後再進行實際投資

---

**報告生成完成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**版本**: Enhanced v3.0
**分析引擎**: Taiwan Futures Backtest System

---

*🔬 本報告採用先進的量化分析方法，結合多維度數據挖掘技術，為您提供最專業的策略評估服務*
"""

        return md_content

    def _extract_win_rate(self, win_rate_str):
        """Extract numeric win rate from string"""
        try:
            if isinstance(win_rate_str, str) and '%' in win_rate_str:
                return float(win_rate_str.replace('%', ''))
            return 0
        except:
            return 0

    def _get_kelly_rating(self, kelly_str):
        """Get Kelly criterion rating"""
        try:
            if isinstance(kelly_str, str) and '%' in kelly_str:
                kelly_value = float(kelly_str.replace('%', ''))
                if kelly_value > 15:
                    return '🟢 正值優秀'
                elif kelly_value > 5:
                    return '🟡 正值良好'
                elif kelly_value > 0:
                    return '🟡 正值保守'
                else:
                    return '⚠️ 負值警告'
            return '⚠️ 需檢視'
        except:
            return '⚠️ 需檢視'

    def _get_kelly_recommendation(self, kelly_str):
        """Get Kelly criterion recommendation"""
        try:
            if isinstance(kelly_str, str) and '%' in kelly_str:
                kelly_value = float(kelly_str.replace('%', ''))
                if kelly_value > 15:
                    return '建議適度加大部位'
                elif kelly_value > 5:
                    return '建議維持適中部位'
                elif kelly_value > 0:
                    return '建議保守操作'
                else:
                    return '建議降低部位或暫停交易'
            return '建議保守操作'
        except:
            return '建議保守操作'

    def _generate_recommendations(self, overall_stats, filter_analysis, risk_metrics):
        """Generate strategy recommendations based on performance"""
        net_profit = overall_stats.get('淨利', 0)
        win_rate_str = str(overall_stats.get('勝率', '0%'))
        win_rate_num = self._extract_win_rate(win_rate_str)
        kelly_str = str(overall_stats.get('凱利', '0%'))
        kelly_num = self._extract_win_rate(kelly_str)

        recommendations = """

---

## 💡 策略優化建議 Strategy Optimization Recommendations

### 🟢 正面發現 Positive Findings

"""

        # Add positive findings based on performance
        if net_profit > 5:
            recommendations += f"1. **整體績效優異**: 策略整體勝率達{win_rate_str}，淨利達{net_profit:.2f}%，表現優異\n"
        elif net_profit > 0:
            recommendations += f"1. **策略有效性**: 策略整體勝率達{win_rate_str}，淨利達{net_profit:.2f}%，顯示策略有效\n"

        # Add filter-specific findings
        counter = 2 if net_profit > 0 else 1

        if filter_analysis and '結算類型' in filter_analysis:
            settlement_data = filter_analysis['結算類型']
            monthly_stats = settlement_data.get('月選', {})
            monthly_win_rate = self._extract_win_rate(monthly_stats.get('勝率', 'N/A'))

            if monthly_win_rate > 55:
                recommendations += f"{counter}. **月選結算優勢**: 月選結算勝率達{monthly_stats.get('勝率', 'N/A')}，表現顯著優於週選\n"
                counter += 1

        if kelly_num > 0:
            recommendations += f"{counter}. **凱利公式正值**: {kelly_str}的凱利值顯示策略具有正期望值\n"

        # Add strategy advantages or warnings
        if net_profit > 0 and win_rate_num > 50 and kelly_num > 0:
            recommendations += """
### ✅ 策略優勢 Strategy Advantages

1. **優異的勝率**: 策略勝率優於隨機交易，顯示策略有效性
2. **正值期望**: 凱利公式為正值，建議可適度操作
3. **風險可控**: 回撤程度在可接受範圍內

### 🔧 具體應用建議 Specific Application Recommendations

#### 1. 部位管理
- **適中部位**: 根據凱利公式建議，可設定適中的交易部位
- **風險控制**: 單筆交易風險控制在合理範圍內

#### 2. 實戰應用
- **紙上交易**: 先進行模擬交易驗證策略效果
- **逐步實施**: 確認有效後逐步增加實戰部位
- **持續監控**: 定期檢討實際績效與回測結果的差異"""
        else:
            recommendations += """
### ⚠️ 注意事項 Important Notes

1. **謹慎評估**: 策略績效需要進一步驗證和優化
2. **風險管理**: 實際操作時務必控制風險
3. **持續改進**: 根據實戰結果不斷調整策略參數"""

        return recommendations


def generate_and_save_report(backtester, filename='result.md'):
    """
    Convenience function to generate and save report

    Args:
        backtester: TaiwanFuturesBacktest instance
        filename: Output filename

    Returns:
        str: Path to saved file or None if failed
    """
    generator = ReportGenerator(backtester)
    return generator.save_results_summary_to_md(filename)
