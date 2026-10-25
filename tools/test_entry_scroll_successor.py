"""Negative controls for the Ask entry scroll-follow successor layer.

Synthetic fixture round trips plus the real-candidate round trip, the
full historical chain round trip through the continue-motion binding
(for ask.html: the legacy-repairs after state, the citation-rendering
after state, the answer-bank after state, the motion map's after
state, then the motion map's before pin; for ask-experience.js: the
motion map's after state, then its before pin), and the required
mutations: an altered token
inside a registered span, an altered older-layer token, and an
unrelated append are all rejected, and a tampered span manifest or
pin is rejected. The layer records no finished in-tree review;
Jeff's independent exact-head review of the PR carrying this
registration is delivered on the channel and gates merge.
"""
import base64
import copy
import difflib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import entry_scroll_successor as c

REAL_BEFORE = dict(c.BEFORE)
REAL_AFTER = dict(c.AFTER)
REAL_SOURCE_SHA = c.SOURCE_SHA

OLD_ASK = (b"<script>\n"
           b"    function addMessage(text, isUser, sources = []) {\n"
           b"        chatBox.appendChild(message);\n"
           b"        chatBox.scrollTop = chatBox.scrollHeight;\n"
           b"    }\n"
           b"</script>\n")
NEW_ASK = (b"<script>\n"
           b"    function bringEntryIntoView(entry) {\n"
           b"        if (!entry || typeof entry.scrollIntoView !== 'function') return;\n"
           b"        entry.scrollIntoView({ behavior: 'auto', block: 'start' });\n"
           b"    }\n"
           b"\n"
           b"    function addMessage(text, isUser, sources = []) {\n"
           b"        chatBox.appendChild(message);\n"
           b"        bringEntryIntoView(message);\n"
           b"    }\n"
           b"</script>\n")
OLD_EXP = (b"    function focusLatestAnswer(answer) {\n"
           b"        const userMessages = chatBox.querySelectorAll('.user-message');\n"
           b"        const exchangeStart = userMessages.length ? userMessages[0] : answer;\n"
           b"    }\n")
NEW_EXP = (b"    function focusLatestAnswer(answer) {\n"
           b"        const exchangeStart = answer.previousElementSibling && answer.previousElementSibling.classList\n"
           b"            && answer.previousElementSibling.classList.contains('user-message')\n"
           b"            ? answer.previousElementSibling\n"
           b"            : answer;\n"
           b"    }\n")
FIXTURE_PAIRS = {"ask.html": (OLD_ASK, NEW_ASK), "ask-experience.js": (OLD_EXP, NEW_EXP)}
FIXTURE_BEFORE = {name: c.sha(pair[0]) for name, pair in FIXTURE_PAIRS.items()}
FIXTURE_AFTER = {name: c.sha(pair[1]) for name, pair in FIXTURE_PAIRS.items()}


def fixture_spans(before, after):
    bl, al = before.splitlines(keepends=True), after.splitlines(keepends=True)
    aoff = [0]
    for line in al:
        aoff.append(aoff[-1] + len(line))
    spans = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=bl, b=al, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        spans.append({"start": aoff[j1], "end": aoff[j2],
                      "previous_b64": base64.b64encode(b"".join(bl[i1:i2])).decode(),
                      "current_b64": base64.b64encode(b"".join(al[j1:j2])).decode()})
    return spans


def fixture_manifest():
    files = {}
    for name, (old, new) in FIXTURE_PAIRS.items():
        files[name] = {"before_sha256": FIXTURE_BEFORE[name],
                       "after_sha256": FIXTURE_AFTER[name],
                       "spans": fixture_spans(old, new)}
    return {"schema": 1, "layer": "entry_scroll_successor", "files": files}


class EntryScrollSuccessorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = fixture_manifest()
        self.write(c.MANIFEST, json.dumps(self.manifest).encode())
        for name, (old, new) in FIXTURE_PAIRS.items():
            self.write(name, new)
        self.patch = patch.multiple(c, BEFORE=FIXTURE_BEFORE, AFTER=FIXTURE_AFTER,
                                    SOURCE_SHA=c.canonical(self.manifest))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def write(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def real_root(self, label, mutated_name=None, mutated_raw=None):
        root = Path(self.temp.name) / label
        root.mkdir()
        (root / "docs/entry-scroll-successor").mkdir(parents=True)
        (root / c.MANIFEST).write_bytes((c.ROOT / c.MANIFEST).read_bytes())
        for name in FIXTURE_PAIRS:
            raw = (c.ROOT / name).read_bytes()
            if name == mutated_name:
                raw = mutated_raw
            (root / name).write_bytes(raw)
        return root

    def test_exact_round_trip_and_gate(self):
        for name, (old, new) in FIXTURE_PAIRS.items():
            self.assertEqual(c.restore(name, new, self.root), old, name)
            self.assertEqual(c.advance(name, old, self.root), new, name)
        self.assertEqual(c.check(self.root)["status"], "ENTRY_SCROLL_SUCCESSOR_EVIDENCE_PASS")

    def test_real_candidate_exact_round_trip(self):
        manifest = json.loads((c.ROOT / c.MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(c.canonical(manifest), REAL_SOURCE_SHA)
        for name, row in manifest["files"].items():
            current = (c.ROOT / name).read_bytes()
            self.assertEqual(c.sha(current), row["after_sha256"], name)
            with patch.multiple(c, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                restored = c.restore(name, current, c.ROOT)
                self.assertEqual(c.sha(restored), row["before_sha256"], name)
                self.assertEqual(c.advance(name, restored, c.ROOT), current, name)

    def test_historical_chain_round_trip(self):
        import continue_motion_binding as gate
        from legacy_answer_repairs_successor import restore as restore_legacy
        from citation_rendering_successor import restore as restore_citation
        from answer_bank_successor import restore as restore_bank
        with patch.multiple(c, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
            name = "ask.html"
            row = gate.mapping()["files"][name]
            current = (gate.ROOT / name).read_bytes()
            projected = c.restore(name, current, gate.ROOT)
            self.assertEqual(c.sha(projected), REAL_BEFORE[name])
            projected = restore_legacy(name, projected, gate.ROOT)
            self.assertEqual(c.sha(projected), "4881b5a20ed045b1d45dd1c393d3204c56cf46692d7fa4837e5257346aa4e7a9")
            projected = restore_citation(name, projected, gate.ROOT)
            self.assertEqual(c.sha(projected), "735ccd0d56d7931a651ec8c06759cc849e7895fa55311f8d9d7d6bb36b419612")
            self.assertEqual(gate.sha(restore_bank(name, projected, gate.ROOT)), row["after_sha256"])
            self.assertEqual(gate.sha(gate.restore(name, current)), row["before_sha256"])
            self.assertEqual(gate.advance(name, gate.restore(name, current)), current)
            name = "ask-experience.js"
            row = gate.mapping()["files"][name]
            current = (gate.ROOT / name).read_bytes()
            self.assertEqual(gate.sha(c.restore(name, current, gate.ROOT)), row["after_sha256"])
            self.assertEqual(gate.sha(gate.restore(name, current)), row["before_sha256"])
            self.assertEqual(gate.advance(name, gate.restore(name, current)), current)

    def test_wrong_route_not_normalized(self):
        self.assertEqual(c.restore("unknown.html", NEW_ASK, self.root), NEW_ASK)
        self.assertEqual(c.advance("unknown.html", OLD_ASK, self.root), OLD_ASK)
        row = copy.deepcopy(self.manifest)
        row["layer"] = "other_successor"
        self.write(c.MANIFEST, json.dumps(row).encode())
        with patch.object(c, "SOURCE_SHA", c.canonical(row)):
            with self.assertRaisesRegex(ValueError, "schema"):
                c.mapping(self.root)

    def test_real_file_mutations_rejected(self):
        ask = (c.ROOT / "ask.html").read_bytes()
        exp = (c.ROOT / "ask-experience.js").read_bytes()
        span = json.loads((c.ROOT / c.MANIFEST).read_text(encoding="utf-8"))["files"]["ask.html"]["spans"][0]
        cases = [
            ("ask.html", "altered-inside", ask.replace(b"bringEntryIntoView", b"bringEntryIntoVieX", 1)),
            ("ask.html", "altered-older-layer", ask[:9750] + bytes([ask[9750] ^ 1]) + ask[9751:]),
            ("ask.html", "unrelated-append", ask + b" "),
            ("ask.html", "removed-span", ask[:span["start"]] + ask[span["end"]:]),
            ("ask-experience.js", "altered-inside", exp.replace(b"focusLatestAnswer(addedAnswer)", b"focusLatestAnswer(addedAnsweX)", 1)),
            ("ask-experience.js", "unrelated-append", exp + b" "),
        ]
        for name, label, mutated in cases:
            raw = (c.ROOT / name).read_bytes()
            self.assertNotEqual(mutated, raw, label)
            self.assertEqual(c.restore(name, mutated, c.ROOT), mutated, label)
            with patch.multiple(c, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                root = self.real_root("mut-" + name.split(".")[0] + "-" + label, name, mutated)
                with self.assertRaisesRegex(ValueError, "Changed entry scroll successor page", msg=label):
                    c.check(root)

    def test_changed_span_manifest_and_pin_rejected(self):
        raw = (self.root / c.MANIFEST).read_bytes()
        changed = copy.deepcopy(self.manifest)
        changed["files"]["ask.html"]["spans"][0]["start"] += 1
        self.write(c.MANIFEST, json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError, "Changed entry scroll successor manifest"):
            c.mapping(self.root)
        with patch.object(c, "SOURCE_SHA", c.canonical(changed)):
            with self.assertRaises(ValueError):
                c.mapping(self.root)
        changed = copy.deepcopy(self.manifest)
        changed["files"]["ask-experience.js"]["before_sha256"] = "0" * 64
        self.write(c.MANIFEST, json.dumps(changed).encode())
        with patch.object(c, "SOURCE_SHA", c.canonical(changed)):
            with self.assertRaisesRegex(ValueError, "Wrong entry scroll predecessor"):
                c.mapping(self.root)
        self.write(c.MANIFEST, raw)

    def test_missing_files_rejected(self):
        for name in [c.MANIFEST, "ask.html", "ask-experience.js"]:
            path = self.root / name
            raw = path.read_bytes()
            path.unlink()
            with self.assertRaises((ValueError, OSError)):
                c.check(self.root)
            self.write(name, raw)


if __name__ == "__main__":
    unittest.main()
