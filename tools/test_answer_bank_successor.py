"""Negative controls for the answer bank (step 1) successor layer.

Synthetic fixture round trips plus real-candidate round trips and the
task-required mutations: stripped prior equals the previous pin, the
full chain reproduces the motion map's before pin, a duplicated
insertion, a truncated insertion, one altered token inside the
insertion, one altered older-layer token, and an unrelated append are
all rejected. The shipped record test asserts the layer's real state
truthfully: Jeff's finished registration-source review (J-2026-10-23-048)
and rendered review (J-2026-10-23-049) are recorded in the real
reviews.json, its status is COMPLETE, and the module pin equals the
record's canonical hash.
"""
import base64
import copy
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import answer_bank_successor as g

REAL_BEFORE = dict(g.BEFORE)
REAL_AFTER = dict(g.AFTER)
REAL_SOURCE_SHA = g.SOURCE_SHA

OLD = {
    "ask.html": b"before page\nrest\n",
    "pioneers.html": b"pioneer\npage\n",
    "pioneer-experience.js": b"function f() {\n  body();\n}\n",
}
INSERT = {
    "ask.html": (12, b"NEW LINE\n"),
    "pioneers.html": (8, b"BANK\n"),
    "pioneer-experience.js": (15, b"  if (bank) return;\n"),
}
NEW = {name: OLD[name][:at] + blob + OLD[name][at:] for name, (at, blob) in INSERT.items()}
FIXTURE_BEFORE = {name: g.sha(raw) for name, raw in OLD.items()}
FIXTURE_AFTER = {name: g.sha(raw) for name, raw in NEW.items()}


def fixture_manifest():
    files = {}
    for name, (at, blob) in INSERT.items():
        files[name] = {
            "before_sha256": FIXTURE_BEFORE[name],
            "after_sha256": FIXTURE_AFTER[name],
            "spans": [{"start": at, "end": at + len(blob), "previous_b64": "",
                       "current_b64": base64.b64encode(blob).decode()}],
        }
    return {"schema": 1, "layer": "answer_bank_successor", "files": files}


class AnswerBankSuccessorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = fixture_manifest()
        self.proof = b"test-only Jeff registration proof"
        self.revproof = b"test-only Jeff rendered proof"
        self.write(g.MANIFEST, json.dumps(self.manifest).encode())
        for name, raw in NEW.items():
            self.write(name, raw)
        self.write("docs/answer-bank-successor/jeff-registration-review-test.json", self.proof)
        self.write("docs/answer-bank-successor/jeff-rendered-review-test.json", self.revproof)
        from PIL import Image
        captures = []
        self.capture_hashes = []
        for screen, size in [("ask-bank-serve-desktop", (8, 6)), ("pioneer-item-phone", (6, 8))]:
            buffer = io.BytesIO()
            Image.new("RGB", size, (24, 40, 32)).save(buffer, format="PNG")
            raw = buffer.getvalue()
            relative = f"{g.RENDERED_DIR}/{screen}.png.b64"
            self.write(relative, base64.encodebytes(raw))
            digest = g.sha(raw)
            self.capture_hashes.append(digest)
            captures.append({"height": size[1], "media": "fixture", "path": relative,
                             "screen": screen, "sha256": digest, "width": size[0]})
        self.observations = {"method": "fixture"}
        self.write(f"{g.RENDERED_DIR}/observations.json", json.dumps(self.observations).encode())
        self.record = {
            "files": dict(FIXTURE_AFTER),
            "layer": "answer_bank_successor",
            "required_reviewers": ["Jeff"],
            "source_sha256": g.canonical(self.manifest),
            "status": "COMPLETE",
            "registration_review": {
                "reviewer": "Jeff", "review_id": "J-TEST-001", "scope": "registration-source",
                "decision": "CONCUR", "finished_pixels": False, "finished_behavior": True,
                "files": dict(FIXTURE_AFTER),
                "evidence": {"path": "docs/answer-bank-successor/jeff-registration-review-test.json",
                             "sha256": g.sha(self.proof)},
            },
            "rendered_evidence": {
                "status": "COLLECTED", "collected_by": "Merlin worker",
                "pages_sha256": dict(FIXTURE_AFTER), "captures": captures,
                "observations": {"path": f"{g.RENDERED_DIR}/observations.json",
                                 "sha256": g.sha(json.dumps(self.observations).encode())},
            },
            "rendered_review": {
                "status": "FINISHED", "reviewer": "Jeff", "review_id": "J-TEST-002",
                "scope": "rendered-review", "decision": "CONCUR", "finished_pixels": True,
                "finished_behavior": True, "files": dict(FIXTURE_AFTER),
                "capture_sha256": list(self.capture_hashes),
                "evidence": {"path": "docs/answer-bank-successor/jeff-rendered-review-test.json",
                             "sha256": g.sha(self.revproof)},
            },
        }
        self.write(g.REVIEWS, json.dumps(self.record).encode())
        self.patch = patch.multiple(g, BEFORE=FIXTURE_BEFORE, AFTER=FIXTURE_AFTER,
                                    SOURCE_SHA=g.canonical(self.manifest),
                                    APPROVED_REVIEWS=g.canonical(self.record))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def write(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def resealed(self, record):
        self.write(g.REVIEWS, json.dumps(record).encode())
        return patch.object(g, "APPROVED_REVIEWS", g.canonical(record))

    def test_exact_round_trip_and_gate(self):
        for name in NEW:
            self.assertEqual(g.restore(name, NEW[name], self.root), OLD[name])
            self.assertEqual(g.advance(name, OLD[name], self.root), NEW[name])
        self.assertEqual(g.check(self.root)["status"], "ANSWER_BANK_SUCCESSOR_EVIDENCE_PASS")

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

    def test_all_historical_map_files_still_round_trip(self):
        import continue_motion_binding as gate
        with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA):
            for name, row in gate.mapping()["files"].items():
                current = (gate.ROOT / name).read_bytes()
                self.assertEqual(gate.sha(gate.restore(name, current)), row["before_sha256"], name)

    def test_wrong_route_not_normalized(self):
        self.assertEqual(g.restore("unknown.html", NEW["ask.html"], self.root), NEW["ask.html"])
        self.assertEqual(g.advance("unknown.html", OLD["ask.html"], self.root), OLD["ask.html"])
        row = copy.deepcopy(self.manifest)
        row["layer"] = "other_successor"
        self.write(g.MANIFEST, json.dumps(row).encode())
        with patch.object(g, "SOURCE_SHA", g.canonical(row)):
            with self.assertRaisesRegex(ValueError, "schema"):
                g.mapping(self.root)

    def test_pending_pin_blocks_even_when_all_scopes_complete(self):
        with patch.object(g, "APPROVED_REVIEWS", None):
            with self.assertRaisesRegex(ValueError, "PENDING"):
                g.check(self.root)

    def test_shipped_record_is_truthfully_complete(self):
        record = json.loads((g.ROOT / g.REVIEWS).read_text(encoding="utf-8"))
        self.assertEqual(record.get("status"), "COMPLETE")
        self.assertEqual(record.get("required_reviewers"), ["Jeff"])
        self.assertEqual(record.get("source_sha256"), REAL_SOURCE_SHA)
        self.assertEqual(record.get("files"), REAL_AFTER)
        registration = record.get("registration_review")
        self.assertIsInstance(registration, dict)
        self.assertEqual(registration.get("reviewer"), "Jeff")
        self.assertEqual(registration.get("review_id"), "J-2026-10-23-048")
        self.assertEqual(registration.get("scope"), "registration-source")
        self.assertEqual(registration.get("decision"), "CONCUR")
        self.assertIs(registration.get("finished_pixels"), False)
        self.assertIs(registration.get("finished_behavior"), True)
        self.assertEqual(registration.get("files"), REAL_AFTER)
        item = registration["evidence"]
        self.assertEqual(item["path"], "docs/answer-bank-successor/J-2026-10-23-048-step1-answer-bank-successor-registration-review.json")
        self.assertEqual(g.sha((g.ROOT / item["path"]).read_bytes()), item["sha256"])
        evidence = record.get("rendered_evidence")
        self.assertIsInstance(evidence, dict)
        self.assertEqual(evidence.get("status"), "COLLECTED")
        self.assertEqual(evidence.get("collected_by"), "Merlin worker")
        self.assertEqual(evidence.get("pages_sha256"), REAL_AFTER)
        captures = evidence.get("captures")
        self.assertEqual(len(captures), 12)
        for cap in captures:
            self.assertEqual(set(cap), {"height", "media", "path", "screen", "sha256", "width"})
            decoded = base64.b64decode((g.ROOT / cap["path"]).read_bytes(), validate=False)
            self.assertEqual(g.sha(decoded), cap["sha256"])
        observations = evidence.get("observations")
        self.assertEqual(observations["path"], g.RENDERED_DIR + "/observations.json")
        self.assertEqual(g.sha((g.ROOT / observations["path"]).read_bytes()), observations["sha256"])
        review = record.get("rendered_review")
        self.assertIsInstance(review, dict)
        self.assertEqual(review.get("status"), "FINISHED")
        self.assertEqual(review.get("reviewer"), "Jeff")
        self.assertEqual(review.get("review_id"), "J-2026-10-23-049")
        self.assertEqual(review.get("scope"), "rendered-review")
        self.assertEqual(review.get("decision"), "CONCUR")
        self.assertIs(review.get("finished_pixels"), True)
        self.assertIs(review.get("finished_behavior"), True)
        self.assertEqual(review.get("files"), REAL_AFTER)
        self.assertEqual(review.get("capture_sha256"), [cap["sha256"] for cap in captures])
        item = review["evidence"]
        self.assertEqual(item["path"], "docs/answer-bank-successor/J-2026-10-23-049-step1-answer-bank-successor-rendered-review.json")
        self.assertEqual(g.sha((g.ROOT / item["path"]).read_bytes()), item["sha256"])
        source = (g.ROOT / "tools/answer_bank_successor.py").read_text(encoding="utf-8")
        self.assertIn('APPROVED_REVIEWS = "' + g.canonical(record) + '"', source)
        self.assertNotIn("APPROVED_REVIEWS = None", source)
        self.assertIn('SOURCE_SHA = "' + REAL_SOURCE_SHA + '"', source)
        with patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA,
                            APPROVED_REVIEWS=g.canonical(record)):
            self.assertEqual(g.check(g.ROOT)["status"], "ANSWER_BANK_SUCCESSOR_EVIDENCE_PASS")

    def _real_tree(self):
        root = Path(self.temp.name) / "real"
        root.mkdir()
        (root / "docs/answer-bank-successor").mkdir(parents=True)
        (root / "docs/answer-bank-successor/manifest.json").write_bytes((g.ROOT / g.MANIFEST).read_bytes())
        for name in REAL_AFTER:
            (root / name).write_bytes((g.ROOT / name).read_bytes())
        return root

    def test_real_page_mutations_rejected(self):
        real = patch.multiple(g, BEFORE=REAL_BEFORE, AFTER=REAL_AFTER, SOURCE_SHA=REAL_SOURCE_SHA)
        with real:
            root = self._real_tree()
            manifest = json.loads((g.ROOT / g.MANIFEST).read_text(encoding="utf-8"))
            name = "ask.html"
            raw = (root / name).read_bytes()
            span = manifest["files"][name]["spans"][0]
            inserted = base64.b64decode(span["current_b64"])
            mutations = {
                "duplicated": raw[:span["start"]] + inserted + raw[span["start"]:],
                "truncated": raw[:span["end"] - 1] + raw[span["end"]:],
                "altered-inside": raw.replace(b"answer-bank-lane.js", b"answer-bank-lanf.js", 1),
                "altered-older-layer": raw[:100] + bytes([raw[100] ^ 1]) + raw[101:],
                "unrelated-append": raw + b" ",
                "removed": raw[:span["start"]] + raw[span["end"]:],
            }
            for label, mutated in mutations.items():
                self.assertNotEqual(mutated, raw, label)
                self.assertEqual(g.restore(name, mutated, root), mutated, label)
                (root / name).write_bytes(mutated)
                with self.assertRaisesRegex(ValueError, "Changed answer bank successor page", msg=label):
                    g.check(root)
                (root / name).write_bytes(raw)
            self.assertEqual(g.sha(g.restore(name, raw, root)), REAL_BEFORE[name])

    def test_changed_span_manifest_and_pin_rejected(self):
        raw = (self.root / g.MANIFEST).read_bytes()
        changed = copy.deepcopy(self.manifest)
        changed["files"]["ask.html"]["spans"][0]["start"] += 1
        self.write(g.MANIFEST, json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError, "Changed answer bank successor manifest"):
            g.mapping(self.root)
        with patch.object(g, "SOURCE_SHA", g.canonical(changed)):
            with self.assertRaises(ValueError):
                g.mapping(self.root)
        changed = copy.deepcopy(self.manifest)
        changed["files"]["ask.html"]["before_sha256"] = "0" * 64
        self.write(g.MANIFEST, json.dumps(changed).encode())
        with patch.object(g, "SOURCE_SHA", g.canonical(changed)):
            with self.assertRaisesRegex(ValueError, "Wrong answer bank predecessor"):
                g.mapping(self.root)
        self.write(g.MANIFEST, raw)

    def test_missing_files_rejected(self):
        for name in [g.MANIFEST, "ask.html", g.REVIEWS]:
            path = self.root / name
            raw = path.read_bytes()
            path.unlink()
            with self.assertRaises((ValueError, OSError)):
                g.check(self.root)
            self.write(name, raw)

    def test_rendered_slots_missing_block_with_missing_message(self):
        for slot in ["rendered_evidence", "rendered_review"]:
            record = copy.deepcopy(self.record)
            record[slot] = {"status": "PENDING"}
            with self.resealed(record):
                with self.assertRaisesRegex(ValueError, "rendered review MISSING"):
                    g.check(self.root)
        record = copy.deepcopy(self.record)
        del record["rendered_review"]
        with self.resealed(record):
            with self.assertRaisesRegex(ValueError, "rendered review MISSING"):
                g.check(self.root)

    def test_tampered_review_records_rejected_even_if_resealed(self):
        edits = []
        row = copy.deepcopy(self.record); row["registration_review"]["decision"] = "PENDING"; edits.append(row)
        row = copy.deepcopy(self.record); row["registration_review"]["finished_pixels"] = True; edits.append(row)
        row = copy.deepcopy(self.record); row["registration_review"]["finished_behavior"] = False; edits.append(row)
        row = copy.deepcopy(self.record); row["registration_review"]["reviewer"] = "Merlin"; edits.append(row)
        row = copy.deepcopy(self.record); row["registration_review"]["scope"] = "rendered"; edits.append(row)
        row = copy.deepcopy(self.record); row["registration_review"]["files"]["ask.html"] = "0" * 64; edits.append(row)
        row = copy.deepcopy(self.record); row["registration_review"]["evidence"]["sha256"] = "0" * 64; edits.append(row)
        row = copy.deepcopy(self.record); row["files"]["ask.html"] = "0" * 64; edits.append(row)
        row = copy.deepcopy(self.record); row["rendered_review"]["reviewer"] = "Merlin"; edits.append(row)
        row = copy.deepcopy(self.record); row["rendered_review"]["capture_sha256"] = ["0" * 64, "0" * 64]; edits.append(row)
        row = copy.deepcopy(self.record); row["rendered_evidence"]["collected_by"] = "Jeff"; edits.append(row)
        for record in edits:
            with self.resealed(record):
                with self.assertRaises(ValueError):
                    g.check(self.root)

    def test_tampered_capture_and_path_escape_rejected(self):
        cap_path = self.record["rendered_evidence"]["captures"][0]["path"]
        raw = (self.root / cap_path).read_bytes()
        mid = len(raw) // 2
        flipped = raw[:mid] + (b"A" if raw[mid:mid + 1] != b"A" else b"B") + raw[mid + 1:]
        self.assertNotEqual(flipped, raw)
        self.write(cap_path, flipped)
        with self.assertRaisesRegex(ValueError, "Changed answer bank rendered evidence"):
            g.check(self.root)
        self.write(cap_path, raw)
        self.assertEqual(g.check(self.root)["status"], "ANSWER_BANK_SUCCESSOR_EVIDENCE_PASS")
        row = copy.deepcopy(self.record)
        row["registration_review"]["evidence"]["path"] = "../outside.txt"
        with self.resealed(row):
            with self.assertRaisesRegex(ValueError, "outside"):
                g.check(self.root)


if __name__ == "__main__":
    unittest.main()
