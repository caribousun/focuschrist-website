"""Negative controls for the legacy answer repairs successor layer.

Synthetic fixture round trips plus the real-candidate round trip, the
full historical chain round trip through the continue-motion binding
(the citation after state and the answer-bank after state, the motion
map's after state, then the motion map's before pin, for both pages),
and the required mutations: an altered token inside a registered span,
an altered older-layer token, and an unrelated append are all
rejected, and a tampered span manifest or pin is rejected. The layer
records no finished in-tree review; Jeff's independent re-review of
the PR head carrying this registration (J-2026-10-25-081 conditions
C1-C2, registry figures as corrected by J-2026-10-25-082) is delivered
on the channel and gates merge.
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
import legacy_answer_repairs_successor as g

REAL_BEFORE = dict(g.BEFORE)
REAL_AFTER = dict(g.AFTER)
REAL_SOURCE_SHA = g.SOURCE_SHA

ASK_OLD = (b"<script>\n"
           b"    const qaDatabase = {\n"
           b"        'is it true': { answer: \"Moroni's invitation is the old text.\" },\n"
           b"        'agency': { answer: \"Agency is the power to choose.\" }\n"
           b"    };\n"
           b"</script>\n")
ASK_NEW = (b"<script>\n"
           b"    const qaDatabase = {\n"
           b"        'is it true': { answer: \"Moroni's invitation is the repaired text, warmer and fuller.\" },\n"
           b"        'children who die': { answer: \"Little children are alive in Christ.\" },\n"
           b"        'agency': { answer: \"Agency is the power to choose.\" }\n"
           b"    };\n"
           b"</script>\n")
PIO_OLD = (b"<script>\n"
           b"    const qaDatabase = {\n"
           b"        'tithing': { answer: \"Tithing is one of the old headings.\" }\n"
           b"    };\n"
           b"</script>\n")
PIO_NEW = (b"<script>\n"
           b"    const qaDatabase = {\n"
           b"        'tithing': { answer: \"Tithing is one of the Savior's teachings, repaired.\" }\n"
           b"    };\n"
           b"</script>\n")
FIXTURE_OLD = {"ask.html": ASK_OLD, "pioneers.html": PIO_OLD}
FIXTURE_NEW = {"ask.html": ASK_NEW, "pioneers.html": PIO_NEW}
FIXTURE_BEFORE = {name: g.sha(raw) for name, raw in FIXTURE_OLD.items()}
FIXTURE_AFTER = {name: g.sha(raw) for name, raw in FIXTURE_NEW.items()}


def fixture_manifest():
    import difflib
    files = {}
    for name in FIXTURE_OLD:
        bl = FIXTURE_OLD[name].splitlines(keepends=True)
        al = FIXTURE_NEW[name].splitlines(keepends=True)
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
        files[name] = {"before_sha256": FIXTURE_BEFORE[name],
                       "after_sha256": FIXTURE_AFTER[name],
                       "spans": spans}
    return {"schema": 1, "layer": "legacy_answer_repairs_successor", "files": files}


class LegacyAnswerRepairsSuccessorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = fixture_manifest()
        self.write(g.MANIFEST, json.dumps(self.manifest).encode())
        for name, raw in FIXTURE_NEW.items():
            self.write(name, raw)
        self.patch = patch.multiple(g, BEFORE=FIXTURE_BEFORE, AFTER=FIXTURE_AFTER,
                                    SOURCE_SHA=g.canonical(self.manifest))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def write(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def test_exact_round_trip_and_gate(self):
        for name in FIXTURE_OLD:
            self.assertEqual(g.restore(name, FIXTURE_NEW[name], self.root), FIXTURE_OLD[name], name)
            self.assertEqual(g.advance(name, FIXTURE_OLD[name], self.root), FIXTURE_NEW[name], name)
        self.assertEqual(g.check(self.root)["status"], "LEGACY_ANSWER_REPAIRS_SUCCESSOR_EVIDENCE_PASS")

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
        from citation_rendering_successor import restore as restore_citation
        from answer_bank_successor import restore as restore_bank
        rows = {"ask.html": ("4a5f73ee35fb5cd8d1a9d30109f7daf9f85f7e3913fb5e3cc012a996d6058db3",
                             "bbeeb8c6e40d4b55a7949ba7544200796457df1ad975fbd2bdb9b75f9d8c8a04"),
                "pioneers.html": ("57fe21dc3a92dde1b5c51cddcf872cabe62d1e88a7ec259fc135afaa80cb8b81",
                                  "b2ed6c9a12d25600262997235fa9971972dddd93f0ef26cad852f7ab66ffc0e0")}
        for name, (map_after, map_before) in rows.items():
            row = gate.mapping()["files"][name]
            self.assertEqual(row["after_sha256"], map_after, name)
            self.assertEqual(row["before_sha256"], map_before, name)
            current = (gate.ROOT / name).read_bytes()
            with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                projected = g.restore(name, current, gate.ROOT)
                self.assertEqual(g.sha(projected), REAL_BEFORE[name], name)
                if name == "ask.html":
                    projected = restore_citation(name, projected, gate.ROOT)
                    self.assertEqual(g.sha(projected),
                                     "735ccd0d56d7931a651ec8c06759cc849e7895fa55311f8d9d7d6bb36b419612", name)
                self.assertEqual(g.sha(restore_bank(name, projected, gate.ROOT)), row["after_sha256"], name)
                self.assertEqual(g.sha(gate.restore(name, current)), row["before_sha256"], name)
                self.assertEqual(gate.advance(name, gate.restore(name, current)), current, name)

    def test_wrong_route_not_normalized(self):
        self.assertEqual(g.restore("unknown.html", ASK_NEW, self.root), ASK_NEW)
        self.assertEqual(g.advance("unknown.html", ASK_OLD, self.root), ASK_OLD)
        row = copy.deepcopy(self.manifest)
        row["layer"] = "other_successor"
        self.write(g.MANIFEST, json.dumps(row).encode())
        with patch.object(g, "SOURCE_SHA", g.canonical(row)):
            with self.assertRaisesRegex(ValueError, "schema"):
                g.mapping(self.root)

    def test_real_file_mutations_rejected(self):
        manifest = json.loads((g.ROOT / g.MANIFEST).read_text(encoding="utf-8"))
        for name in ("ask.html", "pioneers.html"):
            raw = (g.ROOT / name).read_bytes()
            span = manifest["files"][name]["spans"][0]
            inside = span["start"] + 5
            mutations = {
                "altered-inside": raw[:inside] + bytes([raw[inside] ^ 1]) + raw[inside + 1:],
                "unrelated-append": raw + b" ",
                "removed-span": raw[:span["start"]] + raw[span["end"]:],
            }
            if name == "ask.html":
                # Byte 9750 sits inside the answer-bank layer's registered
                # span (bytes 9707-10028), far above every legacy span.
                mutations["altered-older-layer"] = raw[:9750] + bytes([raw[9750] ^ 1]) + raw[9751:]
            for label, mutated in mutations.items():
                self.assertNotEqual(mutated, raw, (name, label))
                self.assertEqual(g.restore(name, mutated, g.ROOT), mutated, (name, label))
                with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                    root = Path(self.temp.name) / ("mut-" + name + "-" + label)
                    root.mkdir()
                    (root / "docs/legacy-answer-repairs-successor").mkdir(parents=True)
                    (root / g.MANIFEST).write_bytes((g.ROOT / g.MANIFEST).read_bytes())
                    for other in ("ask.html", "pioneers.html"):
                        (root / other).write_bytes(mutated if other == name else (g.ROOT / other).read_bytes())
                    with self.assertRaisesRegex(ValueError, "Changed legacy answer repairs successor page",
                                                 msg=(name, label)):
                        g.check(root)

    def test_changed_span_manifest_and_pin_rejected(self):
        raw = (self.root / g.MANIFEST).read_bytes()
        changed = copy.deepcopy(self.manifest)
        changed["files"]["ask.html"]["spans"][0]["start"] += 1
        self.write(g.MANIFEST, json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError, "Changed legacy answer repairs successor manifest"):
            g.mapping(self.root)
        with patch.object(g, "SOURCE_SHA", g.canonical(changed)):
            with self.assertRaises(ValueError):
                g.mapping(self.root)
        changed = copy.deepcopy(self.manifest)
        changed["files"]["pioneers.html"]["before_sha256"] = "0" * 64
        self.write(g.MANIFEST, json.dumps(changed).encode())
        with patch.object(g, "SOURCE_SHA", g.canonical(changed)):
            with self.assertRaisesRegex(ValueError, "Wrong legacy answer repairs predecessor"):
                g.mapping(self.root)
        self.write(g.MANIFEST, raw)

    def test_missing_files_rejected(self):
        for name in [g.MANIFEST, "ask.html", "pioneers.html"]:
            path = self.root / name
            raw = path.read_bytes()
            path.unlink()
            with self.assertRaises((ValueError, OSError)):
                g.check(self.root)
            self.write(name, raw)


if __name__ == "__main__":
    unittest.main()
