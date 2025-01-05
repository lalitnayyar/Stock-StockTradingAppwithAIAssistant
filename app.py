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

def get_ai_response(question):
    """Get AI response and extract stock symbols"""
    try:
        # Get AI response
        response = get_deepseek_response(question)
        if not response:
            return "I apologize, but I couldn't generate a response at the moment. Please try again.", None
        
        # Extract potential stock symbols
        symbol = extract_stock_symbols(response)
        
        # If no symbol found in response, try question
        if not symbol:
            symbol = extract_stock_symbols(question)
        
        return response, symbol
        
    except Exception as e:
        return f"Error: {str(e)}", None

def extract_stock_symbols(text):
    """Extract stock symbols from text using regex patterns"""
    if not text:
        return None
    
    # Common stock symbols and their patterns, ordered by priority
    patterns = [
        r'\$([A-Z]{1,5})\b',                     # $AAPL
        r'ticker[:\s]+([A-Z]{1,5})\b',           # ticker: AAPL
        r'symbol[:\s]+([A-Z]{1,5})\b',           # symbol: AAPL
        r'\b([A-Z]{1,5})\s+(?:stock|shares)\b',  # AAPL stock
        r'\b([A-Z]{1,5})\s+(?:Inc\.?|Corp\.?|Corporation|Company|Ltd\.?)\b',  # AAPL Inc
        r'\b([A-Z]{1,5})\b'                      # AAPL (standalone)
    ]
    
    # Words that should not be treated as stock symbols
    common_words = {
        'A', 'AN', 'AND', 'ARE', 'AS', 'AT', 'BE', 'BY', 'FOR', 'FROM', 'HAS', 'HE',
        'IN', 'IS', 'IT', 'ITS', 'OF', 'ON', 'OR', 'THAT', 'THE', 'TO', 'WAS',
        'WERE', 'WILL', 'WITH', 'THE', 'ABOUT', 'ABOVE', 'AFTER', 'AGAIN', 'ALL',
        'MOST', 'OTHER', 'SOME', 'SUCH', 'NO', 'NOR', 'NOT', 'ONLY', 'OWN', 'SAME',
        'SO', 'THAN', 'TOO', 'VERY', 'CAN', 'WILL', 'JUST', 'SHOULD', 'NOW'
    }
    
    def is_valid_symbol(sym):
        """Check if a symbol is valid"""
        if not sym or len(sym) < 2 or len(sym) > 5:
            return False
        if sym in common_words:
            return False
        try:
            ticker = yf.Ticker(sym)
            info = ticker.info
            if not info or not isinstance(info, dict):
                return False
            # Check if we have basic price information
            if info.get('regularMarketPrice') or info.get('currentPrice'):
                return True
            return False
        except:
            return False
    
    # Try each pattern in order of priority
    text = text.upper()
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            symbol = match.group(1).strip()
            if is_valid_symbol(symbol):
                return symbol
    
    return None

