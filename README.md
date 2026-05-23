# 📈 Goldman Sachs Style Stock Analysis Dashboard

A production-style AI-powered equity research dashboard built with Python, Flask, Plotly, Yahoo Finance, FRED macroeconomic data, and Google Gemini AI.

This project delivers institutional-grade stock analysis through an interactive web application capable of:

- Collecting real-time financial market data
- Performing technical and financial analysis
- Visualizing interactive stock analytics
- Generating AI-powered investment insights
- Comparing companies against industry peers
- Integrating macroeconomic indicators into equity research

---

# 🚀 Features

## 📊 Real-Time Market Data
- Live stock prices via Yahoo Finance
- Historical OHLCV data
- Volume analysis
- Real-time percentage and absolute price changes

## 📈 Interactive Financial Visualizations
- Interactive Plotly charts
- Technical indicator overlays
- Return distributions
- Peer comparison analytics
- Zoomable and hover-enabled charts

## 🔧 Technical Analysis
The dashboard automatically computes:

- Moving Averages
- RSI (Relative Strength Index)
- MACD
- Daily Returns
- Volatility Metrics
- Trend Analysis

## 🌍 Macroeconomic Integration
Using the FRED API, the application incorporates:

- Interest rates
- Inflation data
- GDP indicators
- Economic sentiment proxies

## 🤖 AI-Powered Equity Research
Integrated Google Gemini AI provides:

- Investment thesis generation
- Bullish/Bearish sentiment analysis
- Technical outlook summaries
- Earnings quality evaluation
- AI-generated price targets
- Key catalysts and risk identification

## 👥 Peer Comparison
The dashboard compares the selected stock against relevant market peers using:

- Valuation metrics
- Relative performance
- Market capitalization
- Return metrics

---

# 🏗️ Project Architecture

```text
stock-analysis-dashboard/
│
├── app.py
├── config.py
├── requirements.txt
├── run.sh
├── structure.sh
├── .env
│
├── modules/
│   ├── ai_analyzer.py
│   ├── data_cleaner.py
│   ├── data_collector.py
│   └── visualizer.py
│
├── templates/
│   └── dashboard.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── assets/
│
└── README.md
```

---

# ⚙️ Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Data Source | Yahoo Finance, FRED API |
| AI Engine | Google Gemini API |
| Visualization | Plotly |
| Data Processing | Pandas, NumPy |
| Statistical Analysis | Scikit-learn |
| Frontend | HTML, CSS, JavaScript |
| Environment Management | python-dotenv |

---

# 📦 Installation Guide

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/stock-analysis-dashboard.git
cd stock-analysis-dashboard
```

## 2. Create a Virtual Environment

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 API Configuration

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
FRED_API_KEY=your_fred_api_key
```

---

# ▶️ Running the Application

```bash
python app.py
```

Or:

```bash
bash run.sh
```

---

# 🌐 Access the Dashboard

```text
http://localhost:5001
```

---

# 📊 Dashboard Outputs

- Stock Overview
- Technical Charts
- AI Research Insights
- Peer Analytics
- Macro Analysis

---

# 📚 Educational Value

This project demonstrates practical applications of:

- Financial engineering
- Data analytics
- Quantitative finance
- Machine learning integration
- API engineering
- Interactive visualization

---

# 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push the branch
5. Open a pull request

---

# ⚖️ Disclaimer

This application is for educational and informational purposes only.

It does not constitute financial advice, investment recommendations, or professional research.

Always conduct independent due diligence before making investment decisions.

---

# ⭐ Suggested GitHub Topics

```text
finance
fintech
python
flask
plotly
stock-market
quantitative-finance
ai
machine-learning
yfinance
investment-analysis
gemini-ai
fred-api
equity-research
```
