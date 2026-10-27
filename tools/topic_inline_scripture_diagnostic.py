#!/usr/bin/env python3
"""Diagnostic-only full-corpus assertion collection; normal acceptance gate unchanged."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'scripture-citation-diagnostic.json'
CHECKER_BLOB = 'afbc0072595732a724ba6ca9bc6b71a0d9873496'
PARSER_BLOB = 'df37a93c78df6205777f86cd2cabee70938dc222'

def binding(path):
    data = path.read_bytes()
    return {'path': path.relative_to(ROOT).as_posix(), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(),
            'git_blob': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()}

def main():
    report = {'schema': 1, 'scope': 'Diagnostic assertion collection only; not release acceptance',
              'status': 'INCOMPLETE', 'errors': [], 'source_bindings': [],
              'normal_checker_unchanged': True,
              'limits': ['Each node reports its first failing assertion; other nodes continue.',
                         'Unexpected non-assertion exceptions stop collection and remain fatal.',
                         'A clean diagnostic is not full site QA or publication approval.']}
    code = 1
    try:
        checker = ROOT / 'tools/topic_inline_scripture_qa.py'
        parser = ROOT / 'tools/answer_study_qa.py'
        for source, expected in [(checker, CHECKER_BLOB), (parser, PARSER_BLOB)]:
            pin = binding(source)
            report['source_bindings'].append(pin)
            assert pin['git_blob'] == expected, 'Diagnostic source binding drift: ' + pin['path']
        source = checker.read_text(encoding='utf-8')
        tree = ast.parse(source)
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'check_scriptures')
        loops = [n for n in ast.walk(fn) if isinstance(n, ast.For)
                 and isinstance(n.target, ast.Name) and n.target.id == 'node'
                 and ast.unparse(n.iter) == 'main.walk()']
        assert len(loops) == 1, 'Exact original per-node predicate loop required'
        loop = loops[0]
        old_body = loop.body
        original_predicates = ast.dump(ast.Module(body=old_body, type_ignores=[]), include_attributes=False)
        handler = ast.parse('''try:
    pass
except AssertionError as error:
    __diagnostic_errors.append({'path': path, 'tag': node.tag,
        'href': node.attrs.get('href'), 'class': node.attrs.get('class'),
        'direct_text': clean(' '.join(node.words))[:1600], 'reason': str(error)[:2400]})
    if len(__diagnostic_errors) > 10000:
        raise RuntimeError('Diagnostic error cap exceeded')
''').body[0]
        handler.body = old_body
        loop.body = [handler]
        assert ast.dump(ast.Module(body=handler.body, type_ignores=[]), include_attributes=False) == original_predicates
        spec = importlib.util.spec_from_file_location('diagnostic_original_checker', checker)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # main guard is false; no checker invocation here.
        namespace = dict(vars(module))
        namespace['__diagnostic_errors'] = report['errors']
        compiled = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
        exec(compile(compiled, str(checker) + ':diagnostic-copy', 'exec'), namespace)
        # Reuse the unchanged main's exact discovery and scope assertions, stopping
        # immediately before its checker call and never executing its PASS print.
        original_main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        prefix = []
        for statement in original_main.body:
            if (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)
                    and isinstance(statement.value.func, ast.Name)
                    and statement.value.func.id == 'check_scriptures'):
                break
            prefix.append(statement)
        else:
            raise AssertionError('Original main checker call not found')
        exec(compile(ast.fix_missing_locations(ast.Module(body=prefix, type_ignores=[])),
                     str(checker) + ':unchanged-discovery', 'exec'), namespace)
        paths, featured = namespace['paths'], namespace['featured']
        assert len(paths) == 40 and len(set(paths)) == 40
        report['checked_routes'] = paths
        report['featured_routes'] = featured
        report['source_bindings'] += [binding(ROOT / p) for p in paths + ['art.html']]
        chapter_paths = sorted((ROOT / 'scripture-data').rglob('*.json'))
        report['scripture_corpus_bindings'] = [binding(p) for p in chapter_paths]
        report['attempted_scripture_links'] = namespace['check_scriptures'](ROOT, paths, featured)
        report['status'] = 'DEFECTS_FOUND' if report['errors'] else 'NO_ASSERTION_DEFECTS_FOUND'
        code = 1 if report['errors'] else 0
    except Exception as error:
        report['status'] = 'FATAL_INCOMPLETE'
        report['fatal'] = {'type': type(error).__name__, 'message': str(error)[:2400],
                           'traceback': traceback.format_exc()[-8000:]}
    data = (json.dumps(report, indent=2) + '\n').encode()
    if len(data) > 2 * 1024 * 1024:
        raise RuntimeError('Diagnostic report exceeds 2 MiB; no truncated success report written')
    OUT.write_bytes(data)
    print(json.dumps({'status': report['status'], 'assertion_errors': len(report['errors']),
                      'checked_routes': len(report.get('checked_routes', [])),
                      'report': OUT.name, 'bytes': len(data), 'release_approval': False}))
    return code

if __name__ == '__main__':
    sys.exit(main())
