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
    """Display comprehensive stock details including chart and information"""
    if not symbol:
        return False
        
    hist_data, stock_info = get_stock_data(symbol)
    if hist_data is None or stock_info is None:
        st.error(f"Could not fetch data for {symbol}")
        return False
    
    # Company Header with Current Price
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"{stock_info.get('longName', symbol)} ({symbol})")
    with col2:
        current_price = stock_info.get('regularMarketPrice', 'N/A')
        prev_close = stock_info.get('previousClose', 'N/A')
        if current_price != 'N/A' and prev_close != 'N/A':
            price_change = current_price - prev_close
            price_change_pct = (price_change / prev_close) * 100
            price_color = "green" if price_change >= 0 else "red"
            st.markdown(f"""
                <div style='text-align: right'>
                    <h2 style='margin: 0; color: {price_color}'>${current_price:.2f}</h2>
                    <p style='margin: 0; color: {price_color}'>
                        {price_change:+.2f} ({price_change_pct:+.2f}%)
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    # Key Statistics Grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Previous Close", f"${prev_close:.2f}" if prev_close != 'N/A' else 'N/A')
        st.metric("Open", f"${stock_info.get('open', 'N/A'):.2f}")
    
    with col2:
        st.metric("Day's Range", f"${stock_info.get('dayLow', 'N/A'):.2f} - ${stock_info.get('dayHigh', 'N/A'):.2f}")
        st.metric("52 Week Range", f"${stock_info.get('fiftyTwoWeekLow', 'N/A'):.2f} - ${stock_info.get('fiftyTwoWeekHigh', 'N/A'):.2f}")
    
    with col3:
        market_cap = stock_info.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.2f}B"
            else:
                market_cap_str = f"${market_cap/1e6:.2f}M"
        else:
            market_cap_str = 'N/A'
        st.metric("Market Cap", market_cap_str)
        st.metric("Beta", f"{stock_info.get('beta', 'N/A'):.2f}")
    
    with col4:
        st.metric("Volume", f"{stock_info.get('volume', 'N/A'):,}")
        st.metric("Avg. Volume", f"{stock_info.get('averageVolume', 'N/A'):,}")
    
    # Display chart
    st.plotly_chart(create_candlestick_chart(hist_data, symbol), use_container_width=True)
    
    # Company Information and Additional Metrics
    tab1, tab2, tab3 = st.tabs(["📊 Financial Metrics", "🏢 Company Info", "📈 Additional Stats"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Valuation Metrics")
            st.write(f"- P/E Ratio (TTM): {stock_info.get('trailingPE', 'N/A')}")
            st.write(f"- Forward P/E: {stock_info.get('forwardPE', 'N/A')}")
            st.write(f"- EPS (TTM): ${stock_info.get('trailingEps', 'N/A')}")
            st.write(f"- Forward EPS: ${stock_info.get('forwardEps', 'N/A')}")
        with col2:
            st.markdown("### Dividend Information")
            st.write(f"- Dividend Rate: ${stock_info.get('dividendRate', 'N/A')}")
            st.write(f"- Dividend Yield: {stock_info.get('dividendYield', 'N/A')}%")
            st.write(f"- Ex-Dividend Date: {stock_info.get('exDividendDate', 'N/A')}")
            st.write(f"- Payout Ratio: {stock_info.get('payoutRatio', 'N/A')}")
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Company Profile")
            st.write(f"- Sector: {stock_info.get('sector', 'N/A')}")
            st.write(f"- Industry: {stock_info.get('industry', 'N/A')}")
            st.write(f"- Employees: {stock_info.get('fullTimeEmployees', 'N/A'):,}")
            st.write(f"- Country: {stock_info.get('country', 'N/A')}")
        with col2:
            st.markdown("### Additional Information")
            st.write(f"- Website: {stock_info.get('website', 'N/A')}")
            st.write(f"- CEO: {stock_info.get('companyOfficers', [{}])[0].get('name', 'N/A')}")
            st.write(f"- Founded: {stock_info.get('foundedYear', 'N/A')}")
            st.write(f"- Exchange: {stock_info.get('exchange', 'N/A')}")
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Trading Statistics")
            st.write(f"- 50-Day Moving Average: ${stock_info.get('fiftyDayAverage', 'N/A'):.2f}")
            st.write(f"- 200-Day Moving Average: ${stock_info.get('twoHundredDayAverage', 'N/A'):.2f}")
            st.write(f"- Short Ratio: {stock_info.get('shortRatio', 'N/A')}")
            st.write(f"- Short % of Float: {stock_info.get('shortPercentOfFloat', 'N/A')}%")
        with col2:
            st.markdown("### Price Targets")
            st.write(f"- Analyst Target Price: ${stock_info.get('targetMeanPrice', 'N/A'):.2f}")
            st.write(f"- Target High: ${stock_info.get('targetHighPrice', 'N/A'):.2f}")
            st.write(f"- Target Low: ${stock_info.get('targetLowPrice', 'N/A'):.2f}")
            st.write(f"- Number of Analysts: {stock_info.get('numberOfAnalystOpinions', 'N/A')}")
    
    # Company Description
    with st.expander("📝 Company Description"):
        st.write(stock_info.get('longBusinessSummary', 'No description available.'))
    
    return True

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
