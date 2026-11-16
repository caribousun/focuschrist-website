"""Isolated immutable inputs for historical search-adapter unit tests only.

Never used by a production validator or to normalize current site evidence.
The adapters still validate their original source/index/manifest hashes.
"""
from contextlib import contextmanager
from pathlib import Path
import subprocess
import tempfile
import timeline_51_search_successor as events
import timeline_search_index_successor as search

COMMIT = '4fb9e51deda2997d6974e80a5dce86a65167841c'

@contextmanager
def historical_search_root(repo):
    with tempfile.TemporaryDirectory(prefix='timeline-historical-search-') as folder:
        root = Path(folder)
        def extract(name):
            raw = subprocess.check_output(['git', '-C', str(repo), 'show', COMMIT+':'+name])
            target = root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            return raw
        raw = extract('site-search-index.json')
        if events.sha(raw) != events.AFTER:
            raise ValueError('Historical search fixture differs from pinned event index')
        extract(events.MANIFEST)
        extract(search.MANIFEST)
        for name in set(events.manifest(root)['source_sha256']) | set(search.SOURCES):
            extract(name)
        # Both inverse operations must validate real pinned inputs before use.
        search.restore(events.restore(raw, root), root)
        yield root

@contextmanager
def historical_review_root(repo):
    """Historical review inputs and required artwork, never today's release evidence."""
    names = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-r', '--name-only', COMMIT], text=True).splitlines()
    selected = [n for n in names if n.endswith('.html') or
                (n.startswith('assets/page-art/emma-journey/') and n.endswith('.webp')) or
                (n.startswith(('docs/timeline', 'docs/reviews/timeline-51')) and n.endswith(('.json', '.csv'))) or
                n in ('content-audit.json', 'art-gallery.json', 'docs/section-panel-inventory.json',
                      'timeline-images.js', 'site-search-index.json',
                      'docs/owner-integration-contract/source-manifest.json')]
    with tempfile.TemporaryDirectory(prefix='timeline-historical-review-') as folder:
        root = Path(folder)
        for name in selected:
            target=root/name
            if Path(name).is_absolute() or '..' in Path(name).parts:
                raise ValueError('Unsafe historical fixture path')
            raw=subprocess.check_output(['git', '-C', str(repo), 'show', COMMIT+':'+name])
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
        yield root
