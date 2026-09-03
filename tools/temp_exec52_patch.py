from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected exactly one match, found {count}: {old[:80]!r}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


def replace_all_required(path, old, new):
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count < 1:
        raise SystemExit(f'{path}: expected at least one match for {old!r}')
    path.write_text(text.replace(old, new), encoding='utf-8')


worker = ROOT / 'groq-proxy/src/index.js'
replace_once(worker,
    "const SOURCE_POLICY_VERSION = '2026-09-03.51';",
    "const SOURCE_POLICY_VERSION = '2026-09-03.52';")
replace_once(worker,
    "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.51';",
    "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.52';")
replace_once(worker,
    "return /\\bpray\\w*\\b/i.test(content) && /\\bforgiv\\w*\\b/i.test(content);",
    "return /\\bpray\\w*\\b/i.test(content) && /\\b(?:forgiv\\w*|sins?\\b|guilt\\b)/i.test(content);")

policy_test = ROOT / 'groq-proxy/source-policy.test.js'
replace_all_required(policy_test, '2026-09-03.51', '2026-09-03.52')
anchor = "assert(reviewedDeterministicEvidenceRecovery(\n  'What does Enos 1 teach about prayer and forgiveness?',\n  [{ url: 'https://example.com/enos/1', content: 'prayer forgiven' }],\n) === null, 'reviewed Enos recovery must never accept a non-Church source');"
insert = anchor + "\nconst enosSinWordRecovery = reviewedDeterministicEvidenceRecovery(\n  'What does Enos 1 teach about prayer and forgiveness?',\n  [{\n    url: 'https://www.churchofjesuschrist.org/study/scriptures/bofm/enos/1?lang=eng',\n    content: 'Enos cried unto God in mighty prayer for his own soul. The Lord spoke to him about his sins, and Enos said his guilt was swept away.',\n  }],\n);\nassert(enosSinWordRecovery\n  && enosSinWordRecovery.recoveryId === 'reviewed-enos-1-prayer-forgiveness',\n  'exact Enos 1 evidence using sins or guilt language must activate the audited recovery without requiring the literal word forgiven');\nassert(reviewedDeterministicEvidenceRecovery(\n  'What does Enos 1 teach about prayer and forgiveness?',\n  [{\n    url: 'https://www.churchofjesuschrist.org/study/scriptures/bofm/enos/1?lang=eng',\n    content: 'Enos prayed earnestly to God throughout the day.',\n  }],\n) === null, 'the Enos recovery must still require sin, guilt, or forgiveness evidence in addition to prayer');"
replace_once(policy_test, anchor, insert)

for rel in [
    'tools/live_ai_response_matrix.js',
    'tools/pioneer_local_first_qa.py',
    'tools/scripture_grounding_qa.py',
]:
    replace_all_required(ROOT / rel, '2026-09-03.51', '2026-09-03.52')

memory = ROOT / 'MEMORY.md'
text = memory.read_text(encoding='utf-8')
note = "\n- 2026-09-03 candidate `.52`: the final cold Enos 1 production failure was traced to an overly literal reviewed-recovery gate. The Worker already had the exact official Enos 1 source and prayer evidence, but required the excerpt to contain the literal `forgiv...` stem. `.52` keeps the exact ChurchofJesusChrist.org Enos 1 URL requirement and now accepts the chapter's equivalent sin/forgiveness evidence (`forgiv...`, `sin/sins`, or `guilt`) alongside prayer. This removes HTML/excerpt wording brittleness without broadening the recovery to unrelated sources or questions. Production remains unverified until the complete deployed live matrix passes.\n"
if note.strip() not in text:
    memory.write_text(text.rstrip() + '\n' + note, encoding='utf-8')

print('candidate .52 patch applied')
