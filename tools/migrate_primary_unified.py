from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ["ask.html", "answers.html", "art.html", "pioneers.html", "about.html", "watch.html"]


def add_system(path: Path, text: str) -> str:
    if 'site-system.css' not in text:
        text = text.replace('</head>', '    <link rel="stylesheet" href="site-system.css">\n</head>', 1)
    text = re.sub(r'<body(?![^>]*class=)([^>]*)>', r'<body class="fc-site"\1>', text, count=1)
    if '<body class="' in text and 'fc-site' not in re.search(r'<body[^>]*>', text).group(0):
        text = re.sub(r'<body class="([^"]*)"', lambda m: '<body class="' + (m.group(1) + ' fc-site').strip() + '"', text, count=1)
    return text


def standard_footer(text: str) -> str:
    text = re.sub(r'<footer(?![^>]*data-focuschrist-footer)([^>]*)>', r'<footer class="fc-footer" data-focuschrist-footer="standard"\1>', text, count=1)
    return text


def brand_case(text: str) -> str:
    # Public HTML copy should use the owner-directed brand casing.
    return text.replace('FocusChrist', 'focusChrist')


def migrate_ask(text: str) -> str:
    hero_pattern = re.compile(r'\s*<header class="ask-hero" data-focuschrist-ask-experience="true">.*?</header>', re.S)
    replacement = '''
    <div class="fc-visual-hero fc-visual-hero--christ" data-focuschrist-ask-experience="true" aria-label="Jesus Christ"></div>
    <section class="fc-page-intro" aria-labelledby="ask-page-title">
        <div class="fc-container--standard">
            <p class="fc-eyebrow">A place to seek and study</p>
            <h1 class="fc-display" id="ask-page-title">Ask. Seek. Study.</h1>
            <p class="fc-page-intro-copy">Bring a sincere question about Jesus Christ, scripture, or Latter-day Saint belief. Explore an answer, follow the sources, and continue studying.</p>
            <span class="fc-page-intro-scripture">“Ask, and it shall be given you; seek, and ye shall find.” — Matthew 7:7</span>
        </div>
    </section>'''
    text, count = hero_pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit('Ask hero migration failed')
    return text


def migrate_answers(text: str) -> str:
    pattern = re.compile(r'\s*<header class="answer-hero">.*?</header>', re.S)
    replacement = '''
    <div class="fc-visual-hero fc-visual-hero--christ" aria-label="Jesus Christ"></div>
    <section class="fc-page-intro" aria-labelledby="answers-page-title">
        <div class="fc-container--standard">
            <p class="fc-eyebrow">Study and seek</p>
            <h1 class="fc-display" id="answers-page-title">Answers About Jesus Christ and Latter-day Saint Beliefs</h1>
            <p class="fc-page-intro-copy">A deliberately small collection of original study pages for sincere questions about Jesus Christ, scripture, and the beliefs of The Church of Jesus Christ of Latter-day Saints.</p>
        </div>
    </section>'''
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit('Answers hero migration failed')
    text = re.sub(r'\s*<p class="lede">The focusChrist Answer Library.*?</p>', '', text, count=1, flags=re.S)
    return text


def migrate_art(text: str) -> str:
    pattern = re.compile(r'\s*<!-- Banner -->\s*<div class="banner">.*?</div>\s*</div>', re.S)
    replacement = '''
    <!-- Image-first page hero -->
    <div class="fc-visual-hero fc-visual-hero--christ" aria-label="Jesus Christ"></div>
    <section class="fc-page-intro" aria-labelledby="art-page-title">
        <div class="fc-container--standard">
            <p class="fc-eyebrow">Pause and remember Him</p>
            <h1 class="fc-display" id="art-page-title">Inspirational Art</h1>
            <p class="fc-page-intro-copy">A visual place to reflect on Jesus Christ, scripture, faith, hope, and the quiet moments that can turn the heart toward Him.</p>
        </div>
    </section>'''
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit('Art banner migration failed')
    return text


def migrate_about(text: str) -> str:
    pattern = re.compile(r'\s*<div class="banner">.*?</div>\s*</div>', re.S)
    replacement = '''
    <div class="fc-visual-hero fc-visual-hero--christ" aria-label="Jesus Christ"></div>
    <section class="fc-page-intro" aria-labelledby="about-page-title">
        <div class="fc-container--standard">
            <p class="fc-eyebrow">Why this site exists</p>
            <h1 class="fc-display" id="about-page-title">About focusChrist</h1>
            <p class="fc-page-intro-copy">focusChrist is an independent Christ-centered study resource created to help sincere visitors explore Jesus Christ, scripture, Latter-day Saint belief, faithful history, and trustworthy paths for continued study.</p>
        </div>
    </section>'''
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit('About banner migration failed')
    return text


