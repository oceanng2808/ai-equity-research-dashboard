"""
Configuration settings for the Stock Analysis Dashboard
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    FRED_API_KEY = os.getenv('FRED_API_KEY', '')
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5001
    
    # Data Settings
    DEFAULT_TICKER = 'NVDA'
    DATA_PERIOD = '1y'