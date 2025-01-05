#!/bin/bash

# Install dependencies
pip install -r requirements.txt --upgrade

# Set environment variables for Streamlit
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start Streamlit
streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.baseUrlPath="/app" --browser.serverAddress="0.0.0.0" --browser.serverPort=8501
