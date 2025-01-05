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

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_symbol' not in st.session_state:
    st.session_state.last_symbol = None

def extract_stock_symbols(text):
    """Extract stock symbols from text using regex patterns"""
    if not text:
        return None
    
    # Common stock symbols and their patterns
    patterns = [
        r'\$([A-Z]{1,5})\b',                     # $AAPL
        r'ticker:?\s*([A-Z]{1,5})\b',            # ticker: AAPL or ticker AAPL
        r'symbol:?\s*([A-Z]{1,5})\b',            # symbol: AAPL or symbol AAPL
        r'\b([A-Z]{1,5})\s*(?:stock|shares)\b',  # AAPL stock or AAPL shares
        r'\b([A-Z]{1,5})\b'                      # AAPL (standalone)
    ]
    
    def validate_symbol(sym):
        try:
            ticker = yf.Ticker(sym)
            info = ticker.info
            return bool(info and info.get('regularMarketPrice'))
        except:
            return False

    # First try to find symbols with stock-related context
    for pattern in patterns[:-1]:  # Exclude standalone pattern initially
        matches = re.finditer(pattern, text.upper())
        for match in matches:
            symbol = match.group(1)
            if validate_symbol(symbol):
                return symbol
    
    # If no symbols found with context, try standalone capitals
    matches = re.finditer(patterns[-1], text.upper())
    symbols = [match.group(1) for match in matches]
    for symbol in symbols:
        if validate_symbol(symbol):
            return symbol
    
    return None

def get_stock_data(symbol, period='1y'):
    """Fetch stock data using yfinance"""
    if not symbol:
        return None, None
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or 'regularMarketPrice' not in info:
            return None, None
            
        hist = ticker.history(period=period)
        if hist.empty:
            return None, None
            
        return hist, info
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None, None

def create_candlestick_chart(df, symbol):
    """Create a candlestick chart using plotly"""
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close'])])
    
    fig.update_layout(
        title=f'{symbol} Stock Price',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template='plotly_dark',
        height=600,
        showlegend=False
    )
    
    return fig

def get_ai_response(prompt):
    """Get AI response for stock analysis"""
    if not API_KEY or not API_URL:
        return "AI analysis is currently unavailable. Please check back later."
    
    try:
        # Extract any symbols from the user's question first
        question_symbol = extract_stock_symbols(prompt)
        
        # Enhance prompt to get better stock-related responses
        enhanced_prompt = (
            "You are a financial analyst assistant. "
            "When mentioning companies, always include their stock symbol in uppercase with a $ prefix. "
            f"Question: {prompt}\n"
            f"{'Note: The user mentioned ' + question_symbol + '.' if question_symbol else ''}"
        )
        
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
            
            # Try to extract symbol from AI response
            symbol = extract_stock_symbols(ai_response)
            
            # If no symbol in AI response but found in question, use that
            if not symbol and question_symbol:
                symbol = question_symbol
            
            if symbol:
                st.session_state.last_symbol = symbol
            
            return ai_response, symbol
            
        return f"Error: {response.status_code}", None
    except Exception as e:
        return f"Error: {str(e)}", None

def display_stock_details(symbol):
    """Display stock details including chart and information"""
    if not symbol:
        return False
        
    hist_data, stock_info = get_stock_data(symbol)
    if hist_data is None or stock_info is None:
        st.error(f"Could not fetch data for {symbol}")
        return False
        
    # Display basic metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        current_price = stock_info.get('regularMarketPrice', 'N/A')
        if current_price != 'N/A':
            current_price = f"${current_price:,.2f}"
        st.metric("Current Price", current_price)
    
    with col2:
        market_cap = stock_info.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            market_cap = f"${market_cap:,.0f}"
        st.metric("Market Cap", market_cap)
    
    with col3:
        volume = stock_info.get('volume', 'N/A')
        if volume != 'N/A':
            volume = f"{volume:,}"
        st.metric("Volume", volume)
    
    # Display chart
    st.plotly_chart(create_candlestick_chart(hist_data, symbol), use_container_width=True)
    
    # Additional information
    with st.expander("More Information"):
        st.write(f"**Company:** {stock_info.get('longName', 'N/A')}")
        st.write(f"**Sector:** {stock_info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {stock_info.get('industry', 'N/A')}")
        st.write(f"**52 Week High:** ${stock_info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}")
        st.write(f"**52 Week Low:** ${stock_info.get('fiftyTwoWeekLow', 'N/A'):,.2f}")
        st.write(f"**Beta:** {stock_info.get('beta', 'N/A')}")
        st.write(f"**P/E Ratio:** {stock_info.get('trailingPE', 'N/A')}")
        
    return True

# Main content
st.title("Stock Trading Application")

# AI Chat Section
st.header("AI Financial Assistant")
user_question = st.text_input("Ask about any stock or company (e.g., 'Tell me about Apple stock' or 'What's happening with $TSLA'):")

if user_question:
    if not API_KEY:
        st.warning("Please set up your API key in the .env file")
    else:
        with st.spinner('Analyzing your question...'):
            # Get AI response and extracted symbol
            ai_response, symbol = get_ai_response(user_question)
            
            # Display AI response
            st.write("**AI Response:**", ai_response)
            
            # If we found a symbol, display stock details
            if symbol:
                st.success(f"📈 Showing data for ${symbol}")
                display_stock_details(symbol)
            
            # Add to chat history
            st.session_state.chat_history.append({
                "question": user_question,
                "response": ai_response,
                "symbol": symbol
            })

# Manual Stock Search
with st.sidebar:
    st.title("Manual Stock Search")
    search_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):")
    if search_symbol:
        symbol = search_symbol.upper()
        if display_stock_details(symbol):
            st.session_state.last_symbol = symbol
