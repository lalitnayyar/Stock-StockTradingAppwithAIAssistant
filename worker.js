export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': '*',
    };

    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: corsHeaders
      });
    }

    try {
      const url = new URL(request.url);
      
      // Handle WebSocket upgrade requests for /stream endpoint
      if (request.headers.get('Upgrade') === 'websocket' && url.pathname === '/stream') {
        const streamlitUrl = new URL('ws://127.0.0.1:8501/stream');
        
        // Forward the WebSocket request to Streamlit
        return fetch(streamlitUrl.toString(), {
          method: request.method,
          headers: {
            ...Object.fromEntries(request.headers),
            'Host': '127.0.0.1:8501',
            'Origin': 'http://127.0.0.1:8501',
            'Upgrade': 'websocket',
            'Connection': 'Upgrade'
          },
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
      const streamlitUrl = new URL(url.pathname + url.search, 'http://127.0.0.1:8501');
      const response = await fetch(streamlitUrl.toString(), {
        method: request.method,
        headers: {
          ...Object.fromEntries(request.headers),
          'Host': '127.0.0.1:8501',
          'X-Forwarded-Proto': request.headers.get('x-forwarded-proto') || 'https',
          'X-Real-IP': request.headers.get('cf-connecting-ip') || '',
          'X-Forwarded-For': request.headers.get('cf-connecting-ip') || ''
        },
        body: ['GET', 'HEAD'].includes(request.method) ? null : request.body
      });

      // Create new response with CORS headers
      const newHeaders = new Headers(response.headers);
      Object.entries(corsHeaders).forEach(([key, value]) => {
        newHeaders.set(key, value);
      });

      // Handle redirects
      if (response.status === 301 || response.status === 302) {
        const location = response.headers.get('Location');
        if (location) {
          const redirectUrl = new URL(location, url.origin);
          newHeaders.set('Location', redirectUrl.toString());
        }
      }

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
