"""
Module 1: Data Collection
Fetches REAL-TIME stock data, financial metrics, market information, and macroeconomic data
Uses Yahoo Finance for stocks and FRED API for macro indicators
NO SIMULATED DATA - All data is real from APIs
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class DataCollector:
    """Handles all REAL data fetching operations from Yahoo Finance and FRED API"""
    
    def __init__(self, fred_api_key: str = None):
        """
        Initialize data collector with FRED API key
        Get free key from: https://fred.stlouisfed.org/docs/api/api_key.html
        """
        self.fred_api_key = fred_api_key or os.getenv('FRED_API_KEY', '')
        self.fred_base_url = 'https://api.stlouisfed.org/fred/series/observations'
        
    def is_fred_available(self) -> bool:
        """Check if FRED API key is configured"""
        return bool(self.fred_api_key) and self.fred_api_key != ''
    
    # ========================================================================
    # STOCK DATA METHODS (Yahoo Finance)
    # ========================================================================
    
    def fetch_stock_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetch historical price data for a given ticker
        Raises exception if data cannot be fetched (no simulated fallback)
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                raise ValueError(f"No historical data found for ticker '{ticker}'. Please check the ticker symbol.")
            
            return data
            
        except Exception as e:
            raise Exception(f"Failed to fetch stock data for {ticker}: {str(e)}")
    
    def fetch_current_price(self, ticker: str) -> Dict:
        """
        Fetch current price and change information from real-time data
        Raises exception if data cannot be fetched
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="5d")
            
            if len(data) < 2:
                # Try with longer period if 5 days not available
                data = stock.history(period="1mo")
                if len(data) < 2:
                    raise ValueError(f"Insufficient price data for {ticker}")
            
            current = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            
            return {
                'current_price': float(current),
                'prev_close': float(prev_close),
                'change_abs': float(current - prev_close),
                'change_pct': float((current - prev_close) / prev_close * 100),
                'volume': int(data['Volume'].iloc[-1]),
                'high_52w': None,  # Will be filled from info
                'low_52w': None
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch current price for {ticker}: {str(e)}")
    
    def fetch_financial_metrics(self, ticker: str) -> Dict:
        """
        Fetch fundamental financial metrics from yfinance info
        Raises exception if data cannot be fetched
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info:
                raise ValueError(f"No financial information found for ticker '{ticker}'")
            
            # Get 52-week high/low from history if not in info
            hist = stock.history(period="1y")
            fifty_two_week_high = info.get('fiftyTwoWeekHigh', hist['High'].max() if not hist.empty else 0)
            fifty_two_week_low = info.get('fiftyTwoWeekLow', hist['Low'].min() if not hist.empty else 0)
            
            return {
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0) if info.get('trailingPE', 0) > 0 else None,
                'forward_pe': info.get('forwardPE', 0) if info.get('forwardPE', 0) > 0 else None,
                'eps': info.get('trailingEps', 0),
                'forward_eps': info.get('forwardEps', 0),
                'dividend_yield': (info.get('dividendYield', 0) * 100) if info.get('dividendYield') else 0,
                'beta': info.get('beta', 1.0),
                'target_price': info.get('targetMeanPrice', 0),
                'recommendation': info.get('recommendationKey', 'hold'),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'fifty_two_week_high': fifty_two_week_high,
                'fifty_two_week_low': fifty_two_week_low,
                'short_name': info.get('shortName', ticker),
                'long_name': info.get('longName', ticker),
                'revenue': info.get('totalRevenue', 0),
                'gross_margin': info.get('grossMargins', 0) * 100 if info.get('grossMargins') else 0,
                'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch financial metrics for {ticker}: {str(e)}")
    
    def fetch_peers_real_data(self, ticker: str) -> List[Dict]:
        """
        Fetch REAL peer comparison data from Yahoo Finance
        Dynamically finds peers based on industry and fetches their current data
        """
        try:
            # First get the ticker's industry
            stock = yf.Ticker(ticker)
            industry = stock.info.get('industry', '')
            sector = stock.info.get('sector', 'Technology')
            
            # Map industries to peer tickers (real-time lookup)
            industry_peers = {
                'Semiconductors': ['NVDA', 'AMD', 'INTC', 'AVGO', 'TXN', 'QCOM', 'MU'],
                'Software—Infrastructure': ['MSFT', 'ORCL', 'CRM', 'NOW', 'ADBE', 'PANW'],
                'Software—Application': ['MSFT', 'ADBE', 'SAP', 'INTU', 'CRM', 'SNOW'],
                'Consumer Electronics': ['AAPL', 'SONY', 'LG', 'HEAR', 'GPRO'],
                'Internet Content & Information': ['GOOGL', 'META', 'BIDU', 'SNAP', 'PINS', 'RDDT'],
                'Oil & Gas Integrated': ['XOM', 'CVX', 'BP', 'SHEL', 'TTE', 'COP'],
                'Banks—Regional': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS'],
                'Pharmaceuticals': ['JNJ', 'PFE', 'MRK', 'ABBV', 'BMY', 'LLY'],
                'Retail': ['WMT', 'TGT', 'COST', 'AMZN', 'HD', 'LOW'],
                'Auto Manufacturers': ['TSLA', 'F', 'GM', 'TM', 'HMC', 'RIVN'],
                'Aerospace & Defense': ['BA', 'LMT', 'NOC', 'GD', 'RTX', 'LHX'],
                'Healthcare Plans': ['UNH', 'CVS', 'CI', 'HUM', 'ELV']
            }
            
            # Find matching industry or use sector-based defaults
            peer_tickers = []
            for ind, tickers in industry_peers.items():
                if ind.lower() in industry.lower():
                    peer_tickers = tickers
                    break
            
            # Sector-based fallback if no industry match
            if not peer_tickers:
                sector_peers = {
                    'Technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'CRM', 'ADBE'],
                    'Financial': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C'],
                    'Healthcare': ['JNJ', 'PFE', 'MRK', 'ABBV', 'UNH', 'LLY'],
                    'Energy': ['XOM', 'CVX', 'BP', 'SHEL', 'COP', 'EOG'],
                    'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'NKE', 'SBUX', 'MCD'],
                    'Consumer Defensive': ['PG', 'KO', 'PEP', 'COST', 'WMT', 'PM']
                }
                peer_tickers = sector_peers.get(sector, ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'])
            
            # Remove current ticker and limit to 5 peers
            peer_tickers = [p for p in peer_tickers if p != ticker][:5]
            
            result = []
            for p_ticker in peer_tickers:
                try:
                    peer_stock = yf.Ticker(p_ticker)
                    peer_info = peer_stock.info
                    
                    # Get YTD performance
                    hist = peer_stock.history(period="ytd")
                    ytd_perf = 0
                    if len(hist) >= 2:
                        start_price = hist['Close'].iloc[0]
                        end_price = hist['Close'].iloc[-1]
                        ytd_perf = ((end_price - start_price) / start_price) * 100
                    
                    # Get market cap in billions
                    mkt_cap = peer_info.get('marketCap', 0)
                    mkt_cap_b = mkt_cap / 1e9 if mkt_cap else 0
                    
                    # Get forward P/E
                    forward_pe = peer_info.get('forwardPE', 0)
                    if forward_pe == 0 or forward_pe is None:
                        forward_pe = peer_info.get('trailingPE', 0)
                    
                    result.append({
                        'company': peer_info.get('shortName', p_ticker),
                        'ticker': p_ticker,
                        'mkt_cap': f"{mkt_cap_b:.1f}B" if mkt_cap_b > 0 else 'N/A',
                        'mkt_cap_b': mkt_cap_b,
                        'pe_ntm': round(forward_pe, 1) if forward_pe and forward_pe > 0 else '--',
                        'ytd_perf': round(ytd_perf, 1)
                    })
                except Exception as e:
                    print(f"Could not fetch peer data for {p_ticker}: {e}")
                    continue
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to fetch peer data: {str(e)}")
    
    def fetch_historical_chart_data(self, ticker: str, period: str = "6mo") -> Dict:
        """
        Fetch historical data formatted for interactive charts
        Returns data for Chart.js visualization
        """
        try:
            df = self.fetch_stock_data(ticker, period)
            
            if df.empty:
                raise ValueError(f"No historical data found for {ticker}")
            
            # Prepare data for Chart.js
            dates = df.index.strftime('%Y-%m-%d').tolist()
            prices = [float(x) for x in df['Close'].tolist()]
            volumes = [int(x) for x in df['Volume'].tolist()]
            
            # Calculate RSI
            rsi = self._calculate_rsi(df['Close'])
            rsi_list = [float(x) if not pd.isna(x) else 50 for x in rsi.tolist()]
            
            # Calculate MACD
            macd, signal, hist = self._calculate_macd(df['Close'])
            
            # Calculate Moving Averages
            ma20 = [float(x) if not pd.isna(x) else None for x in df['Close'].rolling(20).mean().tolist()]
            ma50 = [float(x) if not pd.isna(x) else None for x in df['Close'].rolling(50).mean().tolist()]
            
            return {
                'dates': dates,
                'prices': prices,
                'volumes': volumes,
                'rsi': rsi_list,
                'macd': [float(x) if not pd.isna(x) else 0 for x in macd],
                'signal': [float(x) if not pd.isna(x) else 0 for x in signal],
                'histogram': [float(x) if not pd.isna(x) else 0 for x in hist],
                'ma20': ma20,
                'ma50': ma50
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch historical chart data for {ticker}: {str(e)}")
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List, List, List]:
        """Calculate MACD indicator"""
        exp_fast = prices.ewm(span=fast, adjust=False).mean()
        exp_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = exp_fast - exp_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd.tolist(), signal_line.tolist(), histogram.tolist()
    
    # ========================================================================
    # MACROECONOMIC DATA METHODS (FRED API)
    # ========================================================================
    
    def fetch_all_macro_data(self) -> Dict:
        """
        Fetch all macroeconomic indicators in one call
        Uses ONLY real FRED API data - no simulated fallbacks
        """
        macro_data = {
            'fred_available': self.is_fred_available(),
            'timestamp': datetime.now().isoformat()
        }
        
        if not self.is_fred_available():
            macro_data['error'] = 'FRED_API_KEY not configured. Get free key from https://fred.stlouisfed.org/docs/api/api_key.html'
            return macro_data
        
        # Fetch GDP data (returns None if fails)
        try:
            result = self._fetch_fred_series('GDPC1', limit=20)
            if result.get('values'):
                macro_data['gdp'] = result
            else:
                macro_data['gdp'] = {'error': True, 'message': 'No data returned from FRED'}
        except Exception as e:
            macro_data['gdp'] = {'error': True, 'message': str(e)}
        
        # Fetch CPI data
        try:
            result = self._fetch_fred_series('CPIAUCSL', limit=24)
            if result.get('values'):
                # Calculate YoY inflation
                if len(result['values']) >= 13:
                    current = result['values'][-1]
                    year_ago = result['values'][-13]
                    if year_ago != 0:
                        macro_data['inflation_yoy'] = ((current - year_ago) / year_ago) * 100
                macro_data['cpi'] = result
            else:
                macro_data['cpi'] = {'error': True, 'message': 'No data returned from FRED'}
        except Exception as e:
            macro_data['cpi'] = {'error': True, 'message': str(e)}
        
        # Fetch Fed Funds Rate
        try:
            result = self._fetch_fred_series('FEDFUNDS', limit=12)
            if result.get('values'):
                macro_data['fed_funds'] = result
            else:
                macro_data['fed_funds'] = {'error': True, 'message': 'No data returned from FRED'}
        except Exception as e:
            macro_data['fed_funds'] = {'error': True, 'message': str(e)}
        
        # Fetch Unemployment Rate
        try:
            result = self._fetch_fred_series('UNRATE', limit=12)
            if result.get('values'):
                macro_data['unemployment'] = result
            else:
                macro_data['unemployment'] = {'error': True, 'message': 'No data returned from FRED'}
        except Exception as e:
            macro_data['unemployment'] = {'error': True, 'message': str(e)}
        
        # Fetch Treasury Yield
        try:
            result = self._fetch_fred_series('DGS10', limit=12)
            if result.get('values'):
                macro_data['treasury_10y'] = result
            else:
                macro_data['treasury_10y'] = {'error': True, 'message': 'No data returned from FRED'}
        except Exception as e:
            macro_data['treasury_10y'] = {'error': True, 'message': str(e)}
        
        return macro_data
    
    def get_macro_summary(self) -> Dict:
        """
        Get simplified macro summary for dashboard display
        Uses ONLY real FRED API data - no simulated fallbacks
        """
        if not self.is_fred_available():
            return {
                'fred_available': False,
                'error': 'FRED_API_KEY not configured. Get free key from https://fred.stlouisfed.org/docs/api/api_key.html'
            }
        
        try:
            # ========== GDP (GDPC1) ==========
            gdp_params = {
                'series_id': 'GDPC1',
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'sort_order': 'asc',
                'limit': 20
            }
            gdp_resp = requests.get(self.fred_base_url, params=gdp_params, timeout=10)
            gdp_data = gdp_resp.json()
            
            gdp_values = []
            for obs in gdp_data.get('observations', []):
                if obs['value'] != '.' and obs['value'] != '':
                    gdp_values.append(float(obs['value']))
            
            gdp_growth = None
            if len(gdp_values) >= 2:
                current_gdp = gdp_values[-1]
                prev_gdp = gdp_values[-2]
                if prev_gdp != 0:
                    gdp_growth = ((current_gdp - prev_gdp) / prev_gdp) * 100
            
            # ========== CPI (CPIAUCSL) ==========
            cpi_params = {
                'series_id': 'CPIAUCSL',
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'sort_order': 'asc',
                'limit': 24
            }
            cpi_resp = requests.get(self.fred_base_url, params=cpi_params, timeout=10)
            cpi_data = cpi_resp.json()
            
            cpi_values = []
            for obs in cpi_data.get('observations', []):
                if obs['value'] != '.' and obs['value'] != '':
                    cpi_values.append(float(obs['value']))
            
            # Calculate YoY inflation (current vs 12 months ago)
            inflation_rate = None
            if len(cpi_values) >= 13:
                current_cpi = cpi_values[-1]
                year_ago_cpi = cpi_values[-13]
                if year_ago_cpi != 0:
                    inflation_rate = ((current_cpi - year_ago_cpi) / year_ago_cpi) * 100
                    print(f"CPI Debug: Current={current_cpi}, YearAgo={year_ago_cpi}, Inflation={inflation_rate:.2f}%")
            
            # ========== Federal Funds Rate ==========
            fed_params = {
                'series_id': 'FEDFUNDS',
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': 1
            }
            fed_resp = requests.get(self.fred_base_url, params=fed_params, timeout=10)
            fed_data = fed_resp.json()
            
            fed_rate = None
            for obs in fed_data.get('observations', []):
                if obs['value'] != '.' and obs['value'] != '':
                    fed_rate = float(obs['value'])
                    break
            
            # ========== Unemployment Rate ==========
            unemp_params = {
                'series_id': 'UNRATE',
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': 1
            }
            unemp_resp = requests.get(self.fred_base_url, params=unemp_params, timeout=10)
            unemp_data = unemp_resp.json()
            
            unemployment = None
            for obs in unemp_data.get('observations', []):
                if obs['value'] != '.' and obs['value'] != '':
                    unemployment = float(obs['value'])
                    break
            
            # ========== 10-Year Treasury Yield ==========
            treasury_params = {
                'series_id': 'DGS10',
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': 1
            }
            treasury_resp = requests.get(self.fred_base_url, params=treasury_params, timeout=10)
            treasury_data = treasury_resp.json()
            
            treasury_rate = None
            for obs in treasury_data.get('observations', []):
                if obs['value'] != '.' and obs['value'] != '':
                    treasury_rate = float(obs['value'])
                    break
            
            # Return ONLY real data (None for missing values)
            return {
                'gdp_growth': round(gdp_growth, 1) if gdp_growth is not None else None,
                'inflation_rate': round(inflation_rate, 1) if inflation_rate is not None else None,
                'fed_rate': round(fed_rate, 2) if fed_rate is not None else None,
                'unemployment': round(unemployment, 1) if unemployment is not None else None,
                'treasury_rate': round(treasury_rate, 2) if treasury_rate is not None else None,
                'fred_available': True
            }
            
        except Exception as e:
            print(f"Macro summary error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'fred_available': False,
                'error': str(e)
            }