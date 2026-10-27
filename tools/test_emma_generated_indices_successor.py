"""Finite exact-pair and negative controls; synthetic pins are not approvals."""
import base64
import copy
import difflib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import emma_generated_indices_successor as gate


def spans(before, after):
    old, new = before.splitlines(keepends=True), after.splitlines(keepends=True)
    offsets = [0]
    for line in new:
        offsets.append(offsets[-1] + len(line))
    return [{"start": offsets[k], "end": offsets[l],
             "previous_b64": base64.b64encode(b"".join(old[i:j])).decode(),
             "current_b64": base64.b64encode(b"".join(new[k:l])).decode()}
            for tag, i, j, k, l in difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes()
            if tag != "equal"]


class SyntheticIndicesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pairs = {name: (name.encode() + b"\nold alpha\nmiddle\nold beta\nend\n",
                            name.encode() + b"\nnew alpha\nmiddle\nnew beta plus\nend\n")
                      for name in gate.BEFORE}
        self.before = {n: gate.sha(pair[0]) for n, pair in self.pairs.items()}
        self.after = {n: gate.sha(pair[1]) for n, pair in self.pairs.items()}
        self.manifest = {"schema": 1, "layer": "emma_generated_indices_successor", "files": {
            name: {"before_sha256": self.before[name], "after_sha256": self.after[name],
                   "before_bytes": len(old), "after_bytes": len(new), "spans": spans(old, new)}
            for name, (old, new) in self.pairs.items()}}
        self.write_manifest(self.manifest)
        for name, (_, new) in self.pairs.items():
            (self.root / name).write_bytes(new)
        p = patch.multiple(gate, BEFORE=self.before, AFTER=self.after, SOURCE_SHA=gate.canonical(self.manifest))
        p.start()
        self.addCleanup(p.stop)

    def write_manifest(self, manifest):
        path = self.root / gate.MANIFEST
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_exact_pairs_round_trip_and_check(self):
        for name, (old, new) in self.pairs.items():
            self.assertEqual(gate.restore(name, new, self.root), old)
            self.assertEqual(gate.advance(name, old, self.root), new)
        self.assertEqual(gate.check(self.root)["files"], sorted(self.pairs))

    def test_baseline_idempotence_and_wrong_names(self):
        for name, (old, new) in self.pairs.items():
            self.assertEqual(gate.restore(name, old, self.root), old)
            self.assertEqual(gate.advance(name, new, self.root), new)
            for wrong in ["other/" + name, "../" + name, "/" + name, "history/emma-hale-smith.html"]:
                self.assertEqual(gate.restore(wrong, new, self.root), new)
                self.assertEqual(gate.advance(wrong, old, self.root), old)

    def test_one_byte_inside_outside_append_and_removed_span_fail_closed(self):
        for name, (old, new) in self.pairs.items():
            span = self.manifest["files"][name]["spans"][0]
            mutations = [new.replace(b"new alpha", b"NEW alpha", 1),
                         bytes([new[0] ^ 1]) + new[1:], new + b" ", new[:span["start"]] + new[span["end"]:]]
            for mutated in mutations:
                self.assertNotEqual(mutated, new)
                self.assertEqual(gate.restore(name, mutated, self.root), mutated)
                self.assertNotEqual(gate.sha(mutated), self.before[name])
                (self.root / name).write_bytes(mutated)
                with self.assertRaisesRegex(ValueError, "changed generated index"):
                    gate.check(self.root)
            (self.root / name).write_bytes(new)
            self.assertEqual(gate.advance(name, old + b" ", self.root), old + b" ")

    def test_unreviewed_manifest_and_unset_pin_rejected(self):
        changed = copy.deepcopy(self.manifest)
        changed["files"]["art-gallery.json"]["spans"].pop()
        self.write_manifest(changed)
        with self.assertRaisesRegex(ValueError, "changed manifest"):
            gate.mapping(self.root)
        self.write_manifest(self.manifest)
        with patch.object(gate, "SOURCE_SHA", None):
            with self.assertRaisesRegex(ValueError, "changed manifest"):
                gate.mapping(self.root)

    def test_structural_corruptions_rejected_even_with_synthetic_repin(self):
        name = "art-gallery.json"
        mutations = [
            lambda m: m.update(schema=True),
            lambda m: m.update(layer="unrelated"),
            lambda m: m.update(extra=True),
            lambda m: m["files"].pop(name),
            lambda m: m["files"].update({"other.json": copy.deepcopy(m["files"][name])}),
            lambda m: m["files"][name].update(before_sha256="0" * 64),
            lambda m: m["files"][name].update(after_sha256="0" * 64),
            lambda m: m["files"][name].update(before_bytes=True),
            lambda m: m["files"][name].update(after_bytes=1),
            lambda m: m["files"][name].update(spans=[]),
            lambda m: m["files"][name]["spans"][0].update(start=True),
            lambda m: m["files"][name]["spans"][0].update(current_b64="?"),
            lambda m: m["files"][name]["spans"].append(copy.deepcopy(m["files"][name]["spans"][0])),
            lambda m: m["files"][name]["spans"][0].update(end=999999),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(self.manifest)
            mutate(changed)
            self.write_manifest(changed)
            with patch.object(gate, "SOURCE_SHA", gate.canonical(changed)):
                with self.assertRaises((ValueError, KeyError, TypeError)):
                    gate.mapping(self.root)

    def test_exact_slice_and_final_digest_are_checked(self):
        name = "art-gallery.json"
        for field, message in [("current_b64", "inverse byte mismatch"), ("previous_b64", "predecessor mismatch")]:
            changed = copy.deepcopy(self.manifest)
            span = changed["files"][name]["spans"][0]
            raw = base64.b64decode(span[field])
            span[field] = base64.b64encode(bytes([raw[0] ^ 1]) + raw[1:]).decode()
            self.write_manifest(changed)
            with patch.object(gate, "SOURCE_SHA", gate.canonical(changed)):
                with self.assertRaisesRegex(ValueError, message):
                    gate.restore(name, self.pairs[name][1], self.root)
        changed = copy.deepcopy(self.manifest)
        span = changed["files"][name]["spans"][0]
        raw = base64.b64decode(span["previous_b64"])
        span["previous_b64"] = base64.b64encode(bytes([raw[0] ^ 1]) + raw[1:]).decode()
        self.write_manifest(changed)
        with patch.object(gate, "SOURCE_SHA", gate.canonical(changed)):
            with self.assertRaisesRegex(ValueError, "forward byte mismatch"):
                gate.advance(name, self.pairs[name][0], self.root)

    def test_missing_and_symlink_evidence_rejected(self):
        name = "art-gallery.json"
        path = self.root / name
        raw = path.read_bytes()
        path.unlink()
        with self.assertRaisesRegex(ValueError, "missing/outside"):
            gate.check(self.root)
        target = self.root / "other.json"
        target.write_bytes(raw)
        path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "missing/outside"):
            gate.check(self.root)
        path.unlink()
        path.write_bytes(raw)
        (self.root / gate.MANIFEST).unlink()
        with self.assertRaisesRegex(ValueError, "missing/outside"):
            gate.restore(name, raw, self.root)


