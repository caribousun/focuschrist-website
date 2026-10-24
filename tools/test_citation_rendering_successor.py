"""Negative controls for the A047 citation rendering successor layer.

Synthetic fixture round trips plus the real-candidate round trip, the
full historical chain round trip through the continue-motion binding
(the answer-bank after state, the motion map's after state, then the
motion map's before pin for ask.html), and the required mutations: an
altered token inside a registered span, an altered older-layer token,
and an unrelated append are all rejected, and a tampered span manifest
or pin is rejected. The layer records no finished in-tree review;
Jeff's independent re-review of the PR head carrying this registration
(J-2026-10-24-075 conditions C1-C2) is delivered on the channel and
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
import citation_rendering_successor as c

REAL_BEFORE = dict(c.BEFORE)
REAL_AFTER = dict(c.AFTER)
REAL_SOURCE_SHA = c.SOURCE_SHA

OLD = (b"<script>\n"
       b"    const officialGroup = makeGroup('Official Church sources');\n"
       b"    sources.forEach(function (source) {\n"
       b"        officialList.appendChild(link);\n"
       b"    });\n"
       b"    if (officialList.querySelector('.source-link')) sourceBox.appendChild(officialGroup);\n"
       b"</script>\n")
NEW = (b"<script>\n"
       b"    const officialGroupParts = makeSourcesGroup('sources-group--official', 'Official Church sources');\n"
       b"    const relatedGroupParts = makeSourcesGroup('sources-group--related', 'Related focusChrist study');\n"
       b"    const renderedSourceUrls = new Set();\n"
       b"    sources.forEach(function (source) {\n"
       b"        if (isChurchSource) officialGroupParts.list.appendChild(link);\n"
       b"    });\n"
       b"    if (officialGroupParts.list.querySelector('.source-link')) sourceBox.appendChild(officialGroupParts.group);\n"
       b"    if (relatedGroupParts.list.querySelector('.source-link')) sourceBox.appendChild(relatedGroupParts.group);\n"
       b"</script>\n")
FIXTURE_BEFORE = {"ask.html": c.sha(OLD)}
FIXTURE_AFTER = {"ask.html": c.sha(NEW)}


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
    return {"schema": 1, "layer": "citation_rendering_successor",
            "files": {"ask.html": {"before_sha256": FIXTURE_BEFORE["ask.html"],
                                   "after_sha256": FIXTURE_AFTER["ask.html"],
                                   "spans": spans}}}


class CitationRenderingSuccessorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = fixture_manifest()
        self.write(c.MANIFEST, json.dumps(self.manifest).encode())
        self.write("ask.html", NEW)
        self.patch = patch.multiple(c, BEFORE=FIXTURE_BEFORE, AFTER=FIXTURE_AFTER,
                                    SOURCE_SHA=c.canonical(self.manifest))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def write(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def test_exact_round_trip_and_gate(self):
        self.assertEqual(c.restore("ask.html", NEW, self.root), OLD)
        self.assertEqual(c.advance("ask.html", OLD, self.root), NEW)
        self.assertEqual(c.check(self.root)["status"], "CITATION_RENDERING_SUCCESSOR_EVIDENCE_PASS")

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
        from answer_bank_successor import restore as restore_bank
        row = gate.mapping()["files"]["ask.html"]
        self.assertEqual(row["after_sha256"],
                         "4a5f73ee35fb5cd8d1a9d30109f7daf9f85f7e3913fb5e3cc012a996d6058db3")
        self.assertEqual(row["before_sha256"],
                         "bbeeb8c6e40d4b55a7949ba7544200796457df1ad975fbd2bdb9b75f9d8c8a04")
        current = (gate.ROOT / "ask.html").read_bytes()
        with patch.multiple(c, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
            projected = c.restore("ask.html", current, gate.ROOT)
            self.assertEqual(c.sha(projected), REAL_BEFORE["ask.html"])
            self.assertEqual(gate.sha(restore_bank("ask.html", projected, gate.ROOT)), row["after_sha256"])
            self.assertEqual(gate.sha(gate.restore("ask.html", current)), row["before_sha256"])
            self.assertEqual(gate.advance("ask.html", gate.restore("ask.html", current)), current)

    def test_wrong_route_not_normalized(self):
        self.assertEqual(c.restore("unknown.html", NEW, self.root), NEW)
        self.assertEqual(c.advance("unknown.html", OLD, self.root), OLD)
        row = copy.deepcopy(self.manifest)
        row["layer"] = "other_successor"
        self.write(c.MANIFEST, json.dumps(row).encode())
        with patch.object(c, "SOURCE_SHA", c.canonical(row)):
            with self.assertRaisesRegex(ValueError, "schema"):
                c.mapping(self.root)

    def test_real_file_mutations_rejected(self):
        name = "ask.html"
        raw = (c.ROOT / name).read_bytes()
        span = json.loads((c.ROOT / c.MANIFEST).read_text(encoding="utf-8"))["files"][name]["spans"][0]
        mutations = {
            "altered-inside": raw.replace(b"CHURCH_HOST_DOMAINS", b"CHURCH_HOST_DOMAINZ", 1),
            "altered-older-layer": raw[:9750] + bytes([raw[9750] ^ 1]) + raw[9751:],
            "unrelated-append": raw + b" ",
            "removed-span": raw[:span["start"]] + raw[span["end"]:],
        }
        for label, mutated in mutations.items():
            self.assertNotEqual(mutated, raw, label)
            self.assertEqual(c.restore(name, mutated, c.ROOT), mutated, label)
            with patch.multiple(c, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                root = Path(self.temp.name) / ("mut-" + label)
                root.mkdir()
                (root / "docs/citation-rendering-successor").mkdir(parents=True)
                (root / c.MANIFEST).write_bytes((c.ROOT / c.MANIFEST).read_bytes())
                (root / name).write_bytes(mutated)
                with self.assertRaisesRegex(ValueError, "Changed citation rendering successor page", msg=label):
                    c.check(root)

    def test_changed_span_manifest_and_pin_rejected(self):
        raw = (self.root / c.MANIFEST).read_bytes()
        changed = copy.deepcopy(self.manifest)
        changed["files"]["ask.html"]["spans"][0]["start"] += 1
        self.write(c.MANIFEST, json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError, "Changed citation rendering successor manifest"):
            c.mapping(self.root)
        with patch.object(c, "SOURCE_SHA", c.canonical(changed)):
            with self.assertRaises(ValueError):
                c.mapping(self.root)
        changed = copy.deepcopy(self.manifest)
        changed["files"]["ask.html"]["before_sha256"] = "0" * 64
        self.write(c.MANIFEST, json.dumps(changed).encode())
        with patch.object(c, "SOURCE_SHA", c.canonical(changed)):
            with self.assertRaisesRegex(ValueError, "Wrong citation rendering predecessor"):
                c.mapping(self.root)
        self.write(c.MANIFEST, raw)

    def test_missing_files_rejected(self):
        for name in [c.MANIFEST, "ask.html"]:
            path = self.root / name
            raw = path.read_bytes()
            path.unlink()
            with self.assertRaises((ValueError, OSError)):
                c.check(self.root)
            self.write(name, raw)


if __name__ == "__main__":
    unittest.main()
