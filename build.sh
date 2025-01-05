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

# Create index.html
echo "Creating index.html..."
cat > build_output/index.html << EOL
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Trading App</title>
    <script src="https://cdn.jsdelivr.net/npm/streamlit-component-lib@^1.4.0/dist/streamlit.js"></script>
</head>
<body>
    <div id="root"></div>
    <script>
        window.location.href = '/app';
    </script>
</body>
</html>
EOL

# Copy necessary files
echo "Copying files..."
for file in app.py start.py requirements.txt requirements-dev.txt worker.js; do
    if [ -f "$file" ]; then
        cp "$file" build_output/
    else
        echo "Warning: $file not found"
    fi
done

# Copy static files
if [ -d "static" ]; then
    cp -r static/* build_output/static/
fi

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
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
base = "dark"
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans-serif"
EOL

# Create _routes.json for Cloudflare Pages
echo "Creating _routes.json..."
cat > build_output/_routes.json << EOL
{
  "version": 1,
  "include": ["/*"],
  "exclude": []
}
EOL

# Create _headers for Cloudflare Pages
echo "Creating _headers..."
cat > build_output/_headers << EOL
/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  Access-Control-Allow-Headers: Content-Type, Authorization
EOL

# List contents of build directory
echo "Build directory contents:"
ls -la build_output/

echo "Build completed successfully!"
