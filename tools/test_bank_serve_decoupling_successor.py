"""Negative controls for the bank-serve decoupling successor layer.

Synthetic fixture round trips plus the real-candidate round trips for
both registered files, the composed chain round trips (ask.html
through the citation layer, site-common.js through the evaluator and
display-gate layers, both through the continue-motion binding to the
motion map's before pins), and the required mutations: an altered
token inside a registered span, an altered older-layer token, and an
unrelated append are all rejected, and a tampered span manifest or
pin is rejected. The layer records no finished in-tree review; the
independent exact-head review of the PR carrying this registration
gates merge.
"""
import base64
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bank_serve_decoupling_successor as g

REAL_BEFORE = dict(g.BEFORE)
REAL_AFTER = dict(g.AFTER)
REAL_SOURCE_SHA = g.SOURCE_SHA

OLD_ASK = (b"page\n"
           b"        // First check database for relevant entries\n"
           b"        const dbResult = findAnswer(q);\n"
           b"tail\n")
NEW_ASK = (b"page\n"
           b"        const bankLane = window.FocusChristAnswerBankLane;\n"
           b"        if (bankLane) { /* serve with provenance marker */ }\n"
           b"        // First check database for relevant entries\n"
           b"        const dbResult = findAnswer(q);\n"
           b"tail\n")
OLD_SC = (b"head\n"
          b"        if (isPinnedReviewedBankServe(extra)) return ok();\n"
          b"    function isPinnedReviewedBankServe(extra) {\n"
          b"        return !!extra && extra.bankPin.length > 0;\n"
          b"    }\n"
          b"tail\n")
NEW_SC = (b"head\n"
          b"        if (isPinnedReviewedBankServe(extra, text, sources)) return ok();\n"
          b"    function isPinnedReviewedBankServe(extra, text, sources) {\n"
          b"        if (!extra) return false;\n"
          b"        return lane.verifyPinnedServe(claim(extra, text, sources));\n"
          b"    }\n"
          b"tail\n")
FIXTURE_PAIRS = {"ask.html": (OLD_ASK, NEW_ASK), "site-common.js": (OLD_SC, NEW_SC)}
FIXTURE_BEFORE = {name: g.sha(pair[0]) for name, pair in FIXTURE_PAIRS.items()}
FIXTURE_AFTER = {name: g.sha(pair[1]) for name, pair in FIXTURE_PAIRS.items()}


def spans_for(old, new):
    import difflib
    bl, al = old.splitlines(keepends=True), new.splitlines(keepends=True)
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
    return {"schema": 1, "layer": "bank_serve_decoupling_successor",
            "files": {name: {"before_sha256": FIXTURE_BEFORE[name],
                             "after_sha256": FIXTURE_AFTER[name],
                             "spans": spans_for(pair[0], pair[1])}
                      for name, pair in FIXTURE_PAIRS.items()}}


def projected_current(name):
    """The bytes this layer registers for a file, projected out of the
    shipped tree. ask.html carries the entry-scroll successor above
    this layer, so the registered state is the entry-scroll restore
    of the shipped file (the same projection the continue-motion
    binding's decoupling view uses); other files ship at this
    layer's own state."""
    raw = (g.ROOT / name).read_bytes()
    if name == "ask.html":
        from entry_scroll_successor import restore as restore_scroll
        raw = restore_scroll(name, raw, g.ROOT)
    return raw


class BankServeDecouplingSuccessorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = fixture_manifest()
        self.write(g.MANIFEST, json.dumps(self.manifest).encode())
        for name, pair in FIXTURE_PAIRS.items():
            self.write(name, pair[1])
        self.patch = patch.multiple(g, BEFORE=FIXTURE_BEFORE, AFTER=FIXTURE_AFTER,
                                    SOURCE_SHA=g.canonical(self.manifest))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def write(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def test_exact_round_trip_and_gate(self):
        for name, (old, new) in FIXTURE_PAIRS.items():
            self.assertEqual(g.restore(name, new, self.root), old, name)
            self.assertEqual(g.advance(name, old, self.root), new, name)
        self.assertEqual(g.check(self.root)["status"], "BANK_SERVE_DECOUPLING_SUCCESSOR_EVIDENCE_PASS")

    def test_real_candidate_exact_round_trip(self):
        manifest = json.loads((g.ROOT / g.MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(g.canonical(manifest), REAL_SOURCE_SHA)
        for name, row in manifest["files"].items():
            current = projected_current(name)
            self.assertEqual(g.sha(current), row["after_sha256"], name)
            with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                restored = g.restore(name, current, g.ROOT)
                self.assertEqual(g.sha(restored), row["before_sha256"], name)
                self.assertEqual(g.advance(name, restored, g.ROOT), current, name)

    def test_chips_adjunct_lives_inside_the_registered_span(self):
        manifest = json.loads((g.ROOT / g.MANIFEST).read_text(encoding="utf-8"))
        current = projected_current("ask.html")
        self.assertIn(b"ask-followup-chips", current)
        self.assertIn(b"Additional questions", current)
        with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
            restored = g.restore("ask.html", current, g.ROOT)
            self.assertEqual(g.sha(restored), manifest["files"]["ask.html"]["before_sha256"])
            self.assertNotIn(b"ask-followup-chips", restored)
            self.assertEqual(g.advance("ask.html", restored, g.ROOT), current)

    def test_readiness_wait_lives_inside_the_registered_span(self):
        manifest = json.loads((g.ROOT / g.MANIFEST).read_text(encoding="utf-8"))
        current = projected_current("ask.html")
        self.assertIn(b"bankWaitDeadline", current)
        self.assertIn(b"unable to check our approved study sources", current)
        with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
            restored = g.restore("ask.html", current, g.ROOT)
            self.assertEqual(g.sha(restored), manifest["files"]["ask.html"]["before_sha256"])
            self.assertNotIn(b"bankWaitDeadline", restored)
            self.assertEqual(g.advance("ask.html", restored, g.ROOT), current)

    def test_composed_chain_round_trips(self):
        import continue_motion_binding as gate
        with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
            current_ask = (gate.ROOT / "ask.html").read_bytes()
            legacy = json.loads((gate.ROOT / "docs/legacy-answer-repairs-successor/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(legacy["files"]["ask.html"]["after_sha256"], REAL_BEFORE["ask.html"])
            ask_row = gate.mapping()["files"]["ask.html"]
            self.assertEqual(gate.sha(gate.restore("ask.html", current_ask)), ask_row["before_sha256"])
            self.assertEqual(gate.advance("ask.html", gate.restore("ask.html", current_ask)), current_ask)
            current_sc = (gate.ROOT / "site-common.js").read_bytes()
            evaluator = json.loads((gate.ROOT / "docs/evaluator-corrections-successor/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(evaluator["files"]["site-common.js"]["after_sha256"], REAL_BEFORE["site-common.js"])
            sc_row = gate.mapping()["files"]["site-common.js"]
            self.assertEqual(gate.sha(gate.restore("site-common.js", current_sc)), sc_row["before_sha256"])
            self.assertEqual(gate.advance("site-common.js", gate.restore("site-common.js", current_sc)), current_sc)

    def test_wrong_route_not_normalized(self):
        self.assertEqual(g.restore("unknown.html", NEW_ASK, self.root), NEW_ASK)
        self.assertEqual(g.advance("unknown.html", OLD_ASK, self.root), OLD_ASK)
        row = copy.deepcopy(self.manifest)
        row["layer"] = "other_successor"
        self.write(g.MANIFEST, json.dumps(row).encode())
        with patch.object(g, "SOURCE_SHA", g.canonical(row)):
            with self.assertRaisesRegex(ValueError, "schema"):
                g.mapping(self.root)

    def test_real_file_mutations_rejected(self):
        cases = {
            "ask.html": {
                "altered-inside": lambda raw: raw.replace(b"bankResult.pin", b"bankResult.pim", 1),
                "altered-chips-token": lambda raw: raw.replace(b"data-followup-for", b"data-followup-f0r", 1),
                "altered-older-layer": lambda raw: raw[:100] + bytes([raw[100] ^ 1]) + raw[101:],
                "unrelated-append": lambda raw: raw + b" ",
            },
            "site-common.js": {
                "altered-inside": lambda raw: raw.replace(b"verifyPinnedServe({", b"verifyPinnedServf({", 1),
                "altered-older-layer": lambda raw: raw[:100] + bytes([raw[100] ^ 1]) + raw[101:],
                "unrelated-append": lambda raw: raw + b" ",
            },
        }
        manifest = json.loads((g.ROOT / g.MANIFEST).read_text(encoding="utf-8"))
        for name, mutations in cases.items():
            raw = (g.ROOT / name).read_bytes()
            span = manifest["files"][name]["spans"][0]
            mutations["removed-span"] = lambda r, s=span: r[:s["start"]] + r[s["end"]:]
            for label, mutate in mutations.items():
                mutated = mutate(raw)
                self.assertNotEqual(mutated, raw, name + ":" + label)
                self.assertEqual(g.restore(name, mutated, g.ROOT), mutated, name + ":" + label)
                with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                    root = Path(self.temp.name) / ("mut-" + name + "-" + label)
                    root.mkdir()
                    (root / "docs/bank-serve-decoupling-successor").mkdir(parents=True)
                    (root / g.MANIFEST).write_bytes((g.ROOT / g.MANIFEST).read_bytes())
                    (root / name).write_bytes(mutated)
                    other = "site-common.js" if name == "ask.html" else "ask.html"
                    (root / other).write_bytes((g.ROOT / other).read_bytes())
                    with self.assertRaisesRegex(ValueError, "Changed bank serve decoupling successor page", msg=name + ":" + label):
                        g.check(root)

    def test_changed_span_manifest_and_pin_rejected(self):
        raw = (self.root / g.MANIFEST).read_bytes()
        changed = copy.deepcopy(self.manifest)
        changed["files"]["ask.html"]["spans"][0]["start"] += 1
        self.write(g.MANIFEST, json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError, "Changed bank serve decoupling successor manifest"):
            g.mapping(self.root)
        with patch.object(g, "SOURCE_SHA", g.canonical(changed)):
            with self.assertRaises(ValueError):
                g.mapping(self.root)
        changed = copy.deepcopy(self.manifest)
        changed["files"]["site-common.js"]["before_sha256"] = "0" * 64
        self.write(g.MANIFEST, json.dumps(changed).encode())
        with patch.object(g, "SOURCE_SHA", g.canonical(changed)):
            with self.assertRaisesRegex(ValueError, "Wrong bank serve decoupling predecessor"):
                g.mapping(self.root)
        self.write(g.MANIFEST, raw)

    def test_missing_files_rejected(self):
        for name in [g.MANIFEST, "ask.html", "site-common.js"]:
            path = self.root / name
            raw = path.read_bytes()
            path.unlink()
            with self.assertRaises((ValueError, OSError)):
                g.check(self.root)
            self.write(name, raw)


if __name__ == "__main__":
    unittest.main()
