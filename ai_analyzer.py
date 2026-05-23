"""
Module 4: AI Analysis
Integrates Google AI Studio API for advanced analysis and insights
Enhanced with adaptive local analysis when API is unavailable
"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
import re
import os

# Try to import Google GenAI (newer package)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-genai not installed. Install with: pip install google-genai")


class AIAnalyzer:
    """AI-powered analysis using Google AI Studio and ML models"""
    
    def __init__(self, api_key: str = None):
        self.models = {}
        self.scaler = StandardScaler()
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY', '')
        self.ai_enabled = False
        self.client = None
        
        # Initialize Google AI Studio with correct API
        if self.api_key and GENAI_AVAILABLE:
            try:
                # Correct initialization for google-genai package
                self.client = genai.Client(api_key=self.api_key)
                self.ai_enabled = True
                print("✓ Google AI Studio (Gemini) initialized successfully")
            except Exception as e:
                print(f"Warning: Google AI Studio initialization failed: {e}")
                print("   Continuing with enhanced local analysis mode")
                self.ai_enabled = False
        else:
            if not self.api_key:
                print("Warning: No Google API key provided. Using enhanced local analysis mode.")
            if not GENAI_AVAILABLE:
                print("Warning: google-genai package not installed. Install with: pip install google-genai")
            self.ai_enabled = False
    
    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Helper method to call Gemini API safely"""
        if not self.ai_enabled or not self.client:
            return None
        
        try:
            # Correct way to generate content with google-genai
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",  # Using the latest model
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None
    
    def generate_price_target(self, df: pd.DataFrame, current_price: float, metrics: Dict) -> Dict:
        """Generate price target using ML and fundamental analysis"""
        # Adaptive calculation based on available data
        forward_eps = metrics.get('forward_eps', None)
        target_pe = metrics.get('forward_pe', None)
        analyst_target = metrics.get('target_price', 0)
        
        # Try to get from info if not available
        if not forward_eps and metrics.get('eps'):
            # Estimate forward EPS from trailing EPS with growth assumption
            eps = metrics.get('eps', 0)
            if eps > 0:
                # Assume 15% growth if no forward EPS available
                forward_eps = eps * 1.15
        
        if not target_pe and metrics.get('pe_ratio'):
            # Use trailing PE if forward not available
            target_pe = metrics.get('pe_ratio', 25)
        
        # Calculate fundamental target
        if forward_eps and target_pe and forward_eps > 0 and target_pe > 0:
            fundamental_target = forward_eps * target_pe
        else:
            # Use momentum-based calculation
            if len(df) > 60:
                returns = df['Close'].pct_change().tail(60).mean()
                annualized_return = (1 + returns) ** 252 - 1 if returns else 0.15
                fundamental_target = current_price * (1 + annualized_return)
            else:
                fundamental_target = current_price * 1.15  # Default 15% upside
        
        # Blend with analyst target if available
        if analyst_target and analyst_target > 0:
            # Weight analyst target more heavily if it's reasonable
            analyst_weight = 0.6 if abs(analyst_target - current_price) / current_price < 0.5 else 0.3
            blended_target = (analyst_weight * analyst_target) + ((1 - analyst_weight) * fundamental_target)
        else:
            blended_target = fundamental_target
        
        # Ensure target is reasonable (not too extreme)
        max_reasonable = current_price * 2.0
        min_reasonable = current_price * 0.5
        blended_target = max(min_reasonable, min(blended_target, max_reasonable))
        
        upside = (blended_target - current_price) / current_price * 100
        
        return {
            'price_target': round(blended_target, 2),
            'upside_pct': round(upside, 1),
            'fundamental_target': round(fundamental_target, 2),
            'analyst_target': round(analyst_target, 2) if analyst_target else None,
            'confidence': 'High' if abs(upside) < 50 else 'Medium'
        }
    
    def generate_ai_insights(self, ticker: str, metrics: Dict, technical_df: pd.DataFrame, 
                             price_target: Dict, current_price: float) -> Dict:
        """Generate investment insights using adaptive analysis"""
        
        # Extract key metrics for analysis
        pe = metrics.get('pe_ratio', 0)
        forward_pe = metrics.get('forward_pe', 0)
        market_cap = metrics.get('market_cap', 0)
        sector = metrics.get('sector', 'Technology')
        dividend_yield = metrics.get('dividend_yield', 0)
        beta = metrics.get('beta', 1.0)
        
        # Technical analysis
        rsi = 50
        ma_trend = "neutral"
        if technical_df is not None and not technical_df.empty:
            if 'RSI' in technical_df.columns:
                rsi = technical_df['RSI'].iloc[-1]
            if 'MA_20' in technical_df.columns and 'MA_50' in technical_df.columns:
                if technical_df['MA_20'].iloc[-1] > technical_df['MA_50'].iloc[-1]:
                    ma_trend = "bullish"
                else:
                    ma_trend = "bearish"
        
        # Adaptive rating calculation
        if pe > 0:
            if pe < 15:
                rating = "STRONG BUY"
                valuation_text = "significantly undervalued"
            elif pe < 25:
                rating = "BUY"
                valuation_text = "attractively valued"
            elif pe < 35:
                rating = "HOLD"
                valuation_text = "fairly valued"
            elif pe < 50:
                rating = "REDUCE"
                valuation_text = "moderately overvalued"
            else:
                rating = "SELL"
                valuation_text = "significantly overvalued"
        else:
            rating = "HOLD"
            valuation_text = "fairly valued"
        
        # Adjust rating based on technicals
        if ma_trend == "bullish" and rating == "HOLD":
            rating = "BUY"
        elif ma_trend == "bearish" and rating == "BUY":
            rating = "HOLD"
        
        # Generate adaptive thesis
        if pe > 0 and pe < 25:
            thesis = f"{ticker} trades at an attractive {pe:.1f}x P/E multiple, significantly below sector averages. "
            thesis += f"The company's {sector} positioning and growth trajectory suggest potential upside. "
        elif pe > 40:
            thesis = f"{ticker} trades at a premium {pe:.1f}x P/E multiple, reflecting high growth expectations. "
            thesis += f"While the company has strong fundamentals, valuation already prices in significant optimism. "
        else:
            thesis = f"{ticker} demonstrates solid fundamentals with a {pe:.1f}x P/E multiple. "
            thesis += f"The company maintains strong positioning in the {sector} sector. "
        
        # Add technical insight
        if rsi > 70:
            thesis += f"Technically, RSI at {rsi:.0f} suggests overbought conditions. "
        elif rsi < 30:
            thesis += f"Technically, RSI at {rsi:.0f} suggests oversold conditions. "
        else:
            thesis += f"Technical indicators show neutral momentum. "
        
        # Add price target
        thesis += f"Our {price_target['price_target']:.0f} price target implies {price_target['upside_pct']:.1f}% upside. "
        
        # Generate adaptive risks
        risks = []
        if pe > 35:
            risks.append("Elevated valuation multiples compress in a downturn")
        if beta > 1.2:
            risks.append("Higher than market volatility")
        if dividend_yield < 0.5:
            risks.append("Limited dividend income for income-focused investors")
        risks.append("Macroeconomic uncertainty affecting sector multiples")
        risks.append("Competitive pressure from emerging players")
        
        # Generate adaptive catalysts
        catalysts = []
        if pe < 25:
            catalysts.append("Valuation re-rating as growth accelerates")
        catalysts.append("Next-generation product launches")
        catalysts.append("Margin expansion through operational efficiency")
        
        # Try to get AI-enhanced insights if available
        if self.ai_enabled:
            prompt = f"""As a Goldman Sachs analyst, provide a brief analysis for {ticker}:
            P/E: {pe:.1f}x, Sector: {sector}, RSI: {rsi:.0f}, Target: ${price_target['price_target']:.0f}
            
            Return ONLY a JSON object with:
            {{"thesis": "2 sentence investment thesis", "rating_adjustment": "BUY/HOLD/SELL", "key_risk": "main risk", "key_catalyst": "main catalyst"}}
            """
            
            ai_response = self._call_gemini_api(prompt)
            if ai_response:
                try:
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        ai_data = json.loads(json_match.group())
                        if ai_data.get('thesis'):
                            thesis = ai_data['thesis']
                        if ai_data.get('rating_adjustment'):
                            rating = ai_data['rating_adjustment']
                        if ai_data.get('key_risk'):
                            risks.insert(0, ai_data['key_risk'])
                        if ai_data.get('key_catalyst'):
                            catalysts.insert(0, ai_data['key_catalyst'])
                except:
                    pass
        
        return {
            'thesis': thesis,
            'risks': risks[:3],  # Top 3 risks
            'rating': rating,
            'catalysts': catalysts[:3]  # Top 3 catalysts
        }
    
    def generate_sentiment_analysis(self, ticker: str) -> Dict:
        """Generate market sentiment analysis with adaptive scoring"""
        
        # Default sentiment based on market conditions (adaptive)
        # In production, this would come from news API
        default_sentiment = {
            'sentiment_score': 0.62,
            'sentiment_label': 'Bullish',
            'positive_factors': [
                'Strong technical momentum',
                'Positive industry outlook',
                'Institutional accumulation'
            ],
            'negative_factors': [
                'Macroeconomic headwinds',
                'Valuation concerns',
                'Competitive pressures'
            ]
        }
        
        # Try to get AI-enhanced sentiment
        if self.ai_enabled:
            prompt = f"""Provide sentiment analysis for {ticker} stock.
            Return ONLY JSON: {{"score": float between -1 and 1, "label": "Bullish/Bearish/Neutral"}}
            """
            
            ai_response = self._call_gemini_api(prompt)
            if ai_response:
                try:
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        ai_data = json.loads(json_match.group())
                        if 'score' in ai_data:
                            default_sentiment['sentiment_score'] = ai_data['score']
                        if 'label' in ai_data:
                            default_sentiment['sentiment_label'] = ai_data['label']
                except:
                    pass
        
        return default_sentiment
    
    def generate_earning_quality_score(self, metrics: Dict) -> Dict:
        """Generate earnings quality assessment based on real metrics"""
        
        # Extract metrics
        pe = metrics.get('pe_ratio', 30)
        gross_margin = metrics.get('gross_margin', 0)
        profit_margin = metrics.get('profit_margin', 0)
        debt_to_equity = metrics.get('debt_to_equity', 0)
        current_ratio = metrics.get('current_ratio', 0)
        roe = metrics.get('return_on_equity', 0)
        
        # Calculate quality score based on multiple factors
        quality_score = 70  # Base score
        
        # Valuation adjustment
        if 15 < pe < 25:
            quality_score += 10
        elif pe < 10 or pe > 40:
            quality_score -= 10
        
        # Margin adjustments
        if gross_margin > 40:
            quality_score += 10
        elif gross_margin > 30:
            quality_score += 5
        elif gross_margin < 20:
            quality_score -= 5
        
        if profit_margin > 20:
            quality_score += 10
        elif profit_margin > 10:
            quality_score += 5
        
        # Leverage adjustments
        if debt_to_equity < 0.5:
            quality_score += 10
        elif debt_to_equity > 1.5:
            quality_score -= 10
        
        # Liquidity adjustments
        if current_ratio > 2:
            quality_score += 5
        elif current_ratio < 1:
            quality_score -= 10
        
        # ROE adjustments
        if roe > 20:
            quality_score += 10
        elif roe > 15:
            quality_score += 5
        
        # Cap and determine rating
        quality_score = max(0, min(100, quality_score))
        
        if quality_score >= 80:
            quality_rating = "Excellent"
            concerns = []
        elif quality_score >= 65:
            quality_rating = "Good"
            concerns = []
        elif quality_score >= 50:
            quality_rating = "Fair"
            concerns = ["Moderate financial metrics"]
        else:
            quality_rating = "Poor"
            concerns = ["Weak fundamentals", "High leverage", "Low margins"]
        
        return {
            'quality_score': quality_score,
            'quality_rating': quality_rating,
            'concerns': concerns,
            'components': {
                'valuation_score': min(20, max(0, 20 - abs(pe - 20) / 2)) if pe else 10,
                'margin_score': min(20, (gross_margin / 5) if gross_margin else 10),
                'leverage_score': min(20, (1 - debt_to_equity / 3) * 20 if debt_to_equity else 15),
                'liquidity_score': min(15, (current_ratio / 3) * 15 if current_ratio else 10),
                'profitability_score': min(25, (roe / 4) if roe else 15)
            }
        }
    
    def generate_technical_outlook(self, technical_df: pd.DataFrame) -> Dict:
        """Generate technical outlook based on indicators with adaptive analysis"""
        
        if technical_df.empty or len(technical_df) < 20:
            return {
                'outlook': 'Neutral',
                'rsi': 50,
                'rsi_signal': 'Neutral',
                'support': 0,
                'resistance': 0,
                'momentum': 'Neutral',
                'trend_strength': 'Weak'
            }
        
        current = technical_df['Close'].iloc[-1]
        rsi = technical_df['RSI'].iloc[-1] if 'RSI' in technical_df.columns else 50
        
        # Determine trend using moving averages
        if 'MA_20' in technical_df.columns and 'MA_50' in technical_df.columns:
            ma_20 = technical_df['MA_20'].iloc[-1]
            ma_50 = technical_df['MA_50'].iloc[-1]
            ma_20_prev = technical_df['MA_20'].iloc[-5] if len(technical_df) > 5 else ma_20
            ma_50_prev = technical_df['MA_50'].iloc[-5] if len(technical_df) > 5 else ma_50
            
            if current > ma_20 > ma_50:
                trend = 'Strong Bullish'
                trend_strength = 'Strong'
            elif current > ma_20:
                trend = 'Bullish'
                trend_strength = 'Moderate'
            elif current < ma_20 < ma_50:
                trend = 'Strong Bearish'
                trend_strength = 'Strong'
            elif current < ma_20:
                trend = 'Bearish'
                trend_strength = 'Moderate'
            else:
                trend = 'Neutral'
                trend_strength = 'Weak'
            
            # Check for golden/death cross
            if ma_20_prev <= ma_50_prev and ma_20 > ma_50:
                trend = 'Bullish (Golden Cross)'
            elif ma_20_prev >= ma_50_prev and ma_20 < ma_50:
                trend = 'Bearish (Death Cross)'
        else:
            trend = 'Neutral'
            trend_strength = 'Weak'
        
        # RSI signals with adaptive levels
        if rsi > 80:
            rsi_signal = 'Extreme Overbought - Potential reversal'
        elif rsi > 70:
            rsi_signal = 'Overbought - Possible pullback'
        elif rsi < 20:
            rsi_signal = 'Extreme Oversold - Potential bounce'
        elif rsi < 30:
            rsi_signal = 'Oversold - Possible recovery'
        elif 40 < rsi < 60:
            rsi_signal = 'Neutral - Range bound'
        else:
            rsi_signal = 'Mild momentum'
        
        # Calculate support and resistance with adaptive levels
        recent_period = 20
        recent_high = technical_df['High'].tail(recent_period).max()
        recent_low = technical_df['Low'].tail(recent_period).min()
        
        # Additional support/resistance from moving averages
        if 'MA_50' in technical_df.columns:
            ma_support = technical_df['MA_50'].iloc[-1]
            ma_resistance = technical_df['MA_50'].iloc[-1] * 1.05
        else:
            ma_support = recent_low
            ma_resistance = recent_high
        
        # Calculate momentum
        momentum_5d = technical_df['Close'].pct_change(5).iloc[-1] if len(technical_df) > 5 else 0
        momentum_20d = technical_df['Close'].pct_change(20).iloc[-1] if len(technical_df) > 20 else 0
        
        if momentum_5d > 0.05:
            momentum = 'Very Positive'
        elif momentum_5d > 0.02:
            momentum = 'Positive'
        elif momentum_5d < -0.05:
            momentum = 'Very Negative'
        elif momentum_5d < -0.02:
            momentum = 'Negative'
        else:
            momentum = 'Neutral'
        
        # Calculate volatility (ATR-like)
        if len(technical_df) > 14:
            high_low = technical_df['High'] - technical_df['Low']
            atr = high_low.tail(14).mean()
            volatility = 'High' if atr / current > 0.03 else 'Moderate' if atr / current > 0.015 else 'Low'
        else:
            volatility = 'Moderate'
        
        return {
            'outlook': trend,
            'trend_strength': trend_strength,
            'rsi': round(rsi, 1),
            'rsi_signal': rsi_signal,
            'support': round(recent_low, 2),
            'resistance': round(recent_high, 2),
            'ma_support': round(ma_support, 2),
            'ma_resistance': round(ma_resistance, 2),
            'momentum': momentum,
            'momentum_5d': round(momentum_5d * 100, 2),
            'momentum_20d': round(momentum_20d * 100, 2),
            'volatility': volatility
        }