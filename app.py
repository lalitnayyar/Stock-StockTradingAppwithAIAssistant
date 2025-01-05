import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
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

# Initialize session state for cookie management
if 'cookie_manager' not in st.session_state:
    st.session_state['cookie_manager'] = {
        'session_id': datetime.now().strftime("%Y%m%d%H%M%S"),
        'preferences': {}
    }

# Initialize session state
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = 'AAPL'
if 'period' not in st.session_state:
    st.session_state.period = '1y'
if 'interval' not in st.session_state:
    st.session_state.interval = '1d'

# Sidebar
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Stock Analysis", "AI Predictions", "Trading Signals"],
        icons=["graph-up", "robot", "lightning"],
        menu_icon="cast",
        default_index=0,
    )

    st.sidebar.title('Stock Settings')
    stock_symbol = st.sidebar.text_input('Enter Stock Symbol', value=st.session_state.selected_stock)
    period = st.sidebar.selectbox('Select Period', 
                                options=['1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'],
                                index=3)
    interval = st.sidebar.selectbox('Select Interval',
                                  options=['1d', '5d', '1wk', '1mo'],
                                  index=0)

    if stock_symbol:
        st.session_state.selected_stock = stock_symbol.upper()
        st.session_state.period = period
        st.session_state.interval = interval

def load_stock_data():
    """Load stock data using yfinance"""
    try:
        stock = yf.Ticker(st.session_state.selected_stock)
        data = stock.history(period=st.session_state.period, interval=st.session_state.interval)
        if data.empty:
            st.error(f"No data found for {st.session_state.selected_stock}")
            return None, None
        return stock, data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def calculate_technical_indicators(data):
    """Calculate technical indicators"""
    if data is None or data.empty:
        return None
    
    df = data.copy()
    
    # RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # MACD
    macd = ta.macd(df['Close'])
    df = pd.concat([df, macd], axis=1)
    
    # Bollinger Bands
    bb = ta.bbands(df['Close'])
    df = pd.concat([df, bb], axis=1)
    
    # Moving Averages
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    
    return df

def create_stock_chart(data, indicators):
    """Create an interactive stock chart with technical indicators"""
    if data is None or data.empty:
        return None
    
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='OHLC'
    ))
    
    # Add technical indicators
    if indicators:
        if 'SMA_20' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['SMA_20'],
                name='SMA 20',
                line=dict(color='orange')
            ))
        
        if 'EMA_20' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['EMA_20'],
                name='EMA 20',
                line=dict(color='blue')
            ))
        
        if 'BBL_20_2.0' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['BBL_20_2.0'],
                name='BB Lower',
                line=dict(color='gray', dash='dash')
            ))
            
        if 'BBM_20_2.0' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['BBM_20_2.0'],
                name='BB Middle',
                line=dict(color='gray')
            ))
            
        if 'BBU_20_2.0' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['BBU_20_2.0'],
                name='BB Upper',
                line=dict(color='gray', dash='dash')
            ))
    
    fig.update_layout(
        title=f'{st.session_state.selected_stock} Stock Price',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_dark',
        height=800
    )
    
    return fig

def prepare_data_for_prediction(data, lookback=60):
    """Prepare data for LSTM prediction"""
    df = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(df)
    
    X, y = [], []
    for i in range(lookback, len(df_scaled)):
        X.append(df_scaled[i-lookback:i])
        y.append(df_scaled[i])
    
    X = np.array(X)
    y = np.array(y)
    
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    return X_train, X_test, y_train, y_test, scaler

def create_lstm_model(lookback):
    """Create and compile LSTM model"""
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    return model

def predict_stock_prices(data, days_to_predict=30):
    """Predict future stock prices using LSTM"""
    lookback = 60
    X_train, X_test, y_train, y_test, scaler = prepare_data_for_prediction(data, lookback)
    
    model = create_lstm_model(lookback)
    model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)
    
    # Prepare data for future prediction
    last_sequence = data['Close'].values[-lookback:]
    last_sequence = scaler.transform(last_sequence.reshape(-1, 1))
    
    future_predictions = []
    current_sequence = last_sequence
    
    for _ in range(days_to_predict):
        # Predict next value
        next_pred = model.predict(current_sequence.reshape(1, lookback, 1), verbose=0)
        future_predictions.append(next_pred[0])
        
        # Update sequence
        current_sequence = np.roll(current_sequence, -1)
        current_sequence[-1] = next_pred
    
    # Inverse transform predictions
    future_predictions = scaler.inverse_transform(np.array(future_predictions))
    
    # Create future dates
    last_date = data.index[-1]
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_to_predict, freq='B')
    
    return pd.Series(future_predictions.flatten(), index=future_dates)

