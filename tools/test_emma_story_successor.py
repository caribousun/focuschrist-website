"""Negative controls for the Emma story successor layer.

Synthetic fixture round trips plus the real-candidate round trip, and
the required mutations: an altered token inside a registered span,
an altered token outside every span, an unrelated append, and a
removed span are all rejected, and a tampered span manifest or pin
is rejected. The layer records no finished in-tree review; the
finished candidate's independent review is Jeff's exact-bytes
review on the channel, and publication requires Albert's
concurrence on the finished package.
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
import emma_story_successor as c
from emma_hub_citation_successor import restore as restore_hub_citations
from owner_integration_successor import restore as restore_owner

REAL_BEFORE = dict(c.BEFORE)
REAL_AFTER = dict(c.AFTER)
REAL_SOURCE_SHA = c.SOURCE_SHA

NAME = "history/emma-hale-smith.html"
OLD_HUB = (b"<section><p>Luke gives us a quiet place to pause.</p>\n"
           b"<p>Emma was in the carriage.</p></section>\n")
NEW_HUB = (b"<section><p>Family tradition tells of Emma praying in the woods.</p>\n"
           b"<p>Emma was in the carriage.</p>\n"
           b"<p><a href=\"emma-elect-lady.html\">Continue with An Elect Lady</a></p></section>\n")
FIXTURE_PAIRS = {NAME: (OLD_HUB, NEW_HUB)}
FIXTURE_BEFORE = {NAME: c.sha(OLD_HUB)}
FIXTURE_AFTER = {NAME: c.sha(NEW_HUB)}


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
    return {"schema": 1, "layer": "emma_story_successor",
            "files": {NAME: {"before_sha256": FIXTURE_BEFORE[NAME],
                             "after_sha256": FIXTURE_AFTER[NAME],
                             "spans": fixture_spans(OLD_HUB, NEW_HUB)}}}


class EmmaStorySuccessorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = fixture_manifest()
        self.write(c.MANIFEST, json.dumps(self.manifest).encode())
        self.write(NAME, NEW_HUB)
        self.patch = patch.multiple(c, BEFORE=FIXTURE_BEFORE, AFTER=FIXTURE_AFTER,
                                    SOURCE_SHA=c.canonical(self.manifest))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def write(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def real_root(self, label, mutated_raw=None):
        root = Path(self.temp.name) / label
        root.mkdir()
        (root / "docs/emma-story-successor").mkdir(parents=True)
        (root / c.MANIFEST).write_bytes((c.ROOT / c.MANIFEST).read_bytes())
        raw = restore_hub_citations(NAME, restore_owner(NAME, (c.ROOT / NAME).read_bytes(), c.ROOT), c.ROOT)
        if mutated_raw is not None:
            raw = mutated_raw
        (root / NAME).parent.mkdir(parents=True, exist_ok=True)
        (root / NAME).write_bytes(raw)
        return root

    def test_exact_round_trip_and_gate(self):
        self.assertEqual(c.restore(NAME, NEW_HUB, self.root), OLD_HUB)
        self.assertEqual(c.advance(NAME, OLD_HUB, self.root), NEW_HUB)
        self.assertEqual(c.check(self.root)["status"], "EMMA_STORY_SUCCESSOR_EVIDENCE_PASS")

    def test_real_candidate_exact_round_trip(self):
        manifest = json.loads((c.ROOT / c.MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(c.canonical(manifest), REAL_SOURCE_SHA)
        current = restore_hub_citations(NAME, restore_owner(NAME, (c.ROOT / NAME).read_bytes(), c.ROOT), c.ROOT)
        self.assertEqual(c.sha(current), manifest["files"][NAME]["after_sha256"])
        with patch.multiple(c, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
            restored = c.restore(NAME, current, c.ROOT)
            self.assertEqual(c.sha(restored), manifest["files"][NAME]["before_sha256"])
            self.assertEqual(c.advance(NAME, restored, c.ROOT), current)

    def test_wrong_route_not_normalized(self):
        self.assertEqual(c.restore("unknown.html", NEW_HUB, self.root), NEW_HUB)
        self.assertEqual(c.advance("unknown.html", OLD_HUB, self.root), OLD_HUB)
        row = copy.deepcopy(self.manifest)
        row["layer"] = "other_successor"
        self.write(c.MANIFEST, json.dumps(row).encode())
        with patch.object(c, "SOURCE_SHA", c.canonical(row)):
            with self.assertRaisesRegex(ValueError, "schema"):
                c.mapping(self.root)

    def test_real_file_mutations_rejected(self):
        raw = restore_hub_citations(NAME, restore_owner(NAME, (c.ROOT / NAME).read_bytes(), c.ROOT), c.ROOT)
        span = json.loads((c.ROOT / c.MANIFEST).read_text(encoding="utf-8"))["files"][NAME]["spans"][0]
        cases = [
            ("altered-inside", raw.replace(b"grid-column: span 2", b"grid-column: span 3", 1)),
            ("altered-outside", raw[:100] + bytes([raw[100] ^ 1]) + raw[101:]),
            ("unrelated-append", raw + b" "),
            ("removed-span", raw[:span["start"]] + raw[span["end"]:]),
        ]
        for label, mutated in cases:
            self.assertNotEqual(mutated, raw, label)
            with patch.multiple(c, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
                self.assertEqual(c.restore(NAME, mutated, c.ROOT), mutated, label)
                root = self.real_root("mut-" + label, mutated)
                with self.assertRaisesRegex(ValueError, "Changed Emma story successor page", msg=label):
                    c.check(root)

    def test_changed_span_manifest_and_pin_rejected(self):
        raw = (self.root / c.MANIFEST).read_bytes()
        changed = copy.deepcopy(self.manifest)
        changed["files"][NAME]["spans"][0]["start"] += 1
        self.write(c.MANIFEST, json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError, "Changed Emma story successor manifest"):
            c.mapping(self.root)
        with patch.object(c, "SOURCE_SHA", c.canonical(changed)):
            with self.assertRaises(ValueError):
                c.mapping(self.root)
        changed = copy.deepcopy(self.manifest)
        changed["files"][NAME]["before_sha256"] = "0" * 64
        self.write(c.MANIFEST, json.dumps(changed).encode())
        with patch.object(c, "SOURCE_SHA", c.canonical(changed)):
            with self.assertRaisesRegex(ValueError, "Wrong Emma story successor predecessor"):
                c.mapping(self.root)
        self.write(c.MANIFEST, raw)

    def test_missing_files_rejected(self):
        for name in [c.MANIFEST, NAME]:
            path = self.root / name
            raw = path.read_bytes()
            path.unlink()
            with self.assertRaises((ValueError, OSError)):
                c.check(self.root)
            self.write(name, raw)


if __name__ == "__main__":
    unittest.main()
