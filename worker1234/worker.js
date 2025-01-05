
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Add CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  }

  // Handle OPTIONS request for CORS
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: corsHeaders
    })
  }

  try {
    // Forward request to your Streamlit app
    const url = new URL(request.url)
    const response = await fetch(`http://127.0.0.1:8501${url.pathname}${url.search}`, {
      method: request.method,
      headers: request.headers,
      body: request.body
    })

    // Create new response with CORS headers
    const newResponse = new Response(response.body, response)
    Object.keys(corsHeaders).forEach(key => {
      newResponse.headers.set(key, corsHeaders[key])
    })

    return newResponse
  } catch (error) {
    return new Response(`Error: ${error.message}`, {
      status: 500,
      headers: corsHeaders
    })
  }
}
