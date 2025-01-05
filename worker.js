export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': '*',
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
    };

    // Redirect HTTP to HTTPS
    const url = new URL(request.url);
    if (url.protocol === 'http:') {
      url.protocol = 'https:';
      return Response.redirect(url.toString(), 301);
    }

    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: corsHeaders
      });
    }

    try {
      // Handle WebSocket upgrade requests for /stream endpoint
      if (request.headers.get('Upgrade')?.toLowerCase() === 'websocket') {
        // Forward WebSocket connection to Streamlit backend
        const streamlitUrl = 'wss://127.0.0.1:8501/stream';
        const upgradeHeader = request.headers.get('Upgrade');
        const connectionHeader = request.headers.get('Connection');
        const secWebSocketKey = request.headers.get('Sec-WebSocket-Key');
        const secWebSocketProtocol = request.headers.get('Sec-WebSocket-Protocol');
        const secWebSocketVersion = request.headers.get('Sec-WebSocket-Version');
        
        const headers = new Headers({
          'Upgrade': upgradeHeader,
          'Connection': connectionHeader,
          'Sec-WebSocket-Key': secWebSocketKey,
          'Sec-WebSocket-Protocol': secWebSocketProtocol,
          'Sec-WebSocket-Version': secWebSocketVersion,
          'Host': '127.0.0.1:8501',
          'Origin': 'https://127.0.0.1:8501'
        });

        return fetch(streamlitUrl, {
          method: 'GET',
          headers: headers,
          body: request.body
        });
      }

      // Serve static files
      if (url.pathname.startsWith('/static/')) {
        const response = await env.ASSETS.fetch(request);
        if (response.ok) {
          const newHeaders = new Headers(response.headers);
          Object.entries(corsHeaders).forEach(([key, value]) => {
            newHeaders.set(key, value);
          });
          return new Response(response.body, {
            status: response.status,
            headers: newHeaders
          });
        }
      }

      // Handle root path and direct to index.html
      if (url.pathname === '/' || url.pathname === '/index.html') {
        const response = await env.ASSETS.fetch(new Request(new URL('/index.html', request.url)));
        const newHeaders = new Headers(response.headers);
        Object.entries(corsHeaders).forEach(([key, value]) => {
          newHeaders.set(key, value);
        });
        return new Response(response.body, {
          status: response.status,
          headers: newHeaders
        });
      }

      // Forward all other requests to Streamlit
      const streamlitUrl = new URL(url.pathname + url.search, 'https://127.0.0.1:8501');
      const response = await fetch(streamlitUrl.toString(), {
        method: request.method,
        headers: {
          ...Object.fromEntries(request.headers),
          'Host': '127.0.0.1:8501',
          'X-Forwarded-Proto': 'https',
          'X-Real-IP': request.headers.get('cf-connecting-ip') || '',
          'X-Forwarded-For': request.headers.get('cf-connecting-ip') || ''
        },
        body: ['GET', 'HEAD'].includes(request.method) ? null : request.body
      });

      // Create new response with CORS and security headers
      const newHeaders = new Headers(response.headers);
      Object.entries(corsHeaders).forEach(([key, value]) => {
        newHeaders.set(key, value);
      });
      
      // Add additional security headers
      newHeaders.set('Content-Security-Policy', "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: wss:; img-src 'self' data: https:; worker-src 'self' blob:");
      newHeaders.set('X-Content-Type-Options', 'nosniff');
      newHeaders.set('X-Frame-Options', 'SAMEORIGIN');
      newHeaders.set('X-XSS-Protection', '1; mode=block');
      newHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin');

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
