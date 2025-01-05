#!/bin/bash

# Exit on error
set -e

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create build directory
echo "Creating build directory..."
mkdir -p build_output
mkdir -p build_output/static

# Copy necessary files
echo "Copying files..."
cp app.py build_output/
cp start.py build_output/
cp requirements.txt build_output/
cp requirements-dev.txt build_output/
cp worker.js build_output/
cp .env build_output/ || true  # Don't fail if .env doesn't exist

# Create Streamlit config
mkdir -p build_output/.streamlit
cat > build_output/.streamlit/config.toml << EOL
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = true

[browser]
gatherUsageStats = false
EOL

echo "Build completed successfully!"
