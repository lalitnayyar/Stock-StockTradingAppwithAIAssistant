#!/bin/bash

# Exit on error
set -e

# Print commands
set -x

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create build directory
echo "Creating build directory..."
rm -rf build_output || true
mkdir -p build_output
mkdir -p build_output/static

# Copy necessary files
echo "Copying files..."
for file in app.py start.py requirements.txt requirements-dev.txt worker.js; do
    if [ -f "$file" ]; then
        cp "$file" build_output/
    else
        echo "Warning: $file not found"
    fi
done

# Copy .env if it exists
if [ -f ".env" ]; then
    cp .env build_output/
fi

# Create Streamlit config
echo "Creating Streamlit config..."
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

# List contents of build directory
echo "Build directory contents:"
ls -la build_output/

echo "Build completed successfully!"
