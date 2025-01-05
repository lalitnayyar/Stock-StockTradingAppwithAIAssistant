import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
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
        return {}
    
    # Calculate moving averages
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Calculate MACD
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    return data

def prepare_data(data, lookback=60):
    """Prepare data for prediction"""
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))
    
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i, 0])
    
    X = np.array(X)
    y = np.array(y)
    
    return X, y, scaler

def train_model(X, y):
    """Train Random Forest model"""
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def predict_prices(model, data, scaler, lookback=60, days_to_predict=30):
    """Predict future stock prices"""
    last_sequence = data['Close'].values[-lookback:]
    scaled_sequence = scaler.transform(last_sequence.reshape(-1, 1))
    
    predictions = []
    current_sequence = scaled_sequence.reshape(1, -1)
    
    for _ in range(days_to_predict):
        next_pred = model.predict(current_sequence)
        predictions.append(next_pred[0])
        current_sequence = np.roll(current_sequence, -1)
        current_sequence[0, -1] = next_pred
    
    predictions = np.array(predictions).reshape(-1, 1)
    predictions = scaler.inverse_transform(predictions)
    
    return predictions.flatten()

def main():
    """Main application function"""
    st.title('📈 Stock Trading App with AI Assistant')
    
    # Sidebar
    with st.sidebar:
        st.title('Navigation')
        stock_symbol = st.text_input('Enter Stock Symbol:', value=st.session_state['selected_stock'])
        prediction_days = st.slider('Prediction Days:', 5, 60, st.session_state['prediction_days'])
        
        if stock_symbol != st.session_state['selected_stock']:
            st.session_state['selected_stock'] = stock_symbol
        if prediction_days != st.session_state['prediction_days']:
            st.session_state['prediction_days'] = prediction_days
    
    # Load data
    stock, data = load_stock_data()
    
    if len(data) > 0:
        # Calculate indicators
        data = calculate_indicators(data)
        
        # Display stock info
        info = stock.info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"${data['Close'][-1]:.2f}")
        with col2:
            st.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.2f}B")
        with col3:
            st.metric("Volume", f"{info.get('volume', 0):,}")
        
        # Display stock chart
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Stock Price'
        ))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], name='20-day MA'))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], name='50-day MA'))
        fig.update_layout(title='Stock Price Chart', xaxis_title='Date', yaxis_title='Price')
        st.plotly_chart(fig, use_container_width=True)
        
        # AI Predictions
        st.subheader('AI Price Predictions')
        lookback = 60
        
        if len(data) > lookback:
            X, y, scaler = prepare_data(data, lookback)
            model = train_model(X, y)
            predictions = predict_prices(model, data, scaler, lookback, st.session_state['prediction_days'])
            
            future_dates = pd.date_range(
                start=data.index[-1] + timedelta(days=1),
                periods=st.session_state['prediction_days']
            )
            
            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(
                x=data.index[-100:],
                y=data['Close'][-100:],
                name='Historical Price'
            ))
            fig_pred.add_trace(go.Scatter(
                x=future_dates,
                y=predictions,
                name='Predicted Price'
            ))
            fig_pred.update_layout(title='Price Predictions', xaxis_title='Date', yaxis_title='Price')
            st.plotly_chart(fig_pred, use_container_width=True)
            
            # Display prediction metrics
            pred_change = (predictions[-1] - data['Close'][-1]) / data['Close'][-1] * 100
            st.metric(
                "Predicted Price Change",
                f"{pred_change:.2f}%",
                delta=f"${predictions[-1] - data['Close'][-1]:.2f}"
            )

if __name__ == "__main__":
    main()
