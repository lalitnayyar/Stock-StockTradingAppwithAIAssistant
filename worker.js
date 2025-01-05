addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  }

  // Handle CORS preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: corsHeaders
    })
  }

  try {
    const url = new URL(request.url)
    
    // Serve static files from /static directory
    if (url.pathname.startsWith('/static/')) {
      const response = await fetch(request)
      if (response.ok) {
        const newHeaders = new Headers(response.headers)
        Object.entries(corsHeaders).forEach(([key, value]) => {
          newHeaders.set(key, value)
        })
        return new Response(response.body, {
          status: response.status,
          headers: newHeaders
        })
      }
    }

    // Redirect root to /app
    if (url.pathname === '/' || url.pathname === '/index.html') {
      return Response.redirect(`${url.origin}/app`, 301)
    }

    // Forward to Streamlit
    const streamlitUrl = `http://127.0.0.1:8501${url.pathname}${url.search}`
    const response = await fetch(streamlitUrl, {
      method: request.method,
      headers: {
        ...Object.fromEntries(request.headers),
        'Host': '127.0.0.1:8501',
        'X-Forwarded-Proto': 'https',
        'X-Forwarded-For': request.headers.get('cf-connecting-ip') || '',
      },
      body: ['GET', 'HEAD'].includes(request.method) ? null : request.body,
    })

    // Create new response with CORS headers
    const newHeaders = new Headers(response.headers)
    Object.entries(corsHeaders).forEach(([key, value]) => {
      newHeaders.set(key, value)
    })

    return new Response(response.body, {
      status: response.status,
      headers: newHeaders
    })
  } catch (error) {
    console.error('Worker error:', error)
    return new Response(`Error: ${error.message}`, {
      status: 500,
      headers: {
        'Content-Type': 'text/plain',
        ...corsHeaders
      }
    })
  }
}
