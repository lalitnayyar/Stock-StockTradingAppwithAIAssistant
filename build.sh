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

# Create streamlit-client.js
echo "Creating streamlit-client.js..."
cat > build_output/static/streamlit-client.js << EOL
// Initialize Streamlit client
window.addEventListener('DOMContentLoaded', function() {
    // Create WebSocket connection
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = wsProtocol + '//' + window.location.host + '/stream';
    
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => console.log('WebSocket connected');
    ws.onerror = (error) => console.error('WebSocket error:', error);
    
    const client = {
        sendMessage: function(message) {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(message));
            }
        },
        onMessage: function(callback) {
            ws.onmessage = (event) => callback(JSON.parse(event.data));
        }
    };
    
    window.streamlitClient = client;
});
EOL

# Create index.html
echo "Creating index.html..."
cat > build_output/index.html << EOL
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Trading App</title>
    <script src="/static/streamlit-client.js" defer></script>
</head>
<body>
    <div id="root"></div>
    <script>
        // Wait for client to initialize before redirecting
        window.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                window.location.href = '/app';
            }, 100);
        });
    </script>
</body>
</html>
EOL

# Copy necessary files
echo "Copying files..."
for file in app.py start.py requirements.txt requirements-dev.txt; do
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
maxUploadSize = 200

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
base = "dark"
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans-serif"

[client]
showErrorDetails = true
toolbarMode = "minimal"
EOL

# Create _headers for Cloudflare Pages
echo "Creating _headers..."
cat > build_output/_headers << EOL
/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  Access-Control-Allow-Headers: *
  Content-Security-Policy: default-src 'self' 'unsafe-inline' 'unsafe-eval' https: wss: ws:; connect-src 'self' https: wss: ws:; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:;
EOL

# List contents of build directory
echo "Build directory contents:"
ls -la build_output/

echo "Build completed successfully!"