class ActualGeneratedIndicesTests(unittest.TestCase):
    def setUp(self):
        # These are the unchanged historical Emma-layer assertions, NOT a claim
        # that actual current Adams files equal Emma pins. The view first checks
        # all three actual Adams hashes and round trips; Adams tests cover current drift.
        from adams_delivery_successor import predecessor_view
        context = predecessor_view(gate.ROOT)
        self.root = context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)

    def test_both_actual_pairs_and_checks(self):
        self.assertEqual(gate.check(self.root)["files"], sorted(gate.AFTER))
        for name, expected in gate.BEFORE.items():
            current = (self.root / name).read_bytes()
            self.assertEqual(gate.sha(current), gate.AFTER[name])
            prior = gate.restore(name, current)
            self.assertEqual(gate.sha(prior), expected)
            self.assertEqual(gate.advance(name, prior), current)
            self.assertEqual(gate.restore(name, prior), prior)

    def test_actual_current_mutations_not_normalized(self):
        for name in gate.AFTER:
            current = (self.root / name).read_bytes()
            row = gate.mapping()["files"][name]
            start = row["spans"][0]["start"]
            for changed in [current + b" ", bytes([current[0] ^ 1]) + current[1:],
                            current[:start] + bytes([current[start] ^ 1]) + current[start + 1:]]:
                self.assertNotEqual(changed, current)
                self.assertEqual(gate.restore(name, changed), changed)
                self.assertNotEqual(gate.sha(changed), gate.BEFORE[name])
            self.assertEqual(gate.restore("other/" + name, current), current)

    def test_actual_search_composes_to_unchanged_historical_pin(self):
        import timeline_source_import as timeline
        current = (self.root / "site-search-index.json").read_bytes()
        self.assertEqual(gate.sha(timeline.restore_search(current)),
                         "038391c9f469c4c7a24894c629b915851ec097d305e880bdfe12e6f24b3c9e0d")
        for changed in [current + b" ", current.replace(b'"version":1', b'"version":2', 1)]:
            self.assertNotEqual(changed, current)
            self.assertEqual(timeline.restore_search(changed), changed)
        self.assertEqual(gate.BEFORE["art-gallery.json"],
                         timeline.REVIEWED_CONSUMER_INVERSES["art-gallery.json"]["current"])


if __name__ == "__main__":
    unittest.main()
