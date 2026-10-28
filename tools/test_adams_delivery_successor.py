"""Finite exact-pair and negative controls; synthetic pins are not approvals."""
import base64
import copy
import difflib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import adams_delivery_successor as gate
from adams_integration_indices import restore as restore_integration

def historical_input(name):
    if name == "timeline.html":
        # Historical inverse assertions use the frozen predecessor, never the
        # changed current UI as a substitute for the old receipt.
        raw = (gate.ROOT / "docs/timeline-selector/historical-c910.html").read_bytes()
    else:
        raw = (gate.ROOT / name).read_bytes()
    return restore_integration(name, raw)


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
        self.manifest = {"schema": 1, "layer": "adams_delivery_successor", "files": {
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
        self.assertEqual(gate.check_historical(self.root)["files"], sorted(self.pairs))

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
                with self.assertRaisesRegex(ValueError, "changed current delivery"):
                    gate.check_historical(self.root)
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
            gate.check_historical(self.root)
        target = self.root / "other.json"
        target.write_bytes(raw)
        path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "missing/outside"):
            gate.check_historical(self.root)
        path.unlink()
        path.write_bytes(raw)
        (self.root / gate.MANIFEST).unlink()
        with self.assertRaisesRegex(ValueError, "missing/outside"):
            gate.restore(name, raw, self.root)


class ActualGeneratedIndicesTests(unittest.TestCase):
    def test_current_selector_and_index_semantics_without_old_page_fixture(self):
        from timeline_current_indices import validate_current
        result = validate_current(gate.ROOT)
        self.assertEqual(result['status'], 'CURRENT_TIMELINE_INDEX_SEMANTICS_PASS')
        self.assertEqual(gate.check()['files'], sorted(gate.AFTER))

    def test_current_link_and_index_drift_rejected(self):
        from timeline_current_indices import validate_current
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in gate.AFTER:
                (root / name).write_bytes((gate.ROOT / name).read_bytes())
            original = (root / 'timeline.html').read_bytes()
            layout = original.replace(b'fc-timeline-choice__body', b'fc-timeline-choice__body layout-test', 1)
            (root / 'timeline.html').write_bytes(layout)
            validate_current(root)
            broken = original.replace(b'timelines/latter-day-saint-church-history-timeline.html', b'timelines/wrong.html', 1)
            self.assertNotEqual(broken, original)
            (root / 'timeline.html').write_bytes(broken)
            with self.assertRaises(AssertionError): validate_current(root)
            with self.assertRaisesRegex(ValueError, 'current Timeline/index semantics changed'): gate.check(root)
            historical = (gate.ROOT / 'docs/timeline-selector/historical-c910.html').read_bytes()
            (root / 'timeline.html').write_bytes(historical)
            with self.assertRaisesRegex(ValueError, 'current Timeline/index semantics changed'): gate.check(root)
            (root / 'timeline.html').write_bytes(original)
            index = json.loads((root / 'site-search-index.json').read_bytes())
            index['records'] = [r for r in index['records'] if r['url'] != '/timeline.html#adams-1881']
            (root / 'site-search-index.json').write_text(json.dumps(index))
            with self.assertRaises(AssertionError): validate_current(root)

    def test_historical_mapping_remains_unchanged(self):
        # The historical inverse contract remains independently verifiable;
        # it does not attest to the newly generated current indices.
        self.assertEqual(set(gate.mapping()['files']), set(gate.AFTER))


if __name__ == "__main__":
    unittest.main()
