@echo off
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo Creating build directory...
if exist build_output rmdir /s /q build_output
mkdir build_output
mkdir build_output\static

echo Creating streamlit-client.js...
(
echo // Initialize Streamlit client
echo window.addEventListener('DOMContentLoaded', function() {
echo     // Create WebSocket connection
echo     const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
echo     const wsUrl = wsProtocol + '//' + window.location.host + '/stream';
echo     
echo     const ws = new WebSocket(wsUrl^);
echo     ws.onopen = () =^> console.log('WebSocket connected'^);
echo     ws.onerror = (error^) =^> console.error('WebSocket error:', error^);
echo     
echo     const client = {
echo         sendMessage: function(message^) {
echo             if (ws.readyState === WebSocket.OPEN^) {
echo                 ws.send(JSON.stringify(message^)^);
echo             }
echo         },
echo         onMessage: function(callback^) {
echo             ws.onmessage = (event^) =^> callback(JSON.parse(event.data^)^);
echo         }
echo     };
echo     
echo     window.streamlitClient = client;
echo }^);
) > build_output\static\streamlit-client.js

echo Creating index.html...
(
echo ^<!DOCTYPE html^>
echo ^<html lang="en"^>
echo ^<head^>
echo     ^<meta charset="UTF-8"^>
echo     ^<meta name="viewport" content="width=device-width, initial-scale=1.0"^>
echo     ^<title^>Stock Trading App^</title^>
echo     ^<script src="/static/streamlit-client.js" defer^>^</script^>
echo ^</head^>
echo ^<body^>
echo     ^<div id="root"^>^</div^>
echo     ^<script^>
echo         // Wait for client to initialize before redirecting
echo         window.addEventListener('DOMContentLoaded', function() {
echo             setTimeout(() =^> {
echo                 window.location.href = '/app';
echo             }, 100^);
echo         }^);
echo     ^</script^>
echo ^</body^>
echo ^</html^>
) > build_output\index.html

echo Copying necessary files...
for %%f in (app.py start.py requirements.txt requirements-dev.txt) do (
    if exist %%f copy %%f build_output\
)

if exist static xcopy /E /I static build_output\static
if exist .env copy .env build_output\

echo Creating Streamlit config...
mkdir build_output\.streamlit
(
echo [server]
echo port = 8501
echo address = "0.0.0.0"
echo headless = true
echo enableCORS = true
echo enableXsrfProtection = false
echo maxUploadSize = 200
echo.
echo [browser]
echo gatherUsageStats = false
echo serverAddress = "localhost"
echo serverPort = 8501
echo.
echo [theme]
echo base = "dark"
echo primaryColor = "#FF4B4B"
echo backgroundColor = "#0E1117"
echo secondaryBackgroundColor = "#262730"
echo textColor = "#FAFAFA"
echo font = "sans-serif"
echo.
echo [client]
echo showErrorDetails = true
echo toolbarMode = "minimal"
) > build_output\.streamlit\config.toml

echo Creating _headers...
(
echo /*
echo   Access-Control-Allow-Origin: *
echo   Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
echo   Access-Control-Allow-Headers: *
echo   Content-Security-Policy: default-src 'self' 'unsafe-inline' 'unsafe-eval' https: wss: ws:; connect-src 'self' https: wss: ws:; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:;
) > build_output\_headers

echo Build directory contents:
dir /s /b build_output

echo Build completed successfully!
