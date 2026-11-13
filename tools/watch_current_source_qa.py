"""Check unchanged Watch source from the bounded November 2 release.

This verifies source continuity and generator coherence, not a new publication
approval, historical whole-site acceptance, or mobile/browser behavior.
"""
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RELEASE_COMMIT = '722b5b792575fc352a368496d5120bd23c4db70f'
# Retained public workflow 48c040b0971d9a1842a6dcd3993cba4ef1892138.
SOURCE_PINS = {
    'watch.html': 'ca11d19f5cad12c2478ae875dc056e4e5247aac5e3bfde176a4aaf2472397e3b',
    'docs/watch-shorts.json': '13f5ea644b1781af325aee4f0344e83e614b3fd6d1e03fe4eb5e26d25db5b664',
    'assets/shorts/please-choose-to-stay-wilcox-20261031.png': '8eeaff370d942f18598b921f7577298d2b3751d124c2f67e6879000bd16f6ee6',
}

def check_sources(root=ROOT):
    root = Path(root).resolve()
    for name, expected in SOURCE_PINS.items():
        path = root
        for part in Path(name).parts:
            path = path / part
            if path.is_symlink():
                raise ValueError('Symlink in Watch source: ' + name)
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError('Missing or unsafe Watch source: ' + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Changed Watch source: ' + name)
    return {'source_commit': RELEASE_COMMIT, 'files': len(SOURCE_PINS)}

if __name__ == '__main__':
    result = check_sources()
    subprocess.run([sys.executable, str(ROOT/'tools/build_watch_shorts.py'), '--check'], cwd=ROOT, check=True)
    print('Watch source continuity and generator PASS:', result)
    print('No release, global QA, or browser/mobile acceptance is implied.')
