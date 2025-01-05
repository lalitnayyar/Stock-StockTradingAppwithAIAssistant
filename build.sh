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
    <script type="module">
        import streamlit from 'https://cdn.jsdelivr.net/npm/streamlit-component-lib@^1.4.0/dist/streamlit.js';
        window.streamlit = streamlit;
    </script>
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

# Create _headers for Cloudflare Pages
echo "Creating _headers..."
cat > build_output/_headers << EOL
/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  Access-Control-Allow-Headers: Content-Type, Authorization
  Content-Security-Policy: default-src 'self' 'unsafe-inline' 'unsafe-eval' https:; connect-src 'self' https: ws:; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https:;
EOL

# Create worker.js
echo "Creating worker.js..."
cat > build_output/worker.js << EOL
export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      const url = new URL(request.url);
      
      if (url.pathname === '/' || url.pathname === '/index.html') {
        return Response.redirect(\`\${url.origin}/app\`, 301);
      }

      const streamlitUrl = \`http://127.0.0.1:8501\${url.pathname}\${url.search}\`;
      const response = await fetch(streamlitUrl, {
        method: request.method,
        headers: {
          ...Object.fromEntries(request.headers),
          'Host': '127.0.0.1:8501',
          'X-Forwarded-Proto': 'https',
        },
        body: ['GET', 'HEAD'].includes(request.method) ? null : request.body,
      });

      const newHeaders = new Headers(response.headers);
      Object.entries(corsHeaders).forEach(([key, value]) => {
        newHeaders.set(key, value);
      });

      return new Response(response.body, {
        status: response.status,
        headers: newHeaders
      });
    } catch (error) {
      console.error('Worker error:', error);
      return new Response(\`Error: \${error.message}\`, {
        status: 500,
        headers: { 'Content-Type': 'text/plain', ...corsHeaders }
      });
    }
  }
};
EOL

# List contents of build directory
echo "Build directory contents:"
ls -la build_output/

echo "Build completed successfully!"
