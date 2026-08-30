from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = list((ROOT / 'answers').glob('*.html')) + list((ROOT / 'art-study').glob('*.html'))

HEADER_RE = re.compile(
    r'<header class="answer-hero nested"><div><div class="eyebrow">(?P<eyebrow>.*?)</div><h1>(?P<title>.*?)</h1></div></header>',
    re.S,
)


def migrate(path: Path):
    text = path.read_text(encoding='utf-8')
    text = text.replace('FocusChrist', 'focusChrist')
    if '../site-system.css' not in text:
        text = text.replace('<link rel="stylesheet" href="../answer-styles.css">', '<link rel="stylesheet" href="../answer-styles.css"><link rel="stylesheet" href="../site-system.css">', 1)
    text = re.sub(r'<body(?![^>]*class=)([^>]*)>', r'<body class="fc-site"\1>', text, count=1)

    def replace_header(match):
        eyebrow = match.group('eyebrow').strip()
        title = match.group('title').strip()
        return f'''<div class="fc-visual-hero fc-visual-hero--christ" aria-label="Jesus Christ"></div><section class="fc-page-intro" aria-labelledby="nested-page-title"><div class="fc-container--standard"><p class="fc-eyebrow">{eyebrow}</p><h1 class="fc-display" id="nested-page-title">{title}</h1></div></section>'''

    text, count = HEADER_RE.subn(replace_header, text, count=1)
    if count != 1:
        raise SystemExit(f'{path.relative_to(ROOT)}: nested header migration failed')

    text = re.sub(r'<footer(?![^>]*data-focuschrist-footer)([^>]*)>', r'<footer class="fc-footer" data-focuschrist-footer="standard"\1>', text, count=1)
    path.write_text(text, encoding='utf-8')
    print('migrated', path.relative_to(ROOT))


def main():
    for path in PAGES:
        migrate(path)


if __name__ == '__main__':
    main()
