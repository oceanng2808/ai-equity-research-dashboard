"""
Module 2: Data Cleaning & Processing
Calculates real financial ratios from actual metrics
"""

import pandas as pd
import numpy as np
from typing import Dict


class DataCleaner:
    """Cleans and processes stock data for analysis"""
    
    def __init__(self):
        self.cleaning_log = []
    
    def clean_stock_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate stock price data - preserve all values"""
        df_clean = df.copy()
        
        # Remove any duplicate indices
        df_clean = df_clean[~df_clean.index.duplicated(keep='first')]
        
        # Forward fill then backward fill for any missing values
        df_clean = df_clean.ffill().bfill()
        
        self.cleaning_log.append(f"Cleaned data: {len(df_clean)} rows")
        
        return df_clean
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators for analysis - preserve original data"""
        df_tech = df.copy()
        
        if len(df_tech) == 0:
            return df_tech
        
        # Moving Averages (calculated from actual close prices)
        df_tech['MA_20'] = df_tech['Close'].rolling(window=20, min_periods=1).mean()
        df_tech['MA_50'] = df_tech['Close'].rolling(window=50, min_periods=1).mean()
        df_tech['MA_200'] = df_tech['Close'].rolling(window=200, min_periods=1).mean()
        
        # RSI (Relative Strength Index) - calculated from actual price changes
        delta = df_tech['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / loss
        df_tech['RSI'] = 100 - (100 / (1 + rs))
        df_tech['RSI'] = df_tech['RSI'].fillna(50)
        
        # Bollinger Bands (calculated from actual close prices)
        df_tech['BB_Middle'] = df_tech['Close'].rolling(window=20, min_periods=1).mean()
        bb_std = df_tech['Close'].rolling(window=20, min_periods=1).std()
        df_tech['BB_Upper'] = df_tech['BB_Middle'] + (bb_std * 2)
        df_tech['BB_Lower'] = df_tech['BB_Middle'] - (bb_std * 2)
        
        # MACD (calculated from actual close prices)
        exp12 = df_tech['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df_tech['Close'].ewm(span=26, adjust=False).mean()
        df_tech['MACD'] = exp12 - exp26
        df_tech['MACD_Signal'] = df_tech['MACD'].ewm(span=9, adjust=False).mean()
        
        # ATR (Average True Range) - volatility measure
        high_low = df_tech['High'] - df_tech['Low']
        high_close = (df_tech['High'] - df_tech['Close'].shift()).abs()
        low_close = (df_tech['Low'] - df_tech['Close'].shift()).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df_tech['ATR'] = true_range.rolling(window=14, min_periods=1).mean()
        
        # Volume indicators
        df_tech['Volume_MA'] = df_tech['Volume'].rolling(window=20, min_periods=1).mean()
        df_tech['Volume_Ratio'] = df_tech['Volume'] / df_tech['Volume_MA']
        
        # Price momentum (calculated from actual price changes)
        df_tech['Momentum_5d'] = df_tech['Close'].pct_change(5)
        df_tech['Momentum_20d'] = df_tech['Close'].pct_change(20)
        
        # Fill any remaining NaN values
        df_tech = df_tech.fillna(method='bfill').fillna(method='ffill')
        
        return df_tech
    
    def _calculate_roe(self, metrics: Dict) -> float:
        """
        Calculate Return on Equity from real data
        ROE = Net Income / Shareholders' Equity
        """
        net_income = metrics.get('net_income', 0)
        shareholders_equity = metrics.get('shareholders_equity', 0)
        
        if shareholders_equity and shareholders_equity > 0 and net_income:
            return round((net_income / shareholders_equity) * 100, 2)
        return None

    def calculate_financial_ratios(self, metrics: Dict) -> Dict:
        """
        Calculate real financial ratios from actual metrics
        No fixed/hardcoded numbers - all calculations use real data
        """
        # Get real values from metrics
        market_cap = metrics.get('market_cap', 0)
        pe_ratio = metrics.get('pe_ratio', 0)
        forward_pe = metrics.get('forward_pe', 0)
        eps = metrics.get('eps', 0)
        forward_eps = metrics.get('forward_eps', 0)
        dividend_yield = metrics.get('dividend_yield', 0)/100
        beta = metrics.get('beta', 0)
        revenue = metrics.get('revenue', 0)
        gross_margin = metrics.get('gross_margin', 0)
        profit_margin = metrics.get('profit_margin', 0)
        
        # Calculate Price-to-Sales ratio (if revenue available)
        price_to_sales = None
        if revenue and revenue > 0 and market_cap and market_cap > 0:
            price_to_sales = market_cap / revenue
        
        # Calculate PEG ratio (if both PE and growth estimate available)
        peg_ratio = None
        if pe_ratio and pe_ratio > 0:
            # Estimate growth from forward EPS vs trailing EPS
            estimated_growth = None
            if eps and forward_eps and eps > 0:
                estimated_growth = ((forward_eps - eps) / eps) * 100
            if estimated_growth and estimated_growth > 0:
                peg_ratio = pe_ratio / estimated_growth
        
        # Calculate Earnings Yield (inverse of PE)
        earnings_yield = None
        if pe_ratio and pe_ratio > 0:
            earnings_yield = (1 / pe_ratio) * 100
        
        # Determine valuation category based on real PE ratio
        valuation_category = "Fairly Valued"
        if pe_ratio:
            if pe_ratio < 15:
                valuation_category = "Undervalued"
            elif pe_ratio > 30:
                valuation_category = "Overvalued"
        
        # Determine growth category based on forward EPS
        growth_category = "Moderate Growth"
        if eps and forward_eps:
            eps_growth = ((forward_eps - eps) / eps) * 100 if eps > 0 else 0
            if eps_growth > 20:
                growth_category = "High Growth"
            elif eps_growth < 5:
                growth_category = "Low Growth"
        
        return {
            # Real calculated ratios
            'pe_ratio': round(pe_ratio, 2) if pe_ratio else None,
            'forward_pe': round(forward_pe, 2) if forward_pe else None,
            'peg_ratio': round(peg_ratio, 2) if peg_ratio else None,
            'price_to_sales': round(price_to_sales, 2) if price_to_sales else None,
            'earnings_yield': round(earnings_yield, 2) if earnings_yield else None,
            'dividend_yield': round(dividend_yield, 2) if dividend_yield else 0,
            'beta': round(beta, 2) if beta else None,
            
            # Real financial metrics
            'eps': round(eps, 2) if eps else None,
            'forward_eps': round(forward_eps, 2) if forward_eps else None,
            'market_cap_b': round(market_cap / 1e9, 2) if market_cap else None,
            
            # Real margin calculations
            'gross_margin': round(gross_margin, 1) if gross_margin else None,
            'profit_margin': round(profit_margin, 1) if profit_margin else None,
            
            # Analysis categories (derived from real data)
            'valuation_category': valuation_category,
            'growth_category': growth_category,
            
            # Calculate additional metrics
            'roe': self._calculate_roe(metrics),
            'debt_to_equity': metrics.get('debt_to_equity', None),
            'current_ratio': metrics.get('current_ratio', None)
        }