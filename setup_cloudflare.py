import os
import shutil
from pathlib import Path

# Create static directory
static_dir = Path(__file__).parent / 'static'
static_dir.mkdir(exist_ok=True)

# Create worker directory
worker_dir = Path(__file__).parent / 'worker'
worker_dir.mkdir(exist_ok=True)

# Create worker script
worker_script = """
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
"""

with open(worker_dir / 'worker.js', 'w') as f:
    f.write(worker_script)

print("Created static and worker directories")
print("Created worker.js script")
print("\nNext steps:")
print("1. Install Wrangler CLI: npm install -g wrangler")
print("2. Login to Cloudflare: wrangler login")
print("3. Update wrangler.toml with your zone_id and route")
print("4. Deploy: wrangler deploy")
