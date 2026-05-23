stock-analysis-dashboard/
│
├── app.py                          # Main Flask application entry point
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (API keys)
│
├── modules/
│   ├── __init__.py
│   ├── data_collector.py          # Module 1: Data collection (yfinance)
│   ├── data_cleaner.py            # Module 2: Data cleaning & processing
│   ├── visualizer.py              # Module 3: Chart generation
│   └── ai_analyzer.py             # Module 4: AI analysis (Google AI Studio)
│
├── templates/
│   └── dashboard.html              # HTML frontend template
│
├── static/
│   ├── css/
│   │   └── style.css               # CSS styles
│   └── js/
│       └── dashboard.js            # Frontend JavaScript
│
├── output_charts/                  # Generated chart images
│
└── config.py                       # Configuration settings