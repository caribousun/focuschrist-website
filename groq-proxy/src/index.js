// Cloudflare Worker - Groq API Proxy
// Deploy this at workers.cloudflare.com

export default {
  async fetch(request, env) {
    // Only allow POST requests
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    // Your Groq API key - stored in worker secrets, never exposed
    const GROQ_API_KEY = env.GROQ_KEY_NEW; // Using new secret
    
    if (!GROQ_API_KEY) {
      return new Response('API key not configured', { status: 500 });
    }

    // Forward the request to Groq
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GROQ_API_KEY}`,
      },
      body: await request.text(),
    });

    // Return the response
    return new Response(response.body, {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  },
};
