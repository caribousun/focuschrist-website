from pathlib import Path

path = Path('groq-proxy/church-source-index.test.js')
text = path.read_text(encoding='utf-8')
if 'max_tokens === 400' not in text:
    raise SystemExit('church-source-index verifier budget assertion anchors missing')
path.write_text(text.replace('max_tokens === 400', 'max_tokens === 700'), encoding='utf-8')
