"""Current published-text dispatch tests; no project gate or HTML/JS execution."""
import ast
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'tools/static_content_audit.py').read_text()
# Load the actual parser and hash functions without importing/executing the
# project's unrelated review gates or invoking validate().
namespace = {'__file__': str(ROOT / 'tools/static_content_audit.py'), 'Path': Path,
             'HTMLParser': HTMLParser, 'hashlib': hashlib, 'html': html, 're': re}
names = {'ROOT', 'LEDGER', 'SKIP_TAGS', 'PUBLISHED_ATTRIBUTES', 'CURRENT_INTEGRATION_ROUTES'}
for node in ast.parse(SOURCE).body:
    selected = isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets)
    selected |= isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in {'PublishedTextParser', 'published_text', 'content_hash', 'current_timeline_51_source_reviewed'}
    if selected:
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'actual-current-content-extractor', 'exec'), namespace)


def raw_digest(raw):
    parser = namespace['PublishedTextParser'](); parser.feed(raw.decode())
    text = re.sub(r'\s+', ' ', html.unescape(' '.join(parser.parts))).strip()
    return hashlib.sha256(text.encode()).hexdigest()


class BytePath:
    def __init__(self, name, raw): self.name, self.raw = name, raw
    def relative_to(self, root): return Path(self.name)
    def read_bytes(self): return self.raw


class CurrentIntegrationContentAuditTests(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads((ROOT / 'content-audit.json').read_text())['documents']
        self.current = namespace['CURRENT_INTEGRATION_ROUTES']

    def test_exact_nine_current_record_hashes_not_historical_projections(self):
        self.assertEqual(len(self.current), 9)
        for row in self.rows:
            if row['path'] not in self.current: continue
            raw = (ROOT / row['path']).read_bytes()
            self.assertEqual(raw_digest(raw), row['published_text_sha256'], row['path'])
            if row['path'] != 'timeline.html':
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row['reviewed_source_sha256'])
            self.assertEqual(namespace['content_hash'](ROOT / row['path']), row['published_text_sha256'])

    def test_current_routes_never_enter_historical_restore(self):
        def forbidden(*args): raise AssertionError('Current copy entered a historical inverse')
        with patch.dict(sys.modules, {'continue_motion_binding': SimpleNamespace(restore=forbidden),
                                     'timeline_source_import': SimpleNamespace(restore_consumers=forbidden)}):
            for name in self.current:
                namespace['content_hash'](ROOT / name)

    def test_changed_current_byte_rejected_even_when_visible_text_unchanged(self):
        for name in self.current:
            raw = (ROOT / name).read_bytes()
            with self.subTest(name=name):
                if name == 'timeline.html':
                    # A formatting-only change is not a visitor content change.
                    self.assertEqual(namespace['content_hash'](BytePath(name, raw + b'\n')), namespace['content_hash'](BytePath(name, raw)))
                else:
                    with self.assertRaises(AssertionError):
                        namespace['content_hash'](BytePath(name, raw + b'\n'))

    def test_unlisted_route_retains_existing_historical_pipeline(self):
        called = []
        def motion(name, raw): called.append(('motion', name)); return b'<p>Historical motion</p>'
        def timeline(name, raw): called.append(('timeline', name)); return b'<p>Historical timeline</p>'
        with patch.dict(sys.modules, {'continue_motion_binding': SimpleNamespace(restore=motion),
                                     'timeline_source_import': SimpleNamespace(restore_consumers=timeline)}):
            value = namespace['content_hash'](BytePath('history/unrelated.html', b'<p>Current</p>'))
        self.assertEqual(called, [('motion', 'history/unrelated.html'), ('timeline', 'history/unrelated.html')])
        self.assertEqual(value, raw_digest(b'<p>Historical timeline</p>'))

    def test_caption_metadata_and_accessible_copy_change_hash(self):
        base = b'<meta name="description" content="One"><img alt="Two"><figure><figcaption>Three</figcaption></figure>'
        for before, after in [(b'One', b'Different metadata'), (b'Two', b'Different alternative'), (b'Three', b'Different caption')]:
            self.assertNotEqual(raw_digest(base), raw_digest(base.replace(before, after)))
        self.assertEqual(raw_digest(base), raw_digest(base + b'<script>unexecuted()</script><style>body{color:red}</style>'))

    def test_timeline_current_source_binding_is_fail_closed(self):
        raw=b'<section><h2>Current event</h2><p>Sourced words.</p></section>'
        reviewed=namespace['current_timeline_51_source_reviewed']
        digest=hashlib.sha256(raw).hexdigest()
        self.assertFalse(reviewed({},raw))
        self.assertFalse(reviewed({'reviewed_timeline_51_source_sha256':digest},raw+b' '))
        self.assertTrue(reviewed({'reviewed_timeline_51_source_sha256':digest},raw))
        name='church-history.html'
        self.assertEqual(namespace['content_hash'](BytePath(name,raw)),raw_digest(raw))
        self.assertNotEqual(namespace['content_hash'](BytePath(name,raw)),namespace['content_hash'](BytePath(name,raw.replace(b'Sourced',b'Changed'))))

    def test_original_validator_assertions_preserved(self):
        original = ast.parse((ROOT / 'docs/emma-hub-content-audit/static-content-audit-a36.py.source').read_text())
        current = ast.parse(SOURCE)
        old = next(n for n in original.body if isinstance(n, ast.FunctionDef) and n.name == 'validate')
        new = next(n for n in current.body if isinstance(n, ast.FunctionDef) and n.name == 'validate')
        # The current-event guard must actually call the exact binding helper;
        # otherwise removing it from the historical AST would hide a bypass.
        guards=[n for n in ast.walk(new) if isinstance(n,ast.If) and 'current timeline event source review pending or changed' in ast.unparse(n)]
        expected=ast.parse("if name in TIMELINE_51_FILES and not current_timeline_51_source_reviewed(record,path.read_bytes()):\n    errors.append(f'{name}: current timeline event source review pending or changed')").body[0]
        self.assertEqual(len(guards),1)
        self.assertEqual(ast.dump(guards[0],include_attributes=False),ast.dump(expected,include_attributes=False))
        imports=[n for n in ast.walk(new) if isinstance(n,ast.ImportFrom) and n.module=='timeline_51_source_successor']
        self.assertEqual(len(imports),1)
        self.assertEqual([(x.name,x.asname) for x in imports[0].names],[('FILES','TIMELINE_51_FILES')])
        # Remove only separately checked additions before comparing the old AST.
        class RemoveCurrentSourceAssertion(ast.NodeTransformer):
            def visit_ImportFrom(self, node):
                if node.module == 'timeline_51_source_successor': return None
                return self.generic_visit(node)
            def visit_If(self, node):
                if 'current integrated source binding missing or changed' in ast.unparse(node) or 'current timeline event source review pending or changed' in ast.unparse(node):
                    return None
                return self.generic_visit(node)
        new = RemoveCurrentSourceAssertion().visit(new)
        self.assertEqual(ast.dump(old, include_attributes=False), ast.dump(new, include_attributes=False))


if __name__ == '__main__':
    unittest.main()
