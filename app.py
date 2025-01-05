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
st.set_page_config(page_title="Stock StarLink AI App ", layout="wide")

# Initialize API configuration
API_KEY = os.getenv('DEEPSEEK_API_KEY')
API_URL = "https://api.deepseek.com/v1/chat/completions" if API_KEY else None

# Initialize session state for stock symbol and auto search
if 'last_mentioned_symbol' not in st.session_state:
    st.session_state.last_mentioned_symbol = ""
if 'auto_search_symbol' not in st.session_state:
    st.session_state.auto_search_symbol = False

def extract_stock_symbols(text):
    """Extract stock symbols from text using regex patterns"""
    if not text:
        return None
        
    # Pattern for stock symbols: Capital letters with optional $ prefix
    patterns = [
        r'\$([A-Z]{1,5})\b',  # Matches symbols with $ prefix
        r'\b([A-Z]{1,5})(?=\s*stock|\s*shares|\s*price|\s*symbol|\s*ticker)',  # Matches symbols followed by stock-related words
        r'\bsymbol[:\s]+([A-Z]{1,5})\b',  # Matches symbols after "symbol:"
        r'\bticker[:\s]+([A-Z]{1,5})\b',   # Matches symbols after "ticker:"
        r'\b([A-Z]{1,5})\b'  # Any standalone capital letters (as last resort)
    ]
    
    symbols = []
    for pattern in patterns:
        matches = re.finditer(pattern, text.upper())
        for match in matches:
            symbol = match.group(1)
            # Verify if it's a valid stock symbol using yfinance
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                if info and 'regularMarketPrice' in info:  # Better validation
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
        if hist.empty or not info:
            return None, None
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
                     xaxis_title='Date',
                     template='plotly_dark')
    return fig

def get_ai_response(prompt):
    """Get AI response for stock analysis"""
    if not API_KEY or not API_URL:
        return "AI analysis is currently unavailable. Please check back later."
        
    try:
        # Enhance the prompt to encourage symbol mentions
        enhanced_prompt = f"Please analyze the following question and include the stock symbol in your response. If a specific company is mentioned, use its stock symbol: {prompt}"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": enhanced_prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(API_URL, headers=headers, json=data)
        if response.status_code == 200:
            ai_response = response.json()["choices"][0]["message"]["content"]
            # Extract symbol from AI response
            symbol = extract_stock_symbols(ai_response)
            if symbol:
                st.session_state.last_mentioned_symbol = symbol
            return ai_response
        else:
            return f"Error getting AI analysis. Status code: {response.status_code}"
    except Exception as e:
        return f"Error during AI analysis: {str(e)}"

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
            st.write("AI Response:", ai_response)
            
            # Extract and display stock details from AI response
            symbol = extract_stock_symbols(ai_response)
            if symbol:
                st.session_state.last_mentioned_symbol = symbol
                st.success(f" Found stock symbol: {symbol}")
                displayed = display_stock_details(symbol)
                if not displayed:
                    st.error(f"Could not load data for {symbol}")

# Display stock details from manual search if provided
if search_query:
    if search_option == "Company Name":
        # Try to extract symbol from company name
        symbol = extract_stock_symbols(search_query)
        if not symbol:
            st.error("Could not find a valid stock symbol for this company name.")
    else:
        symbol = search_query.upper()
    
    if symbol:
        display_stock_details(symbol)
