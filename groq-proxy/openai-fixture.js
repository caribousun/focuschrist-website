// Offline transport adapter: exercise the real OpenAI HTTP path while source
// tests provide a deterministic verifier verdict. Never used by the Worker.
export function withVerifierFixture(worker) {
  return { async fetch(request, env = {}) {
    const { verifierFixture, ...bindings } = env;
    if (!verifierFixture) return worker.fetch(request, bindings);
    const sourceFetch = globalThis.fetch;
    globalThis.fetch = async (url, options = {}) => {
      if (String(url) === 'https://api.openai.com/v1/chat/completions') {
        const body = JSON.parse(options.body);
        const verdict = await verifierFixture(body.model, body);
        return new Response(JSON.stringify({ choices: [{ message: { content: JSON.stringify(verdict.response ?? verdict) } }] }), { headers: { 'Content-Type': 'application/json' } });
      }
      return sourceFetch(url, options);
    };
    try { return await worker.fetch(request, { ...bindings, OPENAI_API_KEY: 'offline-fixture' }); }
    finally { globalThis.fetch = sourceFetch; }
  }};
}