def main():
    """Main application function"""
    if selected == "Stock Analysis":
        st.title(' Stock Analysis Dashboard')
        
        # Load data
        stock, data = load_stock_data()
        
        if stock and data is not None:
            # Display company info
            info = stock.info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Price", f"${data['Close'][-1]:.2f}", 
                         f"{((data['Close'][-1] - data['Close'][-2])/data['Close'][-2]*100):.2f}%")
            
            with col2:
                st.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.2f}B")
            
            with col3:
                st.metric("Volume", f"{data['Volume'][-1]:,.0f}")
            
            # Calculate and display technical indicators
            indicators = calculate_technical_indicators(data)
            
            # Create and display chart
            fig = create_stock_chart(data, indicators)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Display technical indicators
            if indicators is not None:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("RSI")
                    st.line_chart(indicators['RSI'])
                
                with col2:
                    st.subheader("MACD")
                    st.line_chart(indicators[['MACD_12_26_9', 'MACDs_12_26_9']])
    
    elif selected == "AI Predictions":
        st.title(' AI Stock Price Predictions')
        
        stock, data = load_stock_data()
        
        if stock and data is not None:
            st.info("Training AI model... This may take a few moments.")
            
            # Make predictions
            predictions = predict_stock_prices(data)
            
            # Create prediction chart
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'],
                name='Historical',
                line=dict(color='blue')
            ))
            
            # Predictions
            fig.add_trace(go.Scatter(
                x=predictions.index,
                y=predictions.values,
                name='Predicted',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title=f'{st.session_state.selected_stock} Stock Price Prediction',
                yaxis_title='Price',
                xaxis_title='Date',
                template='plotly_dark',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display prediction metrics
            st.subheader("Prediction Metrics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Predicted Price (30 days)", 
                         f"${predictions.iloc[-1]:.2f}",
                         f"{((predictions.iloc[-1] - data['Close'][-1])/data['Close'][-1]*100):.2f}%")
            
            with col2:
                st.metric("Current Price", 
                         f"${data['Close'][-1]:.2f}")
    
    elif selected == "Trading Signals":
        st.title(' Trading Signals')
        
        stock, data = load_stock_data()
        
        if stock and data is not None:
            # Calculate indicators for signals
            indicators = calculate_technical_indicators(data)
            
            if indicators is not None:
                # Generate trading signals
                signals = pd.DataFrame(index=data.index)
                
                # RSI Signals
                signals['RSI_Signal'] = 'Hold'
                signals.loc[indicators['RSI'] < 30, 'RSI_Signal'] = 'Buy'
                signals.loc[indicators['RSI'] > 70, 'RSI_Signal'] = 'Sell'
                
                # MACD Signals
                signals['MACD_Signal'] = 'Hold'
                signals.loc[indicators['MACD_12_26_9'] > indicators['MACDs_12_26_9'], 'MACD_Signal'] = 'Buy'
                signals.loc[indicators['MACD_12_26_9'] < indicators['MACDs_12_26_9'], 'MACD_Signal'] = 'Sell'
                
                # Bollinger Bands Signals
                signals['BB_Signal'] = 'Hold'
                signals.loc[data['Close'] < indicators['BBL_20_2.0'], 'BB_Signal'] = 'Buy'
                signals.loc[data['Close'] > indicators['BBU_20_2.0'], 'BB_Signal'] = 'Sell'
                
                # Display current signals
                st.subheader("Current Trading Signals")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("RSI Signal", signals['RSI_Signal'][-1])
                with col2:
                    st.metric("MACD Signal", signals['MACD_Signal'][-1])
                with col3:
                    st.metric("BB Signal", signals['BB_Signal'][-1])
                
                # Display signals history
                st.subheader("Recent Trading Signals")
                st.dataframe(signals.tail(10))
                
                # Plot signals on price chart
                fig = go.Figure()
                
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='OHLC'
                ))
                
                # Add buy signals
                buy_signals = signals[signals['RSI_Signal'] == 'Buy'].index
                fig.add_trace(go.Scatter(
                    x=buy_signals,
                    y=data.loc[buy_signals, 'Low'] * 0.99,
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=15, color='green'),
                    name='Buy Signal'
                ))
                
                # Add sell signals
                sell_signals = signals[signals['RSI_Signal'] == 'Sell'].index
                fig.add_trace(go.Scatter(
                    x=sell_signals,
                    y=data.loc[sell_signals, 'High'] * 1.01,
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=15, color='red'),
                    name='Sell Signal'
                ))
                
                fig.update_layout(
                    title=f'{st.session_state.selected_stock} Trading Signals',
                    yaxis_title='Price',
                    xaxis_title='Date',
                    template='plotly_dark',
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
