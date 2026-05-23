"""
Goldman Sachs Complete Stock Analysis Dashboard
Real-time data from Yahoo Finance and FRED API
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
import traceback
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Import modules
from modules.data_collector import DataCollector
from modules.data_cleaner import DataCleaner
from modules.visualizer import DataVisualizer
from modules.ai_analyzer import AIAnalyzer

# Initialize modules
data_collector = DataCollector()
data_cleaner = DataCleaner()
visualizer = DataVisualizer()
ai_analyzer = AIAnalyzer(api_key=os.getenv('GOOGLE_API_KEY', ''))


def clean_for_json(obj):
    """Clean data for JSON serialization"""
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return None if np.isnan(obj) else float(obj)
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif pd.isna(obj):
        return None
    return obj


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze stock ticker"""
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').strip().upper()
        
        if not ticker:
            return jsonify({'error': 'No ticker provided'}), 400
        
        print(f"\n{'='*60}")
        print(f"🔍 Analyzing {ticker}...")
        print(f"{'='*60}")
        
        # Fetch stock data
        print("[1/5] 📊 Fetching stock data...")
        stock_data = data_collector.fetch_stock_data(ticker)
        price_data = data_collector.fetch_current_price(ticker)
        metrics = data_collector.fetch_financial_metrics(ticker)
        
        if stock_data.empty:
            return jsonify({'error': f'No data found for {ticker}'}), 404
        
        print(f"   Stock data shape: {stock_data.shape}")
        print(f"   Price range: ${stock_data['Close'].min():.2f} - ${stock_data['Close'].max():.2f}")
        
        # Fetch peers
        print("[2/5] 👥 Fetching peer comparison...")
        peers = data_collector.fetch_peers_real_data(ticker)
        
        # Fetch macro data
        print("[3/5] 🌍 Fetching macroeconomic data...")
        macro_summary = data_collector.get_macro_summary()
        
        # Process technical indicators
        print("[4/5] 🔧 Processing technical indicators...")
        cleaned_data = data_cleaner.clean_stock_data(stock_data)
        technical_df = data_cleaner.calculate_technical_indicators(cleaned_data)
        financial_ratios = data_cleaner.calculate_financial_ratios(metrics)
        
        # Generate charts
        print("[5/5] 📈 Generating interactive charts...")
        
        # Price chart
        price_chart_json = visualizer.create_interactive_price_chart(technical_df, ticker)
        
        # Technical chart
        tech_chart_json = visualizer.create_interactive_technical_chart(technical_df, ticker)
        
        # Returns chart 
        returns_chart_json = visualizer.create_interactive_returns_chart(stock_data, ticker)
        
        # Peer chart
        peers_df = pd.DataFrame(peers) if peers else pd.DataFrame()
        peer_chart_json = visualizer.create_interactive_peer_chart(peers_df) if not peers_df.empty else json.dumps({'error': 'No peer data'})
        
        # AI Analysis
        current_price = price_data['current_price']
        price_target = ai_analyzer.generate_price_target(technical_df, current_price, metrics)
        ai_insights = ai_analyzer.generate_ai_insights(ticker, metrics, technical_df, price_target, current_price)
        sentiment = ai_analyzer.generate_sentiment_analysis(ticker)
        technical_outlook = ai_analyzer.generate_technical_outlook(technical_df)
        earnings_quality = ai_analyzer.generate_earning_quality_score(metrics)
        
        print(f"✅ Analysis complete!")
        print(f"   Price: ${current_price:.2f}")
        print(f"   Target: ${price_target.get('price_target', 0):.2f}")
        print(f"{'='*60}\n")
        
        # Prepare response
        response = {
            'ticker': ticker,
            'current_price': round(current_price, 2),
            'change_abs': round(price_data['change_abs'], 2),
            'change_pct': round(price_data['change_pct'], 2),
            'volume': price_data.get('volume', 0),
            'price_target': price_target.get('price_target', 0),
            'upside_pct': price_target.get('upside_pct', 0),
            
            # AI Insights
            'thesis': ai_insights.get('thesis', 'Analysis in progress...'),
            'risks': ai_insights.get('risks', ['Market volatility', 'Competition pressure']),
            'rating': ai_insights.get('rating', 'BUY'),
            'catalysts': ai_insights.get('catalysts', ['Product innovation', 'Market expansion']),
            'sentiment_score': sentiment.get('sentiment_score', 0.65),
            'sentiment_label': sentiment.get('sentiment_label', 'Bullish'),
            'technical_outlook': technical_outlook,
            'earnings_quality': earnings_quality,
            
            # Charts
            'price_chart_json': price_chart_json,
            'tech_chart_json': tech_chart_json,
            'returns_chart_json': returns_chart_json,
            'peer_chart_json': peer_chart_json,
            
            # Macro Data
            'macro_summary': macro_summary,
            
            # Metrics
            'metrics_row': [
                {'label': 'Market Cap', 'value': f"${metrics.get('market_cap', 0)/1e9:.1f}B" if metrics.get('market_cap') else 'N/A'},
                {'label': 'P/E (TTM)', 'value': f"{metrics.get('pe_ratio', 0):.1f}x" if metrics.get('pe_ratio') else 'N/A'},
                {'label': 'Forward P/E', 'value': f"{metrics.get('forward_pe', 0):.1f}x" if metrics.get('forward_pe') else 'N/A'},
                {'label': 'Div Yield', 'value': f"{metrics.get('dividend_yield', 0):.2f}%" if metrics.get('dividend_yield') else '0.00%'}
            ],
            'kpi_grid': [
                {'title': '52W High', 'value': f"${metrics.get('fifty_two_week_high', 0):,.0f}", 'sub': 'Upper bound'},
                {'title': '52W Low', 'value': f"${metrics.get('fifty_two_week_low', 0):,.0f}", 'sub': 'Lower bound'},
                {'title': 'Beta', 'value': f"{metrics.get('beta', 0):.2f}", 'sub': 'Volatility measure'},
                {'title': 'ROE', 'value': f"{financial_ratios.get('roe', 0)}%" if financial_ratios.get('roe') else 'N/A', 'sub': 'Return on Equity'}
            ],
            'peers': peers,
            'fred_available': data_collector.is_fred_available(),
            'timestamp': datetime.now().strftime('%d %b %Y, %H:%M:%S')
        }
        
        return jsonify(clean_for_json(response))
        
    except Exception as e:
        print(f"❌ Error analyzing: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_enabled': ai_analyzer.ai_enabled,
        'fred_available': data_collector.is_fred_available(),
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("=" * 70)
    print("🏦 GOLDMAN SACHS EQUITY RESEARCH DASHBOARD")
    print("=" * 70)
    print(f"\n🤖 Google AI Studio: {'✓ ENABLED' if ai_analyzer.ai_enabled else '✗ DISABLED'}")
    print(f"🌍 FRED Macro API: {'✓ CONNECTED' if data_collector.is_fred_available() else '⚠ NOT CONFIGURED'}")
    print("\n📊 Features:")
    print("   • Real-time stock data from Yahoo Finance")
    print("   • Interactive Plotly charts (zoom, pan, hover)")
    print("   • Technical indicators (RSI, MACD, Moving Averages)")
    print("   • Real macro data from FRED API")
    print("   • Real peer comparison from live market data")
    print("   • AI-powered investment thesis")
    print("\n🌐 Access the dashboard at: http://localhost:5001")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5001)