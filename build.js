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
(function() {
    async function initStreamlit() {
        return new Promise((resolve, reject) => {
            const maxAttempts = 10;
            let attempts = 0;
            let backoffDelay = 1000; // Start with 1 second delay

            function tryConnect() {
                try {
                    // Use the worker URL for WebSocket connection
                    const workerDomain = 'stock-stocktradingappwithaiassistant.lalitnayyar.workers.dev';
                    const wsUrl = 'wss://' + workerDomain + '/stream';
                    
                    console.log('Connecting to WebSocket:', wsUrl);
                    const ws = new WebSocket(wsUrl);
                    
                    ws.onopen = () => {
                        console.log('WebSocket connected successfully');
                        const client = {
                            sendMessage: function(message) {
                                if (ws.readyState === WebSocket.OPEN) {
                                    ws.send(JSON.stringify(message));
                                }
                            },
                            onMessage: function(callback) {
                                ws.onmessage = (event) => callback(JSON.parse(event.data));
                            },
                            close: function() {
                                ws.close();
                            }
                        };
                        window.streamlitClient = client;
                        resolve(client);
                    };
                    
                    ws.onerror = (error) => {
                        console.error('WebSocket error:', error);
                        ws.close();
                    };

                    ws.onclose = (event) => {
                        console.log('WebSocket connection closed:', event.code, event.reason);
                        if (!window.streamlitClient) {
                            attempts++;
                            if (attempts < maxAttempts) {
                                console.log(\`Retrying connection (attempt \${attempts}/\${maxAttempts}) after \${backoffDelay}ms...\`);
                                setTimeout(tryConnect, backoffDelay);
                                backoffDelay = Math.min(backoffDelay * 1.5, 5000);
                            } else {
                                reject(new Error('Failed to connect to WebSocket after multiple attempts'));
                                document.getElementById('loading').innerHTML = '<div class="error-message">Failed to connect to the server. Please check if the server is running and refresh the page.</div>';
                            }
                        }
                    };
                } catch (error) {
                    console.error('Error initializing WebSocket:', error);
                    if (attempts < maxAttempts) {
                        setTimeout(tryConnect, backoffDelay);
                        backoffDelay = Math.min(backoffDelay * 1.5, 5000);
                    } else {
                        reject(error);
                    }
                }
            }

            // Start connection attempt
            tryConnect();
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initStreamlit);
    } else {
        initStreamlit().catch(error => {
            console.error('Failed to initialize Streamlit:', error);
            document.getElementById('loading').innerHTML = '<div class="error-message">Failed to initialize the application. Please refresh the page.</div>';
        });
    }
})();`;

fs.writeFileSync(path.join('build_output', 'static', 'streamlit-client.js'), clientJs);

// Create index.html
const indexHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' https: wss:; img-src 'self' data: https:; worker-src 'self' blob:; connect-src 'self' wss: https:;">
    <title>Stock Trading App</title>
    <script src="/static/streamlit-client.js" defer></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #0E1117;
            color: #FAFAFA;
        }
        #loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #0E1117;
            z-index: 1000;
        }
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #FF4B4B;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        .error-message {
            color: #FF4B4B;
            text-align: center;
            padding: 20px;
            max-width: 80%;
            font-size: 16px;
            line-height: 1.5;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div id="loading">
        <div class="spinner"></div>
    </div>
    <div id="root"></div>
    <script>
        window.addEventListener('DOMContentLoaded', function() {
            // Ensure HTTPS
            if (window.location.protocol === 'http:') {
                window.location.href = window.location.href.replace('http:', 'https:');
            }
        });
    </script>
</body>
</html>`;

fs.writeFileSync(path.join('build_output', 'index.html'), indexHtml);

// Create _headers
const headers = `/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  Access-Control-Allow-Headers: *
  Content-Security-Policy: default-src 'self' 'unsafe-inline' 'unsafe-eval' https: wss: ws:; connect-src 'self' https: wss: ws:; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:;
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: same-origin
  X-XSS-Protection: 1; mode=block
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
fs.mkdirSync(path.join('build_output', '.streamlit'), { recursive: true });
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
