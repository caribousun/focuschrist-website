"""Negative controls for the A047 evaluator corrections successor layer.

Synthetic fixture round trips plus the real-candidate round trip, the
full historical chain round trip through the continue-motion binding
(this layer strips to the display-gate successor's after-state, that
layer strips to the motion map's after pin for site-common.js, and the
motion chain reconstructs its before pin), and the required mutations:
an altered token inside a registered span, an altered older-layer
token, and an unrelated append are all rejected, and a tampered span
manifest or pin is rejected. The layer records no finished in-tree
review; Jeff's independent re-review of the PR head carrying this
registration (J-2026-10-24-074 conditions C1-C3) is delivered on the
channel and gates merge.
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
import evaluator_corrections_successor as g

REAL_BEFORE = dict(g.BEFORE)
REAL_AFTER = dict(g.AFTER)
REAL_SOURCE_SHA = g.SOURCE_SHA

OLD = b"header\n    evaluate(text) {\n    body();\n"
NEW = b"header\n    helper(text);\n    evaluate(text) {\n    body();\n"
FIXTURE_BEFORE = {"site-common.js": g.sha(OLD)}
FIXTURE_AFTER = {"site-common.js": g.sha(NEW)}


def fixture_manifest():
    import difflib
    bl, al = OLD.splitlines(keepends=True), NEW.splitlines(keepends=True)
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
    return {"schema": 1, "layer": "evaluator_corrections_successor",
            "files": {"site-common.js": {"before_sha256": FIXTURE_BEFORE["site-common.js"],
                                          "after_sha256": FIXTURE_AFTER["site-common.js"],
                                          "spans": spans}}}


class EvaluatorCorrectionsSuccessorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = fixture_manifest()
        self.write(g.MANIFEST, json.dumps(self.manifest).encode())
        self.write("site-common.js", NEW)
        self.patch = patch.multiple(g, BEFORE=FIXTURE_BEFORE, AFTER=FIXTURE_AFTER,
                                    SOURCE_SHA=g.canonical(self.manifest))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def write(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def test_exact_round_trip_and_gate(self):
        self.assertEqual(g.restore("site-common.js", NEW, self.root), OLD)
        self.assertEqual(g.advance("site-common.js", OLD, self.root), NEW)
        self.assertEqual(g.check(self.root)["status"], "EVALUATOR_CORRECTIONS_SUCCESSOR_EVIDENCE_PASS")

    def test_real_candidate_exact_round_trip(self):
        manifest = json.loads((g.ROOT / g.MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(g.canonical(manifest), REAL_SOURCE_SHA)
        for name, row in manifest["files"].items():
            current = (g.ROOT / name).read_bytes()
            self.assertEqual(g.sha(current), row["after_sha256"], name)
            with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                restored = g.restore(name, current, g.ROOT)
                self.assertEqual(g.sha(restored), row["before_sha256"], name)
                self.assertEqual(g.advance(name, restored, g.ROOT), current, name)

    def test_historical_chain_round_trip(self):
        import continue_motion_binding as gate
        import display_gate_successor as gate_layer
        row = gate.mapping()["files"]["site-common.js"]
        self.assertEqual(row["after_sha256"], gate_layer.BEFORE["site-common.js"])
        self.assertEqual(gate_layer.AFTER["site-common.js"], REAL_BEFORE["site-common.js"])
        self.assertEqual(row["before_sha256"],
                         "fc0ae667fd977c6cd66ef2e649ef9da2cbcf5eee4201094dd90ed48b551e6488")
        current = (gate.ROOT / "site-common.js").read_bytes()
        with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
            self.assertEqual(gate.sha(gate.restore("site-common.js", current)), row["before_sha256"])
            self.assertEqual(gate.advance("site-common.js", gate.restore("site-common.js", current)), current)

    def test_wrong_route_not_normalized(self):
        self.assertEqual(g.restore("unknown.js", NEW, self.root), NEW)
        self.assertEqual(g.advance("unknown.js", OLD, self.root), OLD)
        row = copy.deepcopy(self.manifest)
        row["layer"] = "other_successor"
        self.write(g.MANIFEST, json.dumps(row).encode())
        with patch.object(g, "SOURCE_SHA", g.canonical(row)):
            with self.assertRaisesRegex(ValueError, "schema"):
                g.mapping(self.root)

    def test_real_file_mutations_rejected(self):
        name = "site-common.js"
        raw = (g.ROOT / name).read_bytes()
        span = json.loads((g.ROOT / g.MANIFEST).read_text(encoding="utf-8"))["files"][name]["spans"][0]
        mutations = {
            "altered-inside": raw.replace(b"pastHurtForgivenessRelease", b"pastHurtForgivenessReleasf", 1),
            "altered-older-layer": raw[:100] + bytes([raw[100] ^ 1]) + raw[101:],
            "unrelated-append": raw + b" ",
            "removed-span": raw[:span["start"]] + raw[span["end"]:],
        }
        for label, mutated in mutations.items():
            self.assertNotEqual(mutated, raw, label)
            self.assertEqual(g.restore(name, mutated, g.ROOT), mutated, label)
            with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                root = Path(self.temp.name) / ("mut-" + label)
                root.mkdir()
                (root / Path(g.MANIFEST).parent).mkdir(parents=True)
                (root / g.MANIFEST).write_bytes((g.ROOT / g.MANIFEST).read_bytes())
                (root / name).write_bytes(mutated)
                with self.assertRaisesRegex(ValueError, "Changed evaluator corrections successor page", msg=label):
                    g.check(root)

    def test_changed_span_manifest_and_pin_rejected(self):
        raw = (self.root / g.MANIFEST).read_bytes()
        changed = copy.deepcopy(self.manifest)
        changed["files"]["site-common.js"]["spans"][0]["start"] += 1
        self.write(g.MANIFEST, json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError, "Changed evaluator corrections successor manifest"):
            g.mapping(self.root)
        with patch.object(g, "SOURCE_SHA", g.canonical(changed)):
            with self.assertRaises(ValueError):
                g.mapping(self.root)
        changed = copy.deepcopy(self.manifest)
        changed["files"]["site-common.js"]["before_sha256"] = "0" * 64
        self.write(g.MANIFEST, json.dumps(changed).encode())
        with patch.object(g, "SOURCE_SHA", g.canonical(changed)):
            with self.assertRaisesRegex(ValueError, "Wrong evaluator corrections predecessor"):
                g.mapping(self.root)
        self.write(g.MANIFEST, raw)

    def test_missing_files_rejected(self):
        for name in [g.MANIFEST, "site-common.js"]:
            path = self.root / name
            raw = path.read_bytes()
            path.unlink()
            with self.assertRaises((ValueError, OSError)):
                g.check(self.root)
            self.write(name, raw)


if __name__ == "__main__":
    unittest.main()
