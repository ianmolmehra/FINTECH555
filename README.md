cd ~/Desktop/Projects/FINTECH555
brew install python@3.11
rm -rf .venv

python3.11 -m venv .venv
source .venv/bin/activate

python3.11 -m pip install --upgrade pip setuptools wheel

xcode-select --install

pip install -r requirements.txt

streamlit run app/main.py



pip install streamlit==1.35.0 pandas==2.2.2 numpy==1.26.4 \
  scikit-learn==1.5.0 xgboost==2.0.3 scipy==1.13.1 \
  statsmodels==0.14.2 plotly==5.22.0 kaleido==0.2.1 \
  openpyxl==3.1.4 xlsxwriter==3.2.0 fpdf2==2.7.9

pip install shap==0.45.1 --no-build-isolation
> *"We don't analyze trades. We analyze panic, patience, and decision discipline — using AI."*

**Post-Trade AI Analytics · 6th Semester Major Project**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 What Is FINTECH555?

FINTECH555 is a **production-grade, AI-powered post-trade behavioral analytics platform** built for retail traders. Instead of telling you *what* you traded, it tells you *how* you decide — and where psychology is costing you money.

**Key Experience:** Drag and drop a broker CSV → AI runs everything automatically → Full interactive report renders on the same page. No export needed. No buttons. Everything appears instantly.

---

## 🏗️ Architecture

```
FINTECH555/
├── app/
│   ├── main.py                          # Entry point: streamlit run app/main.py
│   ├── config/
│   │   └── settings.py                  # All thresholds, tax rates, THEME, NSE_SECTOR_MAP
│   ├── upload/
│   │   ├── uploader.py                  # Drag-drop file upload handler
│   │   ├── validator.py                 # Column validation + type normalization
│   │   └── broker_parser.py             # Multi-broker format auto-detection
│   ├── preprocessing/
│   │   └── cleaner.py                   # Feature engineering — 20+ derived columns
│   ├── analytics/                       # 19 analytics modules
│   │   ├── decision_score.py            # Module 1: Decision Intelligence Score
│   │   ├── panic_detection.py           # Module 2: Behavioral Bias & Panic
│   │   ├── simulations.py               # Module 3: Patience Gap (Monte Carlo GBM)
│   │   ├── loss_attribution.py          # Module 4: Loss Attribution (RF + SHAP)
│   │   ├── trader_dna.py                # Module 5: Trader DNA Profile
│   │   ├── skill_vs_luck.py             # Module 6: Skill vs Luck Decomposition
│   │   ├── sector_heatmap.py            # Module 7: Sector Skill Heatmap
│   │   ├── tax_advisor.py               # Module 8: Tax Intelligence (STCG/LTCG)
│   │   ├── annual_review.py             # Module 9: Year-over-Year Review
│   │   ├── prediction_engine.py         # Module 10: Predictive Analytics
│   │   ├── drawdown.py                  # Module 11: Drawdown Analysis
│   │   ├── streak_analysis.py           # Module 12: Streak Analysis
│   │   ├── time_pattern.py              # Module 13: Day/Time Pattern Analysis
│   │   ├── capital_efficiency.py        # Module 14: Capital Efficiency Curve
│   │   ├── kelly_criterion.py           # Module 15: Kelly Criterion
│   │   ├── bayesian_winrate.py          # Module 16: Bayesian Win Rate
│   │   ├── efficient_frontier.py        # Module 17: Efficient Frontier
│   │   ├── trade_tagger.py              # Module 18: Trade Auto-Tagger
│   │   └── peer_comparison.py           # Module 19: Peer Comparison
│   ├── explainability/
│   │   └── xai.py                       # Multi-condition XAI rule engine
│   ├── models/
│   │   ├── ml_models.py                 # Save/load sklearn models (.pkl)
│   │   └── saved/                       # Persisted model files
│   ├── ui/
│   │   ├── layout.py                    # Master layout + render_layout() entry point
│   │   ├── report.py                    # Tabbed report orchestrator (12 tabs)
│   │   ├── charts.py                    # All Plotly chart builders
│   │   ├── components.py                # Reusable: cards, badges, strips
│   │   ├── theme.py                     # Dark FinTech CSS injection
│   │   ├── report_card.py               # Master score card with letter grades
│   │   ├── fingerprint_card.py          # Behavioral Fingerprint Card (5-word summary)
│   │   ├── progress_timeline.py         # Month-by-month evolution timeline
│   │   └── worst_day_view.py            # Worst Day forensic breakdown
│   ├── utils/
│   │   ├── helpers.py                   # Shared utility functions
│   │   ├── export.py                    # Excel export
│   │   └── bootstrap.py                 # Bootstrap CI utilities
│   └── api_integration/                 # Phase 2 stubs (import-safe, no API keys needed)
│       ├── __init__.py
│       ├── broker_api_stub.py           # Zerodha / Upstox live API stub
│       ├── market_data_stub.py          # yfinance / NSEPython data stub
│       ├── llm_explainer_stub.py        # Claude / GPT explanation stub
│       └── README.md                    # Phase 2 activation guide
├── data/
│   └── sample/
│       └── sample_broker_report.csv     # Sample trades for testing
└── requirements.txt
```

