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
        """Validate a single symbol"""
        try:
            is_valid, _ = validate_stock_symbol(sym)
            return is_valid
        except:
            return False

    # First try to find symbols with stock-related context
    for pattern in patterns[:-1]:  # Exclude standalone pattern initially
        matches = re.finditer(pattern, text.upper())
        for match in matches:
            symbol = match.group(1).strip()
            if validate_symbol(symbol):
                return symbol
    
    # If no symbol found with context, try standalone symbols
    matches = re.finditer(patterns[-1], text.upper())
    for match in matches:
        symbol = match.group(1).strip()
        # Filter out common English words that might be mistaken for symbols
        if len(symbol) > 1 and validate_symbol(symbol):
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
        return "AI analysis is currently unavailable. Please check back later.", None
    
    try:
        # Extract any symbols from the user's question first
        question_symbol = extract_stock_symbols(prompt)
        
        # Enhance prompt to get better stock-related responses
        enhanced_prompt = (
            "You are a financial analyst assistant. "
            "Please analyze the following question and provide insights. "
            "IMPORTANT: Always include stock symbols in your response using the format $SYMBOL (e.g., $AAPL for Apple). "
            "If you mention any company, you must include its stock symbol. "
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
            
            # Validate the symbol with yfinance
            if symbol:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    if info and info.get('regularMarketPrice'):
                        st.session_state.last_symbol = symbol
                    else:
                        symbol = None
                except:
                    symbol = None
            
            return ai_response, symbol
            
        return f"Error: {response.status_code}", None
    except Exception as e:
        return f"Error: {str(e)}", None

def display_stock_details(symbol):
    """Display detailed stock information with error handling"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get basic info with timeout and error handling
        try:
            info = ticker.info
            if not info or not isinstance(info, dict):
                st.error(f"Could not fetch basic information for {symbol}")
                return False
        except Exception as e:
            st.error(f"Error fetching basic info: {str(e)}")
            return False

        # Get recent price data
        try:
            hist = ticker.history(period="1d")
            if hist.empty:
                st.error(f"No recent price data available for {symbol}")
                return False
            current_price = hist['Close'].iloc[-1]
        except Exception as e:
            st.error(f"Error fetching price data: {str(e)}")
            return False

        # Create tabs for different categories of information
        overview_tab, financials_tab, news_tab = st.tabs(["Overview", "Financials", "News"])

        with overview_tab:
            # Company Overview
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="Current Price",
                    value=f"${current_price:.2f}",
                    delta=f"{((current_price - info.get('previousClose', current_price)) / info.get('previousClose', current_price) * 100):.2f}%"
                )
                st.metric("Market Cap", f"${info.get('marketCap', 0) / 1e9:.2f}B")
                st.metric("Volume", format(info.get('volume', 0), ',d'))

            with col2:
                st.metric("52 Week High", f"${info.get('fiftyTwoWeekHigh', 0):.2f}")
                st.metric("52 Week Low", f"${info.get('fiftyTwoWeekLow', 0):.2f}")
                st.metric("Average Volume", format(info.get('averageVolume', 0), ',d'))

            # Company Description
            if info.get('longBusinessSummary'):
                st.subheader("About the Company")
                st.write(info['longBusinessSummary'])

        with financials_tab:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A')}")
                st.metric("EPS", f"${info.get('trailingEps', 0):.2f}")
                st.metric("Forward P/E", f"{info.get('forwardPE', 'N/A')}")

            with col2:
                st.metric("Dividend Yield", f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "N/A")
                st.metric("Beta", f"{info.get('beta', 'N/A')}")
                st.metric("Profit Margin", f"{info.get('profitMargins', 0) * 100:.2f}%" if info.get('profitMargins') else "N/A")

        with news_tab:
            try:
                # Get news for the company
                news = ticker.news
                if news:
                    for article in news[:5]:  # Display top 5 news articles
                        st.write(f"**{article.get('title', 'No Title')}**")
                        st.write(f"_{article.get('publisher', 'Unknown')} - {datetime.fromtimestamp(article.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M:%S')}_")
                        st.write(article.get('summary', 'No summary available'))
                        st.markdown("---")
                else:
                    st.info("No recent news available")
            except Exception as e:
                st.warning("Could not fetch news data")

        return True

    except Exception as e:
        st.error(f"Error displaying stock details: {str(e)}")
        return False

def validate_stock_symbol(symbol):
    """Validate if a stock symbol exists and is tradeable"""
    try:
        ticker = yf.Ticker(symbol)
        # Try to get recent data to verify the symbol is valid
        hist = ticker.history(period="1d")
        info = ticker.info
        
        # Check if we got any historical data and basic info
        if not hist.empty and info and isinstance(info, dict):
            return True, info
        return False, None
    except Exception as e:
        print(f"Error validating symbol {symbol}: {str(e)}")
        return False, None

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
            
            # Display AI response in a container with styling
            with st.container():
                st.markdown("### 🤖 AI Analysis")
                st.write(ai_response)
            
            # If we found a symbol, display detailed stock information
            if symbol:
                try:
                    st.success(f"📈 Detailed Analysis for ${symbol}")
                    if display_stock_details(symbol):
                        st.info("Data provided by Yahoo Finance. All prices are in USD unless otherwise noted.")
                    else:
                        st.warning(f"Could not fetch detailed data for ${symbol}")
                except Exception as e:
                    st.error(f"Error displaying stock details: {str(e)}")
            
            # Add to chat history
            st.session_state.chat_history.append({
                "question": user_question,
                "response": ai_response,
                "symbol": symbol
            })

# Manual Stock Search
with st.sidebar:
    st.title("Manual Stock Search")
    with st.form("stock_search_form"):
        search_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):", key="manual_stock_search")
        submit_button = st.form_submit_button("📊 Get Stock Report", use_container_width=True)
        
        if submit_button and search_symbol:
            symbol = search_symbol.upper().strip()
            try:
                # Show loading spinner while fetching data
                with st.spinner(f'Fetching data for ${symbol}...'):
                    # Verify the symbol exists
                    is_valid, info = validate_stock_symbol(symbol)
                    
                    if is_valid:
                        st.success(f"Found ${symbol} - {info.get('longName', '')}")
                        if display_stock_details(symbol):
                            st.session_state.last_symbol = symbol
                            st.info("Data provided by Yahoo Finance. All prices are in USD unless otherwise noted.")
                        else:
                            st.warning(f"Could not fetch complete data for {symbol}. Please try again.")
                    else:
                        st.error(f"Could not find data for symbol: {symbol}. Please check and try again.")
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
    
    # Show recent searches
    if hasattr(st.session_state, 'last_symbol') and st.session_state.last_symbol:
        st.markdown("---")
        st.markdown("### Recent Searches")
        if st.button(f"📈 ${st.session_state.last_symbol}", key="recent_search"):
            symbol = st.session_state.last_symbol
            display_stock_details(symbol)

# Display chat history
if st.session_state.chat_history:
    st.markdown("---")
    st.header("Previous Queries")
    for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5 conversations
        with st.expander(f"Query {len(st.session_state.chat_history)-i}: {chat['question'][:50]}..."):
            st.write("**Question:**", chat['question'])
            st.write("**AI Response:**", chat['response'])
            if chat['symbol']:
                if st.button(f"📊 Show ${chat['symbol']} Details", key=f"history_{i}"):
                    display_stock_details(chat['symbol'])
