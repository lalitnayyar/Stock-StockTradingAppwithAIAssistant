export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: corsHeaders
      });
    }

    try {
      const url = new URL(request.url);
      
      // Serve index.html for root path
      if (url.pathname === '/' || url.pathname === '/index.html') {
        return new Response(`
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
        `, {
          headers: {
            'Content-Type': 'text/html',
            ...corsHeaders
          }
        });
      }

      // Forward request to Streamlit
      const streamlitUrl = `http://127.0.0.1:8501${url.pathname}${url.search}`;
      const response = await fetch(streamlitUrl, {
        method: request.method,
        headers: {
          ...request.headers,
          'Host': '127.0.0.1:8501',
          'X-Forwarded-Proto': 'https'
        },
        body: request.body
      });

      // Create new response with CORS headers
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
      return new Response(`Error: ${error.message}`, {
        status: 500,
        headers: {
          'Content-Type': 'text/plain',
          ...corsHeaders
        }
      });
    }
  }
};
