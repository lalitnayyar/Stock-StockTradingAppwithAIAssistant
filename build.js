const fs = require('fs');
const path = require('path');

// Create build directory
if (fs.existsSync('build_output')) {
    fs.rmSync('build_output', { recursive: true });
}
fs.mkdirSync('build_output');
fs.mkdirSync(path.join('build_output', 'static'));

// Create streamlit-client.js
const clientJs = `
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
`;

fs.writeFileSync(path.join('build_output', 'static', 'streamlit-client.js'), clientJs);

// Create index.html
const indexHtml = `
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
`;

fs.writeFileSync(path.join('build_output', 'index.html'), indexHtml);

// Create _headers
const headers = `/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  Access-Control-Allow-Headers: *
  Content-Security-Policy: default-src 'self' 'unsafe-inline' 'unsafe-eval' https: wss: ws:; connect-src 'self' https: wss: ws:; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:;
`;

fs.writeFileSync(path.join('build_output', '_headers'), headers);

// Copy necessary files
const filesToCopy = ['app.py', 'start.py', 'requirements.txt', 'requirements-dev.txt'];
filesToCopy.forEach(file => {
    if (fs.existsSync(file)) {
        fs.copyFileSync(file, path.join('build_output', file));
    }
});

// Copy static directory if it exists
if (fs.existsSync('static')) {
    fs.cpSync('static', path.join('build_output', 'static'), { recursive: true });
}

// Create .streamlit directory and config
fs.mkdirSync(path.join('build_output', '.streamlit'));
const streamlitConfig = `[server]
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
`;

fs.writeFileSync(path.join('build_output', '.streamlit', 'config.toml'), streamlitConfig);

console.log('Build completed successfully!');
