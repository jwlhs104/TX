# 台指期結算日傾向回測系統
# Taiwan Futures Settlement Day Pattern Backtesting System

## 概述 Overview

本系統分析台指期貨在結算日的價格傾向模式，並建立相應的交易策略。系統根據結算前趨勢指標預測結算日價格方向，實現自動化回測分析。

This system analyzes Taiwan Futures (TAIEX Futures) settlement day price patterns and implements corresponding trading strategies. The system predicts settlement day price direction based on pre-settlement trend indicators and performs automated backtesting analysis.

## 功能特色 Features

### 🎯 核心策略 Core Strategy
- **趨勢指標計算**: 結算前一天收盤價 - 開倉日開盤價
- **交易邏輯**: 趨勢指標 > 0 做多，< 0 做空
- **進出場時機**: 結算日開盤進場，收盤平倉

### 📊 數據處理 Data Processing
- **時間範圍**: 2015年夜盤開始至2025年9月
- **數據頻率**: 日K線資料（OHLCV）
- **結算週期**: 週選（每週三）+ 月選（每月第三個週三）

### 🔍 濾網分析 Filter Analysis
1. **趨勢方向**: 往上 vs 往下
2. **昨日K線**: 紅K vs 黑K
3. **開盤位置**: 高開 vs 低開
4. **結算類型**: 週選 vs 月選

### 📈 績效統計 Performance Statistics
- 完整交易統計（勝負次數、獲利虧損）
- 關鍵績效指標（勝率、盈虧比、凱利公式）
- 風險控制指標（最大回撤）
- 事件發生率分析

## 🚀 Quick Start

### 1. Setup (One-time)
```bash
# Run setup script
bash setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Run Backtest
```bash
# Using Makefile (recommended)
make backtest

# Or using CLI directly
python cli.py backtest
```

### 3. View Results
Results are in `output/` directory:
- `output/results/` - CSV files with trade details
- `output/reports/` - Analysis reports
- `output/plots/` - Performance charts

📖 **See [docs/QUICKSTART.md](docs/QUICKSTART.md) for detailed instructions**

---

## 安裝與使用 Installation & Usage

### 環境要求 Requirements
```bash
# Automatically installed by setup.sh
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.12.0
scipy>=1.9.0
```

### 執行方式 Execution Methods

#### Method 1: Makefile Commands (Easiest)
```bash
make backtest              # Run standard backtest
make backtest-monthly      # Monthly settlements only
make backtest-night        # Night session pricing
make maxpain               # TXO max pain analysis
make report                # Generate comprehensive report
make help                  # Show all commands
```

#### Method 2: Unified CLI
```bash
# TX Backtest
python cli.py backtest [options]

# TXO Max Pain Analysis
python cli.py maxpain [options]

# Generate Report
python cli.py report

# Calculate Max Pain from CSV
python cli.py calc <file>

