import base64
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import commission_hand_successor as successor


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


class CommissionHandSuccessorTests(unittest.TestCase):
    def test_real_pages_restore_and_advance(self):
        manifest = json.loads((ROOT / successor.MANIFEST).read_text(encoding="utf-8"))
        for name, record in manifest["files"].items():
            current = (ROOT / name).read_bytes()
            self.assertEqual(successor.sha(current), record["after_sha256"])
            restored = successor.restore(name, current, ROOT)
            self.assertEqual(successor.sha(restored), record["before_sha256"])
            self.assertEqual(successor.advance(name, restored, ROOT), current)

    def test_unrelated_files_pass_through(self):
        data = b"not a successor consumer"
        self.assertEqual(successor.restore("ask.html", data, ROOT), data)
        self.assertEqual(successor.advance("ask.html", data, ROOT), data)

    def _fixture(self, root):
        (root / "docs/commission-hand-successor/rendered").mkdir(parents=True)
        (root / "docs/commission-hand-successor/manifest.json").write_bytes(
            (ROOT / successor.MANIFEST).read_bytes())
        manifest = json.loads((ROOT / successor.MANIFEST).read_text(encoding="utf-8"))
        for name in ("missionary.html", "index.html", "missionary-details.js"):
            (root / name).write_bytes((ROOT / name).read_bytes())
        from PIL import Image
        captures = []
        hashes = {}
        for screen in sorted(successor.SCREENS):
            buffer = io.BytesIO()
            Image.new("RGB", (8, 6), (24, 40, 32)).save(buffer, format="PNG")
            raw = buffer.getvalue()
            relative = f"{successor.RENDERED_DIR}/{screen}.png.b64"
            (root / relative).write_text(base64.encodebytes(raw).decode(), encoding="utf-8")
            digest = successor.sha(raw)
            hashes[screen] = digest
            captures.append({"height": 6, "media": "fixture", "path": relative,
                             "screen": screen, "sha256": digest, "width": 8})
        observations = {"method": "fixture"}
        (root / successor.RENDERED_DIR / "observations.json").write_text(
            json.dumps(observations), encoding="utf-8")
        reviews = {
            "schema": 1,
            "layer": "commission_hand_successor",
            "registration_review": {"decision": "CONCUR", "finished_behavior": True,
                                    "finished_pixels": False, "reviewer": "Jeff",
                                    "scope": "registration-source"},
            "rendered_evidence": {
                "captures": captures,
                "collected_by": "Merlin worker",
                "details_js_sha256": successor.sha((ROOT / "missionary-details.js").read_bytes()),
                "observations_sha256": successor.sha(json.dumps(observations).encode()),
                "pages_sha256": {name: record["after_sha256"] for name, record in manifest["files"].items()},
                "served_git_head": "0" * 40,
            },
            "rendered_review": {"capture_hashes": hashes, "decision": "CONCUR",
                                "finished_behavior": True, "finished_pixels": True,
                                "reviewer": "Jeff", "scope": "rendered-review"},
        }
        (root / successor.REVIEWS).write_text(json.dumps(reviews), encoding="utf-8")
        return reviews

    def test_sealed_fixture_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reviews = self._fixture(root)
            previous = successor.APPROVED_REVIEWS
            successor.APPROVED_REVIEWS = canonical(reviews)
            try:
                self.assertEqual(successor.check(root)["status"],
                                 "COMMISSION_HAND_SUCCESSOR_EVIDENCE_PASS")
            finally:
                successor.APPROVED_REVIEWS = previous

    def test_pending_reviews_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            previous = successor.APPROVED_REVIEWS
            successor.APPROVED_REVIEWS = None
            try:
                with self.assertRaisesRegex(ValueError, "PENDING"):
                    successor.check(root)
            finally:
                successor.APPROVED_REVIEWS = previous

    def test_fabricated_registration_pixels_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reviews = self._fixture(root)
            reviews["registration_review"]["finished_pixels"] = True
            (root / successor.REVIEWS).write_text(json.dumps(reviews), encoding="utf-8")
            previous = successor.APPROVED_REVIEWS
            successor.APPROVED_REVIEWS = canonical(reviews)
            try:
                with self.assertRaisesRegex(ValueError, "Registration review incomplete"):
                    successor.check(root)
            finally:
                successor.APPROVED_REVIEWS = previous

    def test_unbound_rendered_review_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reviews = self._fixture(root)
            reviews["rendered_review"]["capture_hashes"]["missionary-figure-desktop"] = "0" * 64
            (root / successor.REVIEWS).write_text(json.dumps(reviews), encoding="utf-8")
            previous = successor.APPROVED_REVIEWS
            successor.APPROVED_REVIEWS = canonical(reviews)
            try:
                with self.assertRaisesRegex(ValueError, "not bound to the collected captures"):
                    successor.check(root)
            finally:
                successor.APPROVED_REVIEWS = previous

    def test_page_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reviews = self._fixture(root)
            page = root / "missionary.html"
            page.write_bytes(page.read_bytes() + b" ")
            previous = successor.APPROVED_REVIEWS
            successor.APPROVED_REVIEWS = canonical(reviews)
            try:
                with self.assertRaisesRegex(ValueError, "page changed"):
                    successor.check(root)
            finally:
                successor.APPROVED_REVIEWS = previous

    def test_manifest_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            manifest_path = root / successor.MANIFEST
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"]["index.html"]["spans"][0]["occurrences"] = 2
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source changed"):
                successor.check(root)


if __name__ == "__main__":
    unittest.main()
