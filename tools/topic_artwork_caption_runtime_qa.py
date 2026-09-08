#!/usr/bin/env python3
"""Run the actual caption DOM fixture in headless Chrome; missing browser fails CI."""
import os
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Result(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = {}
    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.result = dict(attrs)

def main():
    configured = os.environ.get('CHROME_BIN')
    candidates = [configured] if configured else []
    candidates += [shutil.which(name) for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser')]
    if os.name == 'nt':
        for variable in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA'):
            base = os.environ.get(variable)
            if base:
                candidates.append(str(Path(base) / 'Google/Chrome/Application/chrome.exe'))
    chrome = next((str(Path(value)) for value in candidates if value and Path(value).is_file()), None)
    if not chrome:
        raise SystemExit('CAPTION DOM QA FAIL: headless Chrome is required; set CHROME_BIN to its executable')
    with tempfile.TemporaryDirectory(prefix='focus-caption-qa-') as directory:
        root = Path(directory)
        (root / 'tools').mkdir()
        shutil.copyfile(ROOT / 'topic-artwork-details.js', root / 'topic-artwork-details.js')
        fixture = root / 'tools/caption.html'
        shutil.copyfile(ROOT / 'tools/topic_artwork_caption_qa.html.fixture', fixture)
        result = subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-first-run',
            '--no-default-browser-check', '--user-data-dir=' + str(root / 'profile'),
            '--virtual-time-budget=5000', '--dump-dom', fixture.as_uri()],
            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=45)
        parsed = Result()
        parsed.feed(result.stdout)
        if result.returncode or parsed.result.get('data-qa') != 'PASS' or parsed.result.get('data-cases') != '4':
            raise SystemExit('CAPTION DOM QA FAIL: ' + str(parsed.result) + '\n' + result.stderr[-2000:])
    print('CAPTION DOM QA PASS: 4 caption fixtures plus a foundation-picture panel; mixed scripture prose, source and study actions, safe fallback and repeated opening')

if __name__ == '__main__':
    main()