def get_deepseek_response(prompt):
    """Get AI response from DeepSeek API"""
    if not API_KEY or not API_URL:
        return None
    
    try:
        # Enhance prompt to get better stock-related responses
        enhanced_prompt = (
            "You are a financial analyst assistant. "
            "Please analyze the following question and provide insights. "
            "IMPORTANT: Always include stock symbols in your response using the format $SYMBOL (e.g., $AAPL for Apple). "
            "If you mention any company, you must include its stock symbol. "
            f"Question: {prompt}"
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
            return response.json()["choices"][0]["message"]["content"]
        
        print(f"API Error: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"Error calling DeepSeek API: {str(e)}")
        return None

def validate_stock_symbol(symbol):
    """Validate if a stock symbol exists and is tradeable"""
    try:
        # Check if the input looks like a company name
        suggestion = get_symbol_suggestions(symbol)
        if suggestion:
            return False, None, f"Did you mean ${suggestion}? Please use the stock symbol instead of the company name."
        
        # Check if it's a common word
        if symbol.upper() in {
            'A', 'AN', 'AND', 'ARE', 'AS', 'AT', 'BE', 'BY', 'FOR', 'FROM', 'HAS', 'HE',
            'IN', 'IS', 'IT', 'ITS', 'OF', 'ON', 'OR', 'THAT', 'THE', 'TO', 'WAS',
            'WERE', 'WILL', 'WITH', 'THE', 'ABOUT', 'ABOVE', 'AFTER', 'AGAIN', 'ALL',
            'MOST', 'OTHER', 'SOME', 'SUCH', 'NO', 'NOR', 'NOT', 'ONLY', 'OWN', 'SAME',
            'SO', 'THAN', 'TOO', 'VERY', 'CAN', 'WILL', 'JUST', 'SHOULD', 'NOW'
        }:
            return False, None, f"'{symbol}' appears to be a common word, not a stock symbol. Please enter a valid stock symbol (e.g., AAPL, MSFT, GOOGL)."
        
        ticker = yf.Ticker(symbol)
        
        # Try to get info first
        info = ticker.info
        if not info or not isinstance(info, dict):
            return False, None, f"Could not find information for symbol ${symbol}. Please verify the symbol is correct."
        
        # If we have basic price information, consider it valid
        if info.get('regularMarketPrice') or info.get('currentPrice'):
            return True, info, None
        
        # Additional validation with historical data if needed
        try:
            hist = ticker.history(period="1mo")
            if not hist.empty:
                return True, info, None
        except:
            # If history check fails but we have price info, still consider it valid
            if info.get('regularMarketPrice') or info.get('currentPrice'):
                return True, info, None
        
        return False, None, f"Could not verify price data for ${symbol}. Please check if this is a valid, actively traded stock symbol."
        
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            return False, None, f"Symbol ${symbol} not found. Please verify the symbol is correct."
        return False, None, f"Error validating symbol: {error_msg}"

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

def create_stock_chart(df, symbol):
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

def get_symbol_suggestions(company_name):
    """Get symbol suggestions for a company name"""
    common_symbols = {
        'TESLA': 'TSLA',
        'APPLE': 'AAPL',
        'MICROSOFT': 'MSFT',
        'AMAZON': 'AMZN',
        'GOOGLE': 'GOOGL',
        'META': 'META',
        'FACEBOOK': 'META',
        'NETFLIX': 'NFLX',
        'NVIDIA': 'NVDA',
        'ALPHABET': 'GOOGL',
    }
    
    # Check for direct matches
    company_name = company_name.upper()
    if company_name in common_symbols:
        return common_symbols[company_name]
    
    # Check for partial matches
    for name, symbol in common_symbols.items():
        if name in company_name or company_name in name:
            return symbol
    
    return None

def display_stock_details(symbol):
    """Display comprehensive stock details including chart and information"""
    try:
        # Validate symbol first
        is_valid, info, error_msg = validate_stock_symbol(symbol)
        if not is_valid:
            st.error(error_msg)
            return False
            
        # Create tabs for different types of information
        tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Key Stats", "📰 Company Info"])
        
        with tab1:
            try:
                # Get historical data
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1y')
                if not hist.empty:
                    fig = create_stock_chart(hist, symbol)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No historical data available for chart visualization.")
            except Exception as e:
                st.error(f"Error creating chart: {str(e)}")
        
        with tab2:
            try:
                if info:
                    col1, col2 = st.columns(2)
                    
                    # Financial Metrics
                    with col1:
                        st.subheader("Financial Metrics")
                        metrics = {
                            "Market Cap": info.get("marketCap", "N/A"),
                            "P/E Ratio": info.get("trailingPE", "N/A"),
                            "EPS": info.get("trailingEps", "N/A"),
                            "52W High": info.get("fiftyTwoWeekHigh", "N/A"),
                            "52W Low": info.get("fiftyTwoWeekLow", "N/A"),
                            "Volume": info.get("volume", "N/A")
                        }
                        
                        for key, value in metrics.items():
                            if isinstance(value, (int, float)):
                                if key == "Market Cap":
                                    value = f"${value:,.0f}"
                                elif value > 1000000:
                                    value = f"{value:,.2f}"
                                else:
                                    value = f"{value:.2f}"
                            st.metric(key, value)
                    
                    # Trading Info
                    with col2:
                        st.subheader("Trading Information")
                        trading_info = {
                            "Current Price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
                            "Open": info.get("regularMarketOpen", "N/A"),
                            "Previous Close": info.get("regularMarketPreviousClose", "N/A"),
                            "Day High": info.get("regularMarketDayHigh", "N/A"),
                            "Day Low": info.get("regularMarketDayLow", "N/A"),
                            "Volume": info.get("regularMarketVolume", "N/A")
                        }
                        
                        for key, value in trading_info.items():
                            if isinstance(value, (int, float)):
                                if key == "Volume":
                                    value = f"{value:,.0f}"
                                else:
                                    value = f"${value:.2f}"
                            st.metric(key, value)
                else:
                    st.warning("Detailed financial data not available.")
            except Exception as e:
                st.error(f"Error displaying financial metrics: {str(e)}")
        
        with tab3:
            try:
                if info:
                    # Company Information
                    st.subheader("Company Information")
                    company_info = {
                        "Name": info.get("longName", "N/A"),
                        "Industry": info.get("industry", "N/A"),
                        "Sector": info.get("sector", "N/A"),
                        "Website": info.get("website", "N/A"),
                        "Description": info.get("longBusinessSummary", "N/A")
                    }
                    
                    for key, value in company_info.items():
                        if key == "Description":
                            st.markdown(f"**{key}:**")
                            st.write(value)
                        else:
                            st.markdown(f"**{key}:** {value}")
                else:
                    st.warning("Company information not available.")
            except Exception as e:
                st.error(f"Error displaying company information: {str(e)}")
        
        return True
        
    except Exception as e:
        st.error(f"Error displaying stock details: {str(e)}")
        return False

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
                    is_valid, info, error_msg = validate_stock_symbol(symbol)
                    
                    if is_valid:
                        st.success(f"Found ${symbol} - {info.get('longName', '')}")
                        if display_stock_details(symbol):
                            st.session_state.last_symbol = symbol
                            st.info("Data provided by Yahoo Finance. All prices are in USD unless otherwise noted.")
                        else:
                            st.warning(f"Could not fetch complete data for {symbol}. Please try again.")
                    else:
                        st.error(error_msg)
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
