#!/bin/bash

echo "=========================================="
echo "Stock Analysis Dashboard"
echo "=========================================="

# Install dependencies
echo "Installing Python dependencies..."
pip install flask yfinance pandas numpy requests python-dotenv plotly

# Create output directory
mkdir -p output_charts

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "FRED_API_KEY=" > .env
    echo "GOOGLE_API_KEY=" >> .env
    echo "Please add your API keys to .env file"
fi

# Run the application
echo "Starting dashboard..."
python app.p