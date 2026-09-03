from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected exactly one match, found {count}: {old[:100]!r}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


def replace_all_required(path, old, new):
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count < 1:
        raise SystemExit(f'{path}: expected at least one match for {old!r}')
    path.write_text(text.replace(old, new), encoding='utf-8')

worker = ROOT / 'groq-proxy/src/index.js'
replace_once(worker, "const SOURCE_POLICY_VERSION = '2026-09-03.52';", "const SOURCE_POLICY_VERSION = '2026-09-03.53';")
replace_once(worker, "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.52';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.53';")
replace_once(worker,
    "return /\\bpray\\w*\\b/i.test(content) && /\\b(?:forgiv\\w*|sins?\\b|guilt\\b)/i.test(content);",
    "return content.trim().length >= 80;")

policy = ROOT / 'groq-proxy/source-policy.test.js'
replace_all_required(policy, '2026-09-03.52', '2026-09-03.53')
old_block = "assert(reviewedDeterministicEvidenceRecovery(\n  'What does Enos 1 teach about prayer and forgiveness?',\n  [{\n    url: 'https://www.churchofjesuschrist.org/study/scriptures/bofm/enos/1?lang=eng',\n    content: 'Enos prayed earnestly to God throughout the day.',\n  }],\n) === null, 'the Enos recovery must still require sin, guilt, or forgiveness evidence in addition to prayer');"
new_block = "const enosExactSourceRecovery = reviewedDeterministicEvidenceRecovery(\n  'What does Enos 1 teach about prayer and forgiveness?',\n  [{\n    url: 'https://www.churchofjesuschrist.org/study/scriptures/bofm/enos/1?lang=eng',\n    content: 'This is a substantive excerpt returned from the exact official Enos 1 chapter after deterministic indexed retrieval and evidence admission. It is long enough to prove that the official chapter was actually fetched rather than inferred from a URL alone.',\n  }],\n);\nassert(enosExactSourceRecovery\n  && enosExactSourceRecovery.recoveryId === 'reviewed-enos-1-prayer-forgiveness',\n  'the audited Enos answer must not depend on which exact words survive deterministic excerpt truncation once the exact official Enos 1 source has been substantively fetched');\nassert(reviewedDeterministicEvidenceRecovery(\n  'What does Enos 1 teach about prayer and forgiveness?',\n  [{\n    url: 'https://www.churchofjesuschrist.org/study/scriptures/bofm/enos/1?lang=eng',\n    content: 'too short',\n  }],\n) === null, 'the Enos recovery must not activate from a bare URL with no substantive retrieved evidence');"
replace_once(policy, old_block, new_block)

for rel in ['tools/live_ai_response_matrix.js', 'tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    replace_all_required(ROOT / rel, '2026-09-03.52', '2026-09-03.53')

memory = ROOT / 'MEMORY.md'
text = memory.read_text(encoding='utf-8')
note = "\n- 2026-09-03 candidate `.53`: the `.52` production matrix proved that even semantic keyword checks inside a truncated Enos excerpt could false-negative on the first cold fetch while the same exact official chapter succeeded from cache. `.53` removes excerpt-wording dependence for this audited recovery: an explicit Enos 1 prayer/forgiveness question may use the pre-reviewed Enos answer only after deterministic retrieval has returned substantive evidence from the exact `churchofjesuschrist.org/study/scriptures/bofm/enos/1` URL. A bare URL or short/non-substantive source cannot activate it. This makes the reviewed answer source-gated rather than cache-wording-gated. Production remains unverified until the complete deployed live matrix passes.\n"
if note.strip() not in text:
    memory.write_text(text.rstrip() + '\n' + note, encoding='utf-8')

print('candidate .53 patch applied')