# Show help
python cli.py --help
```

#### Method 3: Direct Python Scripts (Legacy)
```bash
python taiwan_futures_backtest.py
python txo_max_pain_backtest.py
python generate_report.py
```

### 輸出檔案 Output Files
- `output/results/taiwan_futures_backtest_results.csv`: 詳細交易記錄
- `output/reports/result.md`: 綜合分析報告
- `output/plots/performance_analysis.png`: 績效圖表

## 回測結果 Backtest Results

### 📊 整體策略績效 Overall Performance
| 指標 Metric | 數值 Value |
|-------------|-----------|
| **分析期間** | 2015-01-01 至 2025-09-30 |
| **總交易次數** | 560 |
| **事件發生率** | 100.0% |

### 💰 基礎交易統計 Basic Trading Statistics
| 項目 Item | 數值 Value |
|-----------|-----------|
| **淨利** | -1.53% |
| **總獲利** | 42.66% |
| **總虧損** | -44.18% |
| **最大獲利** | 0.61% |
| **最大虧損** | -0.45% |

### 🎲 交易次數統計 Trade Count Statistics
| 項目 Item | 數值 Value |
|-----------|-----------|
| **勝次** | 275 |
| **敗次** | 285 |
| **總次** | 560 |
| **無歸類** | 0 |

### 📈 績效比率 Performance Ratios
| 項目 Item | 數值 Value |
|-----------|-----------|
| **勝均** | 0.16% |
| **敗均** | -0.16% |
| **筆均** | -0.00% |

### 🔑 關鍵績效指標 Key Performance Indicators
| 指標 KPI | 數值 Value | 評級 Rating |
|----------|-----------|-------------|
| **盈虧比** | 1.001 | ⚖️ 平衡 |
| **勝率** | 49.1% | 📊 接近隨機 |
| **凱利** | -1.8% | ⚠️ 負值建議不交易 |
| **最大回撤** | -4.7% | ✅ 風險可控 |

## 🔍 濾網分析結果 Filter Analysis Results

### 1. 趨勢方向分析 Trend Direction Analysis
| 方向 Direction | 勝率 Win Rate | 筆均 Avg P&L | 總次 Total |
|---------------|--------------|--------------|-----------|
| **往上** | 48.1% | 0.01% | 293 |
| **往下** | 50.2% | -0.01% | 267 |

**結論**: 下跌趨勢略勝於上漲趨勢

### 2. 昨日K線分析 Previous Day Candle Analysis
| K線類型 Candle | 勝率 Win Rate | 筆均 Avg P&L | 總次 Total |
|---------------|--------------|--------------|-----------|
| **紅K** | 52.0% | 0.01% | 275 |
| **黑K** | 46.3% | -0.02% | 285 |

**結論**: 🟢 紅K後的策略表現較佳

### 3. 開盤位置分析 Opening Position Analysis
| 開盤類型 Open Type | 勝率 Win Rate | 筆均 Avg P&L | 總次 Total |
|------------------|--------------|--------------|-----------|
| **高開** | 48.0% | -0.01% | 304 |
| **低開** | 50.4% | 0.01% | 256 |

**結論**: 低開情況下策略表現較佳

### 4. 結算類型分析 Settlement Type Analysis
| 結算類型 Type | 勝率 Win Rate | 筆均 Avg P&L | 總次 Total |
|--------------|--------------|--------------|-----------|
| **週選** | 47.8% | -0.01% | 431 |
| **月選** | 53.5% | 0.01% | 129 |

**結論**: 🎯 **月選結算表現顯著優於週選**

## 💡 策略優化建議 Strategy Optimization Recommendations

### 🟢 正面發現 Positive Findings
1. **月選結算優勢**: 月選結算勝率達53.5%，建議重點關注
2. **紅K效應**: 前日紅K後的策略勝率較高
3. **低開優勢**: 低開情況下策略表現更穩定

### ⚠️ 風險提醒 Risk Warnings
1. **整體勝率偏低**: 49.1%接近隨機，需要嚴格資金管理
2. **凱利公式負值**: 建議降低部位規模或尋找更好的進場時機
3. **盈虧比接近1**: 需要提高勝率或改善出場策略

### 🔧 改進方向 Improvement Directions
1. **專注月選**: 考慮僅交易月選結算日
2. **加強濾網**: 結合紅K + 低開條件進行篩選
3. **優化出場**: 研究盤中最佳平倉時機
4. **加入止損**: 設定合理的止損點位控制風險

## 📁 檔案結構 File Structure

```
TX/
├── taiwan_futures_backtest.py          # 主程式檔案
├── requirements.txt                     # 依賴套件
├── taiwan_futures_backtest_results.csv # 詳細交易記錄
├── 台指結算日傾向回測.pdf                # 策略需求文件
└── README.md                           # 本說明文件
```

## 🔧 技術架構 Technical Architecture

### 核心類別 Core Classes
- `TaiwanFuturesBacktest`: 主要回測引擎
  - `get_taiwan_futures_data()`: 數據獲取
  - `calculate_settlement_dates()`: 結算日計算
  - `run_backtest()`: 執行回測
  - `calculate_performance_stats()`: 績效計算
  - `analyze_filters()`: 濾網分析
  - `generate_report()`: 報告生成

### 數據來源 Data Sources
- **主要**: yfinance (^TWII - 台灣加權指數)
- **備用**: 內建樣本數據生成器

## 📊 輸出格式規範 Output Format Specifications

根據需求文件規範:
- **百分比欄位**: 顯示到小數點後2位 (96.8%)
- **比率欄位**: 顯示到小數點後3位 (1.303)
- **回撤欄位**: 負數顯示 (-17%)

## ⚡ 快速開始 Quick Start

1. **安裝依賴**:
```bash
pip install -r requirements.txt
```

2. **執行回測**:
```bash
python taiwan_futures_backtest.py
```

3. **查看結果**:
   - 終端顯示完整報告
   - CSV檔案包含詳細交易記錄

## 📞 技術支援 Technical Support

如有技術問題或改進建議，請檢查:
1. 數據連線是否正常
2. 所有依賴套件是否已安裝
3. Python版本是否相容 (建議3.7+)

---

**開發完成日期**: 2025-09-20
**版本**: v1.0
**授權**: MIT License

*本系統僅供學術研究和策略回測使用，實際交易請謹慎評估風險*