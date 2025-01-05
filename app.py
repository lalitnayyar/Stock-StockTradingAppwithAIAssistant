import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
import requests
import json
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Stock Trading App with AI Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/lalitnayyar/Stock-StockTradingAppwithAIAssistant',
        'Report a bug': 'https://github.com/lalitnayyar/Stock-StockTradingAppwithAIAssistant/issues',
        'About': 'Stock Trading App with AI Assistant - Created by Lalit Nayyar'
    }
)

# Initialize session state
if 'selected_stock' not in st.session_state:
    st.session_state['selected_stock'] = 'AAPL'
if 'prediction_days' not in st.session_state:
    st.session_state['prediction_days'] = 30
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = None
if 'stock_suggestions' not in st.session_state:
    st.session_state.stock_suggestions = []

def get_stock_suggestions(user_input):
    """Get stock symbol suggestions using DeepSeek AI"""
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        if not api_key:
            return "DeepSeek API key not found"

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a stock market expert. Provide relevant stock symbols based on user input."
                },
                {
                    "role": "user",
                    "content": f"""Based on the input '{user_input}', suggest up to 5 relevant stock symbols.
                    Format the response as a simple comma-separated list of symbols only.
                    Example: AAPL, MSFT, GOOGL"""
                }
            ],
            "temperature": 0.3,
            "max_tokens": 100
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            suggestions = response.json()['choices'][0]['message']['content'].strip()
            return [s.strip() for s in suggestions.split(',')]
        else:
            return []
            
    except Exception as e:
        st.error(f"Error getting suggestions: {str(e)}")
        return []

def get_deepseek_analysis(symbol, historical_data):
    """Get stock analysis using DeepSeek API"""
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        if not api_key:
            return "DeepSeek API key not found"

        # Prepare recent price data
        recent_prices = historical_data['Close'].tail(5).tolist()
        current_price = recent_prices[-1]
        price_change = ((current_price - recent_prices[0]) / recent_prices[0]) * 100
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional stock market analyst specializing in technical and fundamental analysis."
                },
                {
                    "role": "user",
                    "content": f"""Analyze the stock {symbol} with the following data:
                    Current Price: ${current_price:.2f}
                    5-day Price Change: {price_change:.2f}%
                    
                    Provide a detailed analysis including:
                    1. Technical Analysis
                    2. Market Sentiment
                    3. Risk Assessment (Low/Medium/High)
                    4. Price Target (7-day forecast)
                    5. Key Trading Indicators
                    
                    Format the response in a clear, structured manner."""
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Analysis Error: {str(e)}"

# [Rest of your existing functions remain the same]

def main():
    st.title("Stock Trading App with AI Assistant 📈")
    
    # Sidebar
    st.sidebar.header("Settings")
    
    # Add stock search with suggestions
    stock_search = st.sidebar.text_input("Search for stocks", value="", key="stock_search")
    
    if stock_search and len(stock_search) >= 2:
        with st.sidebar:
            with st.spinner('Getting suggestions...'):
                suggestions = get_stock_suggestions(stock_search)
                if suggestions:
                    selected_suggestion = st.selectbox(
                        "Select a stock",
                        suggestions,
                        key="stock_suggestions"
                    )
                    if selected_suggestion:
                        st.session_state['selected_stock'] = selected_suggestion
                        st.session_state.ai_analysis = None
    else:
        selected_stock = st.sidebar.text_input("Or enter stock symbol directly", 
                                             value=st.session_state['selected_stock'])
        if selected_stock != st.session_state['selected_stock']:
            st.session_state['selected_stock'] = selected_stock
            st.session_state.ai_analysis = None

    prediction_days = st.sidebar.slider("Prediction Days", 7, 60, st.session_state['prediction_days'])
    
    if prediction_days != st.session_state['prediction_days']:
        st.session_state['prediction_days'] = prediction_days
    
    # [Rest of your main function remains the same]

if __name__ == "__main__":
    main()