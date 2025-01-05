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
    initial_sidebar_state="expanded"
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
                    5. Key Trading Indicators"""
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
            return f"API Error: {response.status_code}"
            
    except Exception as e:
        return f"Analysis Error: {str(e)}"

def load_stock_data():
    """Load stock data from yfinance"""
    try:
        stock = yf.Ticker(st.session_state['selected_stock'])
        data = stock.history(period="2y")
        return stock, data
    except Exception as e:
        st.error(f"Error loading stock data: {e}")
        return None, pd.DataFrame()

def calculate_indicators(data):
    """Calculate technical indicators"""
    if len(data) == 0:
        return data
    
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    return data

def prepare_data(data, lookback=60):
    """Prepare data for model training"""
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data[['Close']])
    
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i])
        y.append(scaled_data[i])
    
    return np.array(X), np.array(y), scaler

def train_model(X, y):
    """Train Random Forest model"""
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X.reshape(X.shape[0], -1), y.reshape(-1))
    return model

def predict_prices(model, data, scaler, lookback=60, days_to_predict=30):
    """Predict future stock prices"""
    last_sequence = data['Close'].values[-lookback:]
    scaled_last_sequence = scaler.transform(last_sequence.reshape(-1, 1))
    
    predictions = []
    current_sequence = scaled_last_sequence.copy()
    
    for _ in range(days_to_predict):
        next_pred = model.predict(current_sequence.reshape(1, -1))
        predictions.append(next_pred[0])
        current_sequence = np.roll(current_sequence, -1)
        current_sequence[-1] = next_pred
    
    predicted_prices = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
    return predicted_prices.flatten()

def display_stock_info(df, stock_symbol):
    """Display stock information and charts"""
    if len(df) > 0:
        df = calculate_indicators(df)
        
        # Create two columns with different ratios
        empty_col, main_col = st.columns([1, 4])
        
        # Main column (right) - All content
        with main_col:
            # AI Analysis Results
            if st.session_state.ai_analysis:
                st.subheader("🤖 AI Market Analysis")
                st.markdown(st.session_state.ai_analysis)
                st.download_button(
                    label="Download Analysis",
                    data=st.session_state.ai_analysis,
                    file_name=f"{stock_symbol}_analysis.txt",
                    mime="text/plain"
                )
                st.caption("Disclaimer: This AI analysis is for informational purposes only.")
            
            # Metrics row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}", 
                         f"{((df['Close'].iloc[-1] - df['Close'].iloc[-2])/df['Close'].iloc[-2]*100):.2f}%")
            with col2:
                st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
            with col3:
                st.metric("RSI", f"{df['RSI'].iloc[-1]:.2f}")
            
            # Price Prediction
            X, y, scaler = prepare_data(df[['Close']])
            if len(X) > 0:
                model = train_model(X, y)
                predictions = predict_prices(model, df, scaler, days_to_predict=st.session_state['prediction_days'])
                
                last_date = df.index[-1]
                future_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                           periods=st.session_state['prediction_days'], freq='B')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Historical'))
                fig.add_trace(go.Scatter(x=future_dates, y=predictions, name='Predicted',
                                       line=dict(dash='dash')))
                
                fig.update_layout(title='Stock Price Prediction',
                                xaxis_title='Date',
                                yaxis_title='Price',
                                hovermode='x unified',
                                height=400)
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Technical Indicators
            st.subheader("Technical Indicators")
            tech_col1, tech_col2 = st.columns(2)
            
            with tech_col1:
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD'))
                fig_macd.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], name='Signal Line'))
                fig_macd.update_layout(title='MACD', height=400)
                st.plotly_chart(fig_macd, use_container_width=True)
            
            with tech_col2:
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI'))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.update_layout(title='RSI', height=400)
                st.plotly_chart(fig_rsi, use_container_width=True)

def main():
    st.title("Stock Trading App with AI Assistant 📈")
    
    st.sidebar.header("Settings")
    
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
                        
                        # AI Analysis Button in sidebar
                        if st.button('Get AI Market Analysis'):
                            with st.spinner('Generating AI Analysis...'):
                                stock, df = load_stock_data()
                                if stock and len(df) > 0:
                                    st.session_state.ai_analysis = get_deepseek_analysis(selected_suggestion, df)
                        
                        # Load and display stock data immediately
                        stock, df = load_stock_data()
                        if stock and len(df) > 0:
                            display_stock_info(df, selected_suggestion)
    else:
        selected_stock = st.sidebar.text_input("Or enter stock symbol directly", 
                                             value=st.session_state['selected_stock'])
        if selected_stock != st.session_state['selected_stock']:
            st.session_state['selected_stock'] = selected_stock
            
            # AI Analysis Button in sidebar
            if st.button('Get AI Market Analysis'):
                with st.spinner('Generating AI Analysis...'):
                    stock, df = load_stock_data()
                    if stock and len(df) > 0:
                        st.session_state.ai_analysis = get_deepseek_analysis(selected_stock, df)
            
            # Load and display stock data immediately
            stock, df = load_stock_data()
            if stock and len(df) > 0:
                display_stock_info(df, selected_stock)

    prediction_days = st.sidebar.slider("Prediction Days", 7, 60, st.session_state['prediction_days'])
    if prediction_days != st.session_state['prediction_days']:
        st.session_state['prediction_days'] = prediction_days
        # Refresh display with new prediction days
        stock, df = load_stock_data()
        if stock and len(df) > 0:
            display_stock_info(df, st.session_state['selected_stock'])

if __name__ == "__main__":
    main()