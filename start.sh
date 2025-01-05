#!/bin/bash
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
