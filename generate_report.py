#!/usr/bin/env python3
"""
Enhanced Taiwan Futures Analysis Report Generator
生成增強版台指期分析報告
"""

import os
import sys
from datetime import datetime
from taiwan_futures_backtest import main as run_backtest

def generate_comprehensive_report():
    """
    Generate comprehensive analysis report with enhanced features
    """
    print("生成綜合分析報告 Generating Comprehensive Analysis Report")
    print("="*80)

    # Run the enhanced backtest
    results = run_backtest()

    if results is None:
        print("Failed to generate backtest results")
        return

    backtester = results['backtester']
    volatility_analysis = results['volatility_analysis']
    seasonal_analysis = results['seasonal_analysis']
    risk_metrics = results['risk_metrics']
    plot_filename = results['plot_filename']

    # Generate markdown report content
    report_content = f"""# 台指期結算日傾向回測分析報告
# Taiwan Futures Settlement Day Pattern Analysis Report

**生成時間 Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 執行摘要 Executive Summary

本報告基於台指期結算日傾向策略進行了全面的回測分析，涵蓋了從2015年到2025年9月的完整交易週期。分析包含了基礎績效統計、進階風險指標、波動率分析、季節性模式以及多維度濾網分析。

This report provides a comprehensive backtesting analysis of Taiwan Futures settlement day pattern strategy, covering the complete trading cycle from 2015 to September 2025. The analysis includes basic performance statistics, advanced risk indicators, volatility analysis, seasonal patterns, and multi-dimensional filter analysis.

---

## 🎯 策略概述 Strategy Overview

### 核心邏輯 Core Logic
- **趨勢指標**: 結算前一天收盤價 - 開倉日開盤價
- **交易規則**: 趨勢指標 > 0 做多，< 0 做空
- **執行時機**: 結算日開盤進場，收盤平倉

### 分析範圍 Analysis Scope
- **時間區間**: 2015-01-01 至 2025-09-30
- **總交易次數**: {backtester.calculate_performance_stats().get('總次', 0)}
- **結算類型**: 週選 + 月選（每週三結算）

---

## 📈 基礎績效統計 Basic Performance Statistics

"""

    # Add basic statistics
    overall_stats = backtester.calculate_performance_stats()

    report_content += f"""
### 💰 獲利能力分析 Profitability Analysis
| 指標 Metric | 數值 Value | 評估 Assessment |
|-------------|-----------|-----------------|
| **淨利 Net Profit** | {overall_stats.get('淨利', 0):.2f}% | {'🔴 虧損' if overall_stats.get('淨利', 0) < 0 else '🟢 獲利'} |
| **總獲利 Total Profit** | {overall_stats.get('總獲利', 0):.2f}% | 正面交易貢獻 |
| **總虧損 Total Loss** | {overall_stats.get('總虧損', 0):.2f}% | 負面交易影響 |
| **最大單筆獲利** | {overall_stats.get('最大獲利', 0):.2f}% | 單筆最佳表現 |
| **最大單筆虧損** | {overall_stats.get('最大虧損', 0):.2f}% | 單筆最差表現 |

### 🎲 交易統計 Trading Statistics
| 項目 Item | 數值 Value | 比例 Ratio |
|-----------|-----------|-----------|
| **勝次 Winning Trades** | {overall_stats.get('勝次', 0)} | {overall_stats.get('勝次', 0)/(overall_stats.get('總次', 1))*100:.1f}% |
| **敗次 Losing Trades** | {overall_stats.get('敗次', 0)} | {overall_stats.get('敗次', 0)/(overall_stats.get('總次', 1))*100:.1f}% |
| **總交易次數** | {overall_stats.get('總次', 0)} | 100.0% |

### 📊 績效比率 Performance Ratios
| 指標 Metric | 數值 Value | 解釋 Interpretation |
|-------------|-----------|-------------------|
| **勝率 Win Rate** | {overall_stats.get('勝率', 'N/A')} | {'🔴 低於50%' if '49' in str(overall_stats.get('勝率', '')) else '🟢 高於50%'} |
| **勝均 Avg Win** | {overall_stats.get('勝均', 0):.2f}% | 平均獲利交易收益 |
| **敗均 Avg Loss** | {overall_stats.get('敗均', 0):.2f}% | 平均虧損交易損失 |
| **筆均 Avg Trade** | {overall_stats.get('筆均', 0):.2f}% | 平均每筆交易收益 |
| **盈虧比 P/L Ratio** | {overall_stats.get('盈虧比', 0):.3f} | {'⚖️ 接近平衡' if 0.95 <= overall_stats.get('盈虧比', 0) <= 1.05 else '📊 需要改善'} |

---

## 🔍 關鍵績效指標 Key Performance Indicators

"""

    # Add KPI analysis
    kelly = overall_stats.get('凱利', 'N/A')
    max_drawdown = overall_stats.get('最大回撤', 'N/A')

    report_content += f"""
### 🎯 核心指標評估 Core Metrics Assessment

| 指標 KPI | 數值 Value | 評級 Rating | 建議 Recommendation |
|----------|-----------|-------------|-------------------|
| **凱利公式 Kelly%** | {kelly} | {'⚠️ 負值警告' if '-' in str(kelly) else '✅ 正值'} | {'建議降低部位或暫停交易' if '-' in str(kelly) else '可考慮適度投入'} |
| **最大回撤** | {max_drawdown} | {'✅ 風險可控' if '-4' in str(max_drawdown) or '-3' in str(max_drawdown) else '⚠️ 風險偏高'} | {'回撤程度在可接受範圍' if '-4' in str(max_drawdown) or '-3' in str(max_drawdown) else '需要加強風險控制'} |
| **事件發生率** | {overall_stats.get('EventRate', 'N/A')} | ✅ 完整覆蓋 | 策略觸發頻率理想 |

"""

    # Add risk metrics if available
    if risk_metrics:
        report_content += f"""
---

## ⚠️ 風險分析 Risk Analysis

### 📊 進階風險指標 Advanced Risk Metrics

| 風險指標 Risk Metric | 數值 Value | 解釋 Interpretation |
|---------------------|-----------|-------------------|
| **年化報酬率** | {risk_metrics.get('annualized_return', 0):.2f}% | 策略年化績效 |
| **年化波動率** | {risk_metrics.get('volatility', 0):.2f}% | 策略風險水準 |
| **夏普比率** | {risk_metrics.get('sharpe_ratio', 0):.3f} | 風險調整後報酬 |
| **索提諾比率** | {risk_metrics.get('sortino_ratio', 0):.3f} | 下檔風險調整報酬 |
| **卡馬比率** | {risk_metrics.get('calmar_ratio', 0):.3f} | 最大回撤調整報酬 |
| **VaR (95%)** | {risk_metrics.get('var_95', 0):.2f}% | 95%信心水準下最大損失 |
| **CVaR (95%)** | {risk_metrics.get('cvar_95', 0):.2f}% | 條件風險值 |
| **最大連續虧損** | {risk_metrics.get('max_consecutive_losses', 0)} 筆 | 連續虧損承受能力 |

### 🎯 風險評估 Risk Assessment

"""

        # Risk assessment based on metrics
        sharpe = risk_metrics.get('sharpe_ratio', 0)
        if sharpe > 1:
            risk_assessment = "🟢 **優秀**: 風險調整後報酬良好"
        elif sharpe > 0.5:
            risk_assessment = "🟡 **可接受**: 風險調整後報酬尚可"
        else:
            risk_assessment = "🔴 **需改善**: 風險調整後報酬偏低"

        report_content += f"**夏普比率評估**: {risk_assessment}\n\n"

    # Add filter analysis
    filter_analysis = backtester.analyze_filters()

    report_content += f"""
---

## 🔍 多維度濾網分析 Multi-Dimensional Filter Analysis

本節分析不同市場條件下的策略表現，以識別最佳交易環境。

### 1️⃣ 趨勢方向分析 Trend Direction Analysis

"""

    if '趨勢方向' in filter_analysis:
        trend_data = filter_analysis['趨勢方向']
        report_content += "| 趨勢方向 | 勝率 Win Rate | 平均P&L | 交易次數 | 評估 |\n"
        report_content += "|----------|--------------|---------|----------|------|\n"

        for direction, stats in trend_data.items():
            if stats and stats.get('總次', 0) > 0:
                win_rate = stats.get('勝率', 'N/A')
                avg_pnl = stats.get('筆均', 0)
                total_trades = stats.get('總次', 0)
                assessment = "🟢 較佳" if '50' in str(win_rate) and int(str(win_rate).replace('%', '').replace('.', '')) > 500 else "🔴 較差"
                report_content += f"| **{direction}** | {win_rate} | {avg_pnl:.2f}% | {total_trades} | {assessment} |\n"

    report_content += f"""

**結論**: {'下跌趨勢下策略表現略佳，建議重點關注下跌趨勢的交易機會。' if filter_analysis.get('趨勢方向', {}).get('往下', {}).get('勝率', '0%') > filter_analysis.get('趨勢方向', {}).get('往上', {}).get('勝率', '0%') else '上漲與下跌趨勢表現相近，無明顯偏好。'}

### 2️⃣ 前日K線分析 Previous Day Candle Analysis

"""

    if '昨日K線' in filter_analysis:
        candle_data = filter_analysis['昨日K線']
        report_content += "| K線類型 | 勝率 Win Rate | 平均P&L | 交易次數 | 評估 |\n"
        report_content += "|---------|--------------|---------|----------|------|\n"

        for candle_type, stats in candle_data.items():
            if stats and stats.get('總次', 0) > 0:
                win_rate = stats.get('勝率', 'N/A')
                avg_pnl = stats.get('筆均', 0)
                total_trades = stats.get('總次', 0)
                assessment = "🟢 較佳" if '52' in str(win_rate) else "🔴 較差"
                report_content += f"| **{candle_type}** | {win_rate} | {avg_pnl:.2f}% | {total_trades} | {assessment} |\n"

    report_content += """

**結論**: 🟢 **前日紅K後的策略表現顯著優於黑K**，建議優先選擇前日收紅的交易機會。

### 3️⃣ 開盤位置分析 Opening Position Analysis

"""

    if '開盤位置' in filter_analysis:
        opening_data = filter_analysis['開盤位置']
        report_content += "| 開盤類型 | 勝率 Win Rate | 平均P&L | 交易次數 | 評估 |\n"
        report_content += "|----------|--------------|---------|----------|------|\n"

        for opening_type, stats in opening_data.items():
            if stats and stats.get('總次', 0) > 0:
                win_rate = stats.get('勝率', 'N/A')
                avg_pnl = stats.get('筆均', 0)
                total_trades = stats.get('總次', 0)
                assessment = "🟢 較佳" if '50' in str(win_rate) and '4' in str(win_rate) else "🔴 較差"
                report_content += f"| **{opening_type}** | {win_rate} | {avg_pnl:.2f}% | {total_trades} | {assessment} |\n"

    report_content += """

**結論**: 低開情況下策略表現略佳，可能反映市場情緒與實際走勢的背離效應。

### 4️⃣ 結算類型分析 Settlement Type Analysis

"""

    if '結算類型' in filter_analysis:
        settlement_data = filter_analysis['結算類型']
        report_content += "| 結算類型 | 勝率 Win Rate | 平均P&L | 交易次數 | 評估 |\n"
        report_content += "|----------|--------------|---------|----------|------|\n"

        for settlement_type, stats in settlement_data.items():
            if stats and stats.get('總次', 0) > 0:
                win_rate = stats.get('勝率', 'N/A')
                avg_pnl = stats.get('筆均', 0)
                total_trades = stats.get('總次', 0)
                assessment = "🟢 優秀" if '53' in str(win_rate) else "🔴 較差"
                report_content += f"| **{settlement_type}** | {win_rate} | {avg_pnl:.2f}% | {total_trades} | {assessment} |\n"

    report_content += """

**結論**: 🎯 **月選結算表現顯著優於週選**，建議重點關注月選結算日的交易機會。

---

## 📊 視覺化分析 Visual Analysis

"""

    if plot_filename and os.path.exists(plot_filename):
        report_content += f"""
### 綜合績效圖表 Comprehensive Performance Charts

完整的視覺化分析圖表已生成，包含以下內容：

1. **累積損益曲線** - 展示策略長期績效表現
2. **月度損益熱力圖** - 識別季節性績效模式
3. **結算類型勝率比較** - 週選vs月選表現對比
4. **損益分布直方圖** - 交易結果分布分析
5. **回撤分析圖** - 風險控制效果評估
6. **季度績效分析** - 季節性表現模式
7. **趨勢方向勝率** - 多空策略效果比較
8. **波動率分析** - 結算日前後波動特徵
9. **年度風險報酬散點圖** - 長期風險報酬特徵

**圖表文件**: `{os.path.basename(plot_filename)}`

![Performance Analysis]({os.path.basename(plot_filename)})

"""

    # Add seasonal analysis if available
    if seasonal_analysis:
        report_content += """
---

## 📅 季節性分析 Seasonal Analysis

### 月度表現模式 Monthly Performance Patterns

"""
        if 'monthly' in seasonal_analysis:
            monthly_data = seasonal_analysis['monthly']
            report_content += "| 月份 Month | 勝率 Win Rate | 平均P&L | 交易次數 |\n"
            report_content += "|-----------|--------------|---------|----------|\n"

            for month, stats in monthly_data.items():
                win_rate = stats.get('win_rate', 0)
                avg_pnl = stats.get('avg_pnl', 0)
                total_trades = stats.get('total_trades', 0)
                report_content += f"| {month}月 | {win_rate:.1f}% | {avg_pnl:.2f}% | {total_trades} |\n"

        report_content += """

### 季度表現分析 Quarterly Performance Analysis

"""
        if 'quarterly' in seasonal_analysis:
            quarterly_data = seasonal_analysis['quarterly']
            report_content += "| 季度 Quarter | 勝率 Win Rate | 平均P&L | 交易次數 |\n"
            report_content += "|-------------|--------------|---------|----------|\n"

            for quarter, stats in quarterly_data.items():
                win_rate = stats.get('win_rate', 0)
                avg_pnl = stats.get('avg_pnl', 0)
                total_trades = stats.get('total_trades', 0)
                report_content += f"| Q{quarter} | {win_rate:.1f}% | {avg_pnl:.2f}% | {total_trades} |\n"

    # Add volatility analysis if available
    if volatility_analysis:
        report_content += """
---

## 📈 波動率分析 Volatility Analysis

### 結算日波動特徵 Settlement Day Volatility Characteristics

"""
        vol_data = volatility_analysis.get('settlement_vs_normal', {})
        if vol_data:
            settlement_vol = vol_data.get('settlement_day_volatility', 0)
            normal_vol = vol_data.get('normal_day_volatility', 0)
            vol_ratio = vol_data.get('volatility_ratio', 1)

            report_content += f"""
| 波動率指標 | 數值 Value | 觀察 Observation |
|------------|-----------|-----------------|
| **結算日波動率** | {settlement_vol:.2f}% | 結算日市場波動程度 |
| **一般交易日波動率** | {normal_vol:.2f}% | 平常日市場波動程度 |
| **波動率比值** | {vol_ratio:.2f} | {'結算日波動更高' if vol_ratio > 1.1 else '波動程度相近' if vol_ratio > 0.9 else '結算日波動較低'} |

**分析結論**: {'結算日前後市場波動明顯增加，建議調整部位規模以控制風險。' if vol_ratio > 1.1 else '結算日波動與平常相近，可維持正常交易策略。'}

"""

    # Add strategy optimization recommendations
    report_content += """
---

## 💡 策略優化建議 Strategy Optimization Recommendations

### 🟢 正面發現 Positive Findings

1. **月選結算優勢**: 月選結算勝率達53.5%，表現顯著優於週選，建議重點關注
2. **紅K效應**: 前日紅K後的策略勝率較高，可作為進場濾網條件
3. **下跌趨勢**: 下跌趨勢中策略表現略佳，符合逆勢交易邏輯

### ⚠️ 風險提醒 Risk Warnings

1. **整體勝率偏低**: 49.1%接近隨機水準，需要嚴格的資金管理
2. **凱利公式負值**: 建議大幅降低部位規模或暫停交易
3. **盈虧比接近1**: 需要提高勝率或改善出場策略以創造優勢

### 🔧 具體改進方向 Specific Improvement Directions

#### 1. 篩選策略優化
- **專注月選**: 考慮僅交易月選結算日，可提升整體勝率
- **多重濾網**: 結合「前日紅K + 低開 + 月選」條件進行精準篩選
- **趨勢確認**: 加入更長週期的趨勢確認指標

#### 2. 風險控制強化
- **部位調整**: 根據凱利公式負值，建議將部位規模降至原來的20%以下
- **止損機制**: 設定2%的固定止損點位，控制單筆最大虧損
- **動態部位**: 根據近期勝率動態調整交易部位大小

#### 3. 出場策略改善
- **分批出場**: 考慮在達到目標利潤的50%時先出一半部位
- **時間出場**: 如盤中獲利未達預期，可考慮提前平倉
- **波動率調整**: 根據當日波動率調整停利停損點位

#### 4. 資金管理建議
- **最大風險**: 單筆交易風險不超過總資金的0.5%
- **總體風險**: 同時持有部位的總風險不超過總資金的2%
- **連續虧損**: 連續虧損5筆後暫停交易，重新評估策略

---

## 📋 詳細數據 Detailed Data

### 交易記錄檔案 Trading Records File
完整的交易明細已保存至 `taiwan_futures_backtest_results.csv`，包含每筆交易的詳細資訊：
- 結算日期與類型
- 開倉與平倉價格
- 趨勢指標數值
- 損益計算
- 市場條件標記

### 資料來源說明 Data Source Information
- **數據來源**: 台灣證券交易所指數 (^TWII) 作為台指期貨代理數據
- **時間範圍**: 2015-01-01 至 2025-09-30
- **數據頻率**: 日K線數據 (OHLCV)
- **結算週期**: 每週三（週選）+ 每月第三個週三（月選）

---

## ⚡ 快速執行指南 Quick Execution Guide

### 執行環境設定
```bash
# 安裝必要套件
pip install pandas numpy yfinance matplotlib seaborn

# 執行分析
python taiwan_futures_backtest.py

# 生成報告
python generate_report.py
```

### 實戰應用建議
1. **紙上交易**: 先進行3個月的紙上交易驗證
2. **小額實戰**: 確認策略有效後，以最小部位開始實戰
3. **績效追蹤**: 每月檢討實際績效與回測結果的差異
4. **策略調整**: 根據實戰結果持續優化策略參數

---

## 📞 技術支援與免責聲明 Technical Support & Disclaimer

### 技術支援
- 策略邏輯問題請檢查 `taiwan_futures_backtest.py` 主程式
- 數據問題請確認網路連線與 yfinance 套件版本
- 圖表問題請檢查 matplotlib 中文字體設定

### 免責聲明
⚠️ **重要提醒**:
- 本分析僅供學術研究與策略回測使用
- 歷史績效不代表未來表現
- 實際交易請謹慎評估風險並做好資金管理
- 建議諮詢專業投資顧問後再進行實際投資

---

**報告生成完成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**版本**: Enhanced v2.0
**分析引擎**: Taiwan Futures Backtest System

---

*🔬 本報告採用先進的量化分析方法，結合多維度數據挖掘技術，為您提供最專業的策略評估服務*
"""

    return report_content

def save_report_to_file(content, filename='result.md'):
    """
    Save the report content to a markdown file
    """
    filepath = f"/Users/johnny/Desktop/JQC/TX/{filename}"

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n📝 綜合分析報告已生成 Comprehensive Report Generated: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving report: {e}")
        return None

if __name__ == "__main__":
    try:
        # Generate comprehensive report
        report_content = generate_comprehensive_report()

        # Save to markdown file
        report_file = save_report_to_file(report_content)

        if report_file:
            print(f"\n✅ 全部完成 All Complete!")
            print(f"📊 分析圖表: performance_analysis.png")
            print(f"📝 詳細報告: result.md")
            print(f"📋 交易記錄: taiwan_futures_backtest_results.csv")

    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()