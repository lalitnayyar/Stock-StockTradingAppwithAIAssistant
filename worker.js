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
      
      // Handle WebSocket upgrade requests
      if (request.headers.get('Upgrade') === 'websocket') {
        return fetch('http://127.0.0.1:8501' + url.pathname + url.search, {
          headers: request.headers,
          method: request.method,
          body: request.body,
          redirect: 'follow'
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

      // Handle root path
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

      // Forward to Streamlit
      const streamlitUrl = new URL(url.pathname + url.search, 'http://127.0.0.1:8501');
      const response = await fetch(streamlitUrl.toString(), {
        method: request.method,
        headers: {
          ...Object.fromEntries(request.headers),
          'Host': '127.0.0.1:8501',
          'X-Forwarded-Proto': 'https',
          'X-Real-IP': request.headers.get('cf-connecting-ip') || '',
          'X-Forwarded-For': request.headers.get('cf-connecting-ip') || ''
        },
        body: ['GET', 'HEAD'].includes(request.method) ? null : request.body,
        redirect: 'follow'
      });

      // Create new response with CORS headers
      const newHeaders = new Headers(response.headers);
      Object.entries(corsHeaders).forEach(([key, value]) => {
        newHeaders.set(key, value);
      });

      // Special handling for redirects
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
