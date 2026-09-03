import subprocess
from pathlib import Path

subprocess.run(['python', 'tools/temp_exec41_patch_v2.py'], check=True)

path = Path('groq-proxy/church-source-index.test.js')
text = path.read_text(encoding='utf-8')
anchor = '  relevantParagraphText,\n  REQUEST_BUDGET_MS,\n'
replacement = '  relevantParagraphText,\n  retrieveIndexedChurchEvidence,\n  REQUEST_BUDGET_MS,\n'
if anchor not in text:
    raise SystemExit('Missing church-source-index import anchor')
text = text.replace(anchor, replacement, 1)
path.write_text(text, encoding='utf-8')
