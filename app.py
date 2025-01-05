import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv
import requests
import re

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="Stock Trading App", layout="wide")

# Initialize API configuration
API_KEY = os.getenv('DEEPSEEK_API_KEY')
API_URL = "https://api.deepseek.com/v1/chat/completions"

# Initialize session state for stock symbol and auto search
if 'last_mentioned_symbol' not in st.session_state:
    st.session_state.last_mentioned_symbol = ""
if 'auto_search_symbol' not in st.session_state:
    st.session_state.auto_search_symbol = False

def extract_stock_symbols(text):
    """Extract stock symbols from text using regex patterns"""
    # Pattern for stock symbols: Capital letters with optional ^ prefix
    patterns = [
        r'\$([A-Z]{1,5})\b',  # Matches symbols with $ prefix
        r'\b([A-Z]{1,5})(?=\s*stock|\s*shares|\s*price|\s*symbol|\s*ticker)',  # Matches symbols followed by stock-related words
        r'\bsymbol[:\s]+([A-Z]{1,5})\b',  # Matches symbols after "symbol:"
        r'\bticker[:\s]+([A-Z]{1,5})\b'   # Matches symbols after "ticker:"
    ]
    
    symbols = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            symbol = match.group(1)
            # Verify if it's a valid stock symbol using yfinance
            try:
                ticker = yf.Ticker(symbol)
                if ticker.info:  # If we can get info, it's likely a valid symbol
                    symbols.append(symbol)
            except:
                continue
    
    return symbols[0] if symbols else None

def get_stock_data(symbol, period='1y'):
    """Fetch stock data using yfinance"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return None, None

def create_candlestick_chart(df):
    """Create a candlestick chart using plotly"""
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close'])])
    fig.update_layout(title='Stock Price Chart',
                     yaxis_title='Price',
                     xaxis_title='Date')
    return fig

def get_ai_response(prompt):
    """Get AI response using Deepseek API"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful financial advisor. When discussing stocks, always mention the stock symbol in the format: $SYMBOL"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        response_text = result['choices'][0]['message']['content']
        
        # Extract stock symbol if present
        symbol = extract_stock_symbols(response_text)
        if symbol:
            st.session_state.last_mentioned_symbol = symbol
            st.session_state.auto_search_symbol = True  # Set flag to trigger auto search
        
        return response_text
    except Exception as e:
        return f"Error: {str(e)}"

def display_stock_details(symbol):
    """Display stock details including chart and information"""
    if symbol:
        hist_data, stock_info = get_stock_data(symbol)
        
        if hist_data is not None and stock_info is not None:
            # Display basic info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", f"${stock_info.get('currentPrice', 'N/A')}")
            with col2:
                st.metric("Market Cap", f"${stock_info.get('marketCap', 'N/A'):,}")
            with col3:
                st.metric("Volume", f"{stock_info.get('volume', 'N/A'):,}")
            
            # Display chart
            st.plotly_chart(create_candlestick_chart(hist_data), use_container_width=True)
            
            # Additional stock info
            with st.expander("More Information"):
                st.write(f"**Company Name:** {stock_info.get('longName', 'N/A')}")
                st.write(f"**Sector:** {stock_info.get('sector', 'N/A')}")
                st.write(f"**Industry:** {stock_info.get('industry', 'N/A')}")
                st.write(f"**52 Week High:** ${stock_info.get('fiftyTwoWeekHigh', 'N/A')}")
                st.write(f"**52 Week Low:** ${stock_info.get('fiftyTwoWeekLow', 'N/A')}")
            return True
    return False

# Sidebar for search
st.sidebar.title("Stock Search")
search_option = st.sidebar.radio("Search by:", ["Symbol", "Company Name"])
search_query = st.sidebar.text_input("Enter search term:")

# Main content
st.title("Stock Trading Application")

# AI Chat Section
st.header("AI Financial Assistant")
user_question = st.text_input("Ask anything about stocks or trading:")
if user_question:
    if not API_KEY:
        st.warning("Please set up your API key in the .env file")
    else:
        with st.spinner('Getting AI response...'):
            ai_response = get_ai_response(user_question)
            st.write(ai_response)
            
            # If a new symbol was found in the response, show details
            if st.session_state.last_mentioned_symbol:
                st.success(f"📈 Loading data for {st.session_state.last_mentioned_symbol}...")
                displayed = display_stock_details(st.session_state.last_mentioned_symbol)
                if not displayed:
                    st.error(f"Could not load data for {st.session_state.last_mentioned_symbol}")

# Display stock details from manual search if provided
if search_query:
    if search_option == "Company Name":
        symbol = search_query  # In real app, implement company name to symbol conversion
    else:
        symbol = search_query.upper()
    display_stock_details(symbol)
