"""Negative controls for the Pioneer entry scroll-follow successor layer.

Synthetic fixture round trips plus the real-candidate round trip, the
full historical chain round trip through the continue-motion binding
(for pioneers.html: the legacy-answer-repairs after state, the
answer-bank after state, the motion map's after state, then the
motion map's before pin; for pioneer-experience.js: the answer-bank
after state, the motion map's after state, then its before pin), and
the required mutations: an altered token inside a registered span, an
unrelated append, and a removed span are all rejected, and a tampered
span manifest or pin is rejected. The layer records no finished
in-tree review; Jeff's independent exact-head review of the PR
carrying this registration is delivered on the channel and gates
merge.
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
import pioneer_entry_scroll_successor as c

REAL_BEFORE = dict(c.BEFORE)
REAL_AFTER = dict(c.AFTER)
REAL_SOURCE_SHA = c.SOURCE_SHA

OLD_PH = (b"<script>\n"
          b"    function addMessage(t, i, s = [], extraBtn = null) {\n"
          b"        c.appendChild(d);\n"
          b"        c.scrollTop = 0;\n"
          b"    }\n"
          b"</script>\n")
NEW_PH = (b"<script>\n"
          b"    function bringEntryIntoView(entry) {\n"
          b"        if (!entry || typeof entry.scrollIntoView !== 'function') return;\n"
          b"        entry.scrollIntoView({ behavior: 'auto', block: 'start' });\n"
          b"    }\n"
          b"\n"
          b"    function addMessage(t, i, s = [], extraBtn = null) {\n"
          b"        c.appendChild(d);\n"
          b"        bringEntryIntoView(d);\n"
          b"    }\n"
          b"</script>\n")
OLD_PE = (b"    window.addMessage = function (text, isUser, sources = [], extraBtn = null) {\n"
          b"        box.appendChild(message);\n"
          b"        return message;\n"
          b"    };\n")
NEW_PE = (b"    function bringPioneerEntryIntoView(entry) {\n"
          b"        if (!entry || typeof entry.scrollIntoView !== 'function') return;\n"
          b"        entry.scrollIntoView({ behavior: 'auto', block: 'start' });\n"
          b"    }\n"
          b"\n"
          b"    window.addMessage = function (text, isUser, sources = [], extraBtn = null) {\n"
          b"        box.appendChild(message);\n"
          b"        bringPioneerEntryIntoView(message);\n"
          b"        return message;\n"
          b"    };\n")
FIXTURE_PAIRS = {"pioneers.html": (OLD_PH, NEW_PH), "pioneer-experience.js": (OLD_PE, NEW_PE)}
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
    return {"schema": 1, "layer": "pioneer_entry_scroll_successor", "files": files}


class PioneerEntryScrollSuccessorTests(unittest.TestCase):
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
        (root / "docs/pioneer-entry-scroll-successor").mkdir(parents=True)
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
        self.assertEqual(c.check(self.root)["status"], "PIONEER_ENTRY_SCROLL_SUCCESSOR_EVIDENCE_PASS")

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
        from answer_bank_successor import restore as restore_bank
        with patch.multiple(c, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
            name = "pioneers.html"
            row = gate.mapping()["files"][name]
            current = (gate.ROOT / name).read_bytes()
            projected = c.restore(name, current, gate.ROOT)
            self.assertEqual(c.sha(projected), REAL_BEFORE[name])
            projected = restore_legacy(name, projected, gate.ROOT)
            self.assertEqual(c.sha(projected), "b2b988d240a7d54b60b2d2701fde26f54fa6ca1b63261b3d7f7f9e89377a3bf5")
            self.assertEqual(gate.sha(restore_bank(name, projected, gate.ROOT)), row["after_sha256"])
            self.assertEqual(gate.sha(gate.restore(name, current)), row["before_sha256"])
            self.assertEqual(gate.advance(name, gate.restore(name, current)), current)
            name = "pioneer-experience.js"
            row = gate.mapping()["files"][name]
            current = (gate.ROOT / name).read_bytes()
            projected = c.restore(name, current, gate.ROOT)
            self.assertEqual(c.sha(projected), REAL_BEFORE[name])
            self.assertEqual(gate.sha(restore_bank(name, projected, gate.ROOT)), row["after_sha256"])
            self.assertEqual(gate.sha(gate.restore(name, current)), row["before_sha256"])
            self.assertEqual(gate.advance(name, gate.restore(name, current)), current)

    def test_wrong_route_not_normalized(self):
        self.assertEqual(c.restore("unknown.html", NEW_PH, self.root), NEW_PH)
        self.assertEqual(c.advance("unknown.html", OLD_PH, self.root), OLD_PH)
        row = copy.deepcopy(self.manifest)
        row["layer"] = "other_successor"
        self.write(c.MANIFEST, json.dumps(row).encode())
        with patch.object(c, "SOURCE_SHA", c.canonical(row)):
            with self.assertRaisesRegex(ValueError, "schema"):
                c.mapping(self.root)

    def test_real_file_mutations_rejected(self):
        ph = (c.ROOT / "pioneers.html").read_bytes()
        pe = (c.ROOT / "pioneer-experience.js").read_bytes()
        span = json.loads((c.ROOT / c.MANIFEST).read_text(encoding="utf-8"))["files"]["pioneers.html"]["spans"][0]
        cases = [
            ("pioneers.html", "altered-inside", ph.replace(b"bringEntryIntoView", b"bringEntryIntoVieX", 1)),
            ("pioneers.html", "unrelated-append", ph + b" "),
            ("pioneers.html", "removed-span", ph[:span["start"]] + ph[span["end"]:]),
            ("pioneer-experience.js", "altered-inside", pe.replace(b"bringPioneerEntryIntoView(message)", b"bringPioneerEntryIntoVieX(message)", 1)),
            ("pioneer-experience.js", "unrelated-append", pe + b" "),
        ]
        for name, label, mutated in cases:
            raw = (c.ROOT / name).read_bytes()
            self.assertNotEqual(mutated, raw, label)
            self.assertEqual(c.restore(name, mutated, c.ROOT), mutated, label)
            with patch.multiple(c, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                root = self.real_root("mut-" + name.split(".")[0] + "-" + label, name, mutated)
                with self.assertRaisesRegex(ValueError, "Changed pioneer entry scroll successor page", msg=label):
                    c.check(root)

    def test_changed_span_manifest_and_pin_rejected(self):
        raw = (self.root / c.MANIFEST).read_bytes()
        changed = copy.deepcopy(self.manifest)
        changed["files"]["pioneers.html"]["spans"][0]["start"] += 1
        self.write(c.MANIFEST, json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError, "Changed pioneer entry scroll successor manifest"):
            c.mapping(self.root)
        with patch.object(c, "SOURCE_SHA", c.canonical(changed)):
            with self.assertRaises(ValueError):
                c.mapping(self.root)
        changed = copy.deepcopy(self.manifest)
        changed["files"]["pioneer-experience.js"]["before_sha256"] = "0" * 64
        self.write(c.MANIFEST, json.dumps(changed).encode())
        with patch.object(c, "SOURCE_SHA", c.canonical(changed)):
            with self.assertRaisesRegex(ValueError, "Wrong pioneer entry scroll predecessor"):
                c.mapping(self.root)
        self.write(c.MANIFEST, raw)

    def test_missing_files_rejected(self):
        for name in [c.MANIFEST, "pioneers.html", "pioneer-experience.js"]:
            path = self.root / name
            raw = path.read_bytes()
            path.unlink()
            with self.assertRaises((ValueError, OSError)):
                c.check(self.root)
            self.write(name, raw)


if __name__ == "__main__":
    unittest.main()
