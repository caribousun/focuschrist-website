#!/usr/bin/env python3
"""Regression controls for required map inline-script and existing text binding."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import static_content_audit as audit


class ScriptBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name, value in [('ROOT', self.root), ('LEDGER', self.root/'content-audit.json')]:
            patcher = patch.object(audit, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.first = b'<script>const story = {desc:"Original narrative", source:"https://example.test/source"};</script>'
        self.second = b'<script type="application/json">{"source":"second"}</script>'
        self.raw = b'<p>Original prose.</p>\r\n' + self.first + b'\r\n' + self.second
        self.records = []
        for name in sorted(audit.INLINE_SCRIPT_ROUTES) + ['ordinary.html']:
            path = self.root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.raw)
            record = {'path':name, 'status':'non-source-dependent', 'reviewed_on':'2026-10-04',
                      'review_standard':'synthetic test fixture', 'published_text_sha256':audit.content_hash(path)}
            if name in audit.INLINE_SCRIPT_ROUTES:
                record['reviewed_inline_script_sha256'] = audit.inline_script_hash(path)
            self.records.append(record)
        self.save()

    def save(self):
        audit.LEDGER.write_text(json.dumps({'documents':self.records}), encoding='utf-8')

    def validate(self, expected, message=''):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = audit.validate()
        self.assertEqual(result, expected, out.getvalue())
        self.assertIn(message, out.getvalue())

    def test_valid_and_out_of_scope(self):
        self.validate(0)
        (self.root/'ordinary.html').write_bytes(self.raw.replace(b'Original narrative', b'Other narrative'))
        self.validate(0)

    def test_required_fields(self):
        for record in self.records:
            if record['path'] not in audit.INLINE_SCRIPT_ROUTES:
                continue
            with self.subTest(route=record['path']):
                saved = record.pop('reviewed_inline_script_sha256')
                self.save()
                self.validate(1, 'inline script review missing or changed')
                record['reviewed_inline_script_sha256'] = saved
                self.save()

    def test_mutations(self):
        changes = {
            'description':self.raw.replace(b'Original narrative', b'Changed narrative'),
            'source':self.raw.replace(b'https://example.test/source', b'https://example.test/wrong'),
            'add':self.raw + b'<script>newCode()</script>',
            'add_empty':self.raw + b'<script></script>',
            'remove':self.raw.replace(self.first, b''),
            'reorder':b'<p>Original prose.</p>\r\n' + self.second + b'\r\n' + self.first,
            'attributes':self.raw.replace(b'<script>', b'<script type="module">'),
            'raw_newlines':self.raw.replace(b'\r\n', b'\n').replace(b'Original narrative', b'Original\r\nnarrative'),
        }
        for name in sorted(audit.INLINE_SCRIPT_ROUTES):
            path = self.root/name
            for label, changed in changes.items():
                with self.subTest(route=name, mutation=label):
                    path.write_bytes(changed)
                    self.validate(1, 'inline script review missing or changed')
                    path.write_bytes(self.raw)

    def test_outside_script_keeps_existing_gate(self):
        for name in sorted(audit.INLINE_SCRIPT_ROUTES):
            path = self.root/name
            original_hash = audit.inline_script_hash(path)
            path.write_bytes(self.raw.replace(b'Original prose', b'Changed prose'))
            self.assertEqual(audit.inline_script_hash(path), original_hash)
            self.validate(1, 'published wording changed after review')
            path.write_bytes(self.raw)

    def test_raw_parser_boundaries(self):
        raw = b'<!-- <script>ignored</script> --><SCRIPT data-x=">">a &amp; b\r\n</SCRIPT><script src="x.js"></script><script>c</script>'
        parser = audit.InlineScriptParser(raw)
        parser.feed(raw.decode('latin-1'))
        self.assertEqual(parser.blocks, [b'<SCRIPT data-x=">">a &amp; b\r\n</SCRIPT>', b'<script>c</script>'])

    def test_unterminated_script(self):
        path = self.root/next(iter(audit.INLINE_SCRIPT_ROUTES))
        path.write_bytes(self.raw + b'<script>unterminated')
        self.validate(1, 'unterminated inline script')


if __name__ == '__main__':
    unittest.main()
