from pathlib import Path

path = Path('groq-proxy/church-source-index.test.js')
text = path.read_text(encoding='utf-8')
old = '&& indexedVerifierBody.max_tokens === 400'
new = '&& indexedVerifierBody.max_tokens === 700'
if old not in text:
    raise SystemExit('church-source-index verifier budget assertion anchor missing')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