def migrate_watch(text: str) -> str:
    pattern = re.compile(r'\s*<header class="answer-hero">.*?</header>', re.S)
    replacement = '''
    <div class="fc-visual-hero fc-visual-hero--christ" aria-label="Jesus Christ"></div>
    <section class="fc-page-intro" aria-labelledby="watch-page-title">
        <div class="fc-container--standard">
            <p class="fc-eyebrow">Watch and continue study</p>
            <h1 class="fc-display" id="watch-page-title">Continue from @theRisen636</h1>
            <p class="fc-page-intro-copy">Continue from a video, Short, scripture image, or devotional thought into the exact scripture, permanent Answer, Art &amp; Study, or Ask path that matches the subject.</p>
        </div>
    </section>'''
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit('Watch hero migration failed')
    text = re.sub(r'\s*<p class="lede">If a focusChrist video.*?</p>', '', text, count=1, flags=re.S)
    return text


def migrate_pioneers(text: str) -> str:
    pattern = re.compile(r'\s*<!-- Banner -->\s*<a class="banner".*?</a>', re.S)
    replacement = '''
 <!-- Image-first historical hero -->
 <a class="fc-visual-hero fc-visual-hero--history" href="pioneer%20art.png" target="_blank" rel="noopener noreferrer" aria-label="Open full pioneer artwork">
     <img src="working-banner.png" alt="Latter-day Saint pioneer journey artwork">
 </a>
 <section class="fc-page-intro" aria-labelledby="pioneer-page-title">
     <div class="fc-container--standard">
         <p class="fc-eyebrow">Faith across the journey</p>
         <h1 class="fc-display" id="pioneer-page-title">Pioneer Faith &amp; History</h1>
         <p class="fc-page-intro-copy">Explore the journeys, sacrifices, questions, and faith of Latter-day Saint pioneers, then follow the historical sources and continue the conversation.</p>
     </div>
 </section>'''
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit('Pioneer banner migration failed')
    text = text.replace('Ask any question about Mormon pioneers.', 'Ask a sincere question about Latter-day Saint pioneers and their history.')
    text = text.replace('>Clear</button>', '>New Question</button>')
    return text


def main():
    transforms = {
        'ask.html': migrate_ask,
        'answers.html': migrate_answers,
        'art.html': migrate_art,
        'pioneers.html': migrate_pioneers,
        'about.html': migrate_about,
        'watch.html': migrate_watch,
    }
    for filename in PRIMARY:
        path = ROOT / filename
        text = path.read_text(encoding='utf-8')
        text = brand_case(text)
        text = add_system(path, text)
        text = transforms[filename](text)
        text = standard_footer(text)
        path.write_text(text, encoding='utf-8')
        print('migrated', filename)

    css = ROOT / 'site-system.css'
    css_text = css.read_text(encoding='utf-8')
    css_text = css_text.replace('min-height: clamp(290px, 31vw, 390px);', 'min-height: clamp(260px, 22vw, 330px);')
    if '.fc-visual-hero > img' not in css_text:
        css_text = css_text.replace('.fc-visual-hero::before,\n.fc-visual-hero::after {', '''.fc-visual-hero > img {\n    position: absolute;\n    inset: 0;\n    width: 100%;\n    height: 100%;\n    object-fit: cover;\n    object-position: center center;\n    z-index: -2;\n}\n\n.fc-visual-hero::before,\n.fc-visual-hero::after {''')
        css_text = css_text.replace('position: relative;\n    min-height:', 'position: relative;\n    isolation: isolate;\n    min-height:', 1)
    css.write_text(css_text, encoding='utf-8')

    ask_css = ROOT / 'ask-experience.css'
    ask_text = ask_css.read_text(encoding='utf-8')
    ask_text += '''\n\n/* Unified site migration: page introduction now sits below an unobstructed hero image. */\nbody.fc-site .ask-main { margin-top: 0; padding-top: 22px; }\n'''
    ask_css.write_text(ask_text, encoding='utf-8')


if __name__ == '__main__':
    main()