---

## 🚀 How to Run

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Step 1: Clone / Extract the project
```bash
cd FINTECH555
```

### Step 2: Create a virtual environment (recommended)
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Mac/Linux:
source .venv/bin/activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** `shap` and `xgboost` may take a few minutes to install. This is normal.

### Step 4: Run the application
```bash
streamlit run app/main.py
```

### Step 5: Open in browser
Streamlit will auto-open: `http://localhost:8501`

---

## 📊 How to Use

1. **Open the app** — you'll see the FINTECH555 hero dashboard
2. **Download the sample file** from the sidebar, or use your own broker export
3. **Drag and drop** your CSV/Excel file onto the upload widget
4. **Wait ~5 seconds** — all 19 analytics modules run automatically
5. **Navigate the 12 tabs** to explore every dimension of your trading behavior
6. **Check the sidebar** — paste NSE stock symbols for Watchlist Intelligence

---

## 📁 Supported Broker Formats

| Broker | Detection Method | Auto-Mapped |
|--------|-----------------|-------------|
| Zerodha | `tradingsymbol` column | ✅ |
| Upstox | `scrip_code` column | ✅ |
| Groww | `stock_name` column | ✅ |
| Angel One | `scripname` column | ✅ |
| Generic/Custom | Standard columns (symbol, pnl, etc.) | ✅ |

If auto-detection fails → manual column mapping UI appears automatically.

**Standard CSV format (easiest):**
```csv
symbol,entry_date,exit_date,entry_price,exit_price,quantity,pnl,sector
RELIANCE,2024-01-15,2024-02-01,2450.00,2510.50,10,605.00,Energy
TCS,2024-01-20,2024-03-01,3800.00,3920.00,5,600.00,IT
```

---

## 🧠 19 Analytics Modules

| # | Module | ML Concept | Key Output |
|---|--------|-----------|------------|
| 1 | Decision Intelligence Score | CV, Penalty Function | 0-100 score + grade |
| 2 | Panic & Bias Detection | KMeans Clustering (k=3) | 5-bias radar chart |
| 3 | Patience Gap Simulator | Geometric Brownian Motion | Alternate reality PnL |
| 4 | Loss Attribution | Random Forest + SHAP | Loss cause breakdown |
| 5 | Trader DNA Profile | Multi-dim scoring matrix | 6-axis archetype |
| 6 | Skill vs Luck | Monte Carlo z-score + KS test | Skill % with Bootstrap CI |
| 7 | Sector Heatmap | Gini + Herfindahl Index | Treemap by sector |
| 8 | Tax Intelligence | STCG/LTCG rules | Tax optimization score |
| 9 | Annual Review | YoY comparison | Report card A-F grades |
| 10 | Prediction Engine | GBM + Ridge + k-NN | Next-trade win probability |
| 11 | Drawdown Analysis | Max Drawdown formula | Calmar ratio + equity curve |
| 12 | Streak Analysis | Run-Length Encoding | Post-streak conditional P |
| 13 | Time/Day Patterns | Chi-Squared Test | Best/worst trading days |
| 14 | Capital Efficiency | OLS Regression, Pearson r | Optimal capital band |
| 15 | Kelly Criterion | f* = (bp-q)/b | Half-Kelly recommendation |
| 16 | Bayesian Win Rate | Beta-Binomial conjugate | 95% credible interval |
| 17 | Efficient Frontier | Markowitz, QP optimization | Optimal sector weights |
| 18 | Trade Auto-Tagger | Rule-based multi-label | Color-coded trade tags |
| 19 | Peer Comparison | scipy.stats.percentileofscore | Retail trader percentile |

---

## 📐 ML & Statistics Concepts Implemented

Every concept has an inline comment in the code explaining the formula:

- **Coefficient of Variation** — CV = std/mean (sizing discipline)
- **K-Means Clustering** — minimizes within-cluster sum of squares
- **Geometric Brownian Motion** — S(t) = S(0)×exp((μ-σ²/2)t + σ√t×Z)
- **Random Forest + SHAP** — ensemble trees with Shapley value attribution
- **Logistic Regression** — P(Win) = sigmoid(w·X + b)
- **Monte Carlo Simulation** — 1000 shuffles, z-score vs actual
- **Sharpe Ratio** — Mean/Std × √252 (annualized)
- **Sortino Ratio** — Mean/Downside_Std × √252
- **Bootstrap CI** — 95% CI = mean ± 1.96×std (CLT application)
- **Kolmogorov-Smirnov Test** — non-parametric distribution comparison
- **Gradient Boosting** — F_m(x) = F_{m-1}(x) + γ×h_m(x)
- **Ridge Regression** — minimize MSE + λ||w||² (L2 regularization)
- **k-NN Regression** — average of k nearest historical trades
- **Max Drawdown** — (Peak - Trough) / Peak
- **Calmar Ratio** — Annual Return / Max Drawdown
- **Run-Length Encoding** — compress win/loss sequences
- **Chi-Squared Test** — χ² = Σ(obs-exp)²/exp (day uniformity)
- **OLS Regression** — β = (X'X)⁻¹X'y (capital vs return)
- **Kelly Criterion** — f* = (bp - q) / b (optimal bet fraction)
- **Beta-Binomial Bayes** — Posterior = Beta(W+1, L+1)
- **Markowitz Frontier** — Var(Rp) = w'Σw (quadratic programming)
- **Gini Coefficient** — profit distribution inequality
- **Herfindahl Index** — H = Σ(share_i²) (concentration measure)
- **Percentile Scoring** — scipy.stats.percentileofscore vs benchmark

---

## 🎨 UI Visual Features

- **Dark FinTech Theme** — `#0A0F0A` background, `#00C853` green accents
- **Behavioral Fingerprint Card** — 5-word AI personality summary
- **Progress Timeline** — month-by-month BHS evolution dots
- **Worst Day Forensic** — narrative storytelling of worst trading day
- **Report Card** — letter grades (A-F) for every performance dimension
- **Watchlist Intelligence** — sidebar sector match scoring for NSE stocks
- **Trade Auto-Tagger** — color-coded filterable trade history table
- **What-If Sliders** — interactive DIS improvement simulation

---

## 🔧 Phase 2 — API Integration (Optional)

All analytics work offline in Phase 1. Phase 2 adds live data:

```bash
# Install Phase 2 dependencies
pip install anthropic openai kiteconnect yfinance

# Set environment variables
export ANTHROPIC_API_KEY="your-claude-api-key"
export ZERODHA_API_KEY="your-zerodha-key"
```

See `app/api_integration/README.md` for detailed activation guide.

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: streamlit` | Run `pip install -r requirements.txt` |
| `shap` install fails on Windows | `pip install shap --no-build-isolation` |
| File upload "No trades found" | Check CSV has `symbol`, `entry_date`, `pnl` columns |
| Charts not rendering | Ensure `plotly>=5.22.0` installed |
| Port 8501 already in use | `streamlit run app/main.py --server.port 8502` |
| `kaleido` error on PDF export | Install: `pip install kaleido==0.2.1` |

---

## 📦 Dependencies

```
streamlit==1.35.0      # Web UI framework
pandas==2.2.2          # Data manipulation
numpy==1.26.4          # Numerical computing
scikit-learn==1.5.0    # ML algorithms
scipy==1.13.1          # Statistics (KS test, percentile)
plotly==5.22.0         # Interactive charts
shap==0.45.1           # ML explainability
statsmodels==0.14.2    # Statistical models
xgboost==2.0.3         # Gradient boosting
openpyxl==3.1.4        # Excel read
xlsxwriter==3.2.0      # Excel write
fpdf2==2.7.9           # PDF export
```

---

## 🎓 Academic Context

**Project:** 6th Semester Major Project  
**Domain:** FinTech · Behavioral Finance · Machine Learning  
**Academic Rigor:** 24+ ML/statistical concepts with inline formula documentation  
**Industry Standard:** Production-quality code structure suitable for real deployment  

Every non-trivial line of code has an inline comment naming the ML concept, formula, or statistical theorem being applied. The code itself IS the academic documentation.

---

## ⚠️ Disclaimer

FINTECH555 is an educational and analytical tool for understanding past trading behavior. It is **not investment advice**. Past behavioral patterns do not guarantee future performance. All analytics are for educational purposes only.

---

*Built with Python · Streamlit · scikit-learn · Plotly · FINTECH555 © 2025*
