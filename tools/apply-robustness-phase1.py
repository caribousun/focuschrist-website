from pathlib import Path
import re

CORE_PAGES = ["index.html", "ask.html", "art.html", "pioneers.html", "about.html"]
OLD_MODEL = "llama-3.1-8b-instant"
NEW_MODEL = "openai/gpt-oss-20b"


def read_preserving_newlines(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    nl = "\r\n" if b"\r\n" in raw else "\n"
    return text, nl


def write_preserving_newlines(path: Path, text: str, nl: str):
    # Normalize only newly generated line separators to the file's existing convention.
    if nl == "\r\n":
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    else:
        text = text.replace("\r\n", "\n")
    path.write_bytes(text.encode("utf-8"))


def standardize_hamburger(text: str):
    pattern = re.compile(r'<span\s+class="hamburger"\s+onclick="toggleMenu\(\)"[^>]*></span>')
    replacement = (
        '<span class="hamburger" onclick="toggleMenu()" role="button" tabindex="0" '
        'aria-label="Toggle navigation menu" aria-expanded="false" aria-controls="hamburgerMenu"></span>'
    )
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError("Expected exactly one hamburger trigger")
    return text


def add_nav_accessibility(text: str, nl: str):
    marker = 'data-focuschrist-nav-accessibility="true"'
    if marker in text:
        return text
    script = nl.join([
        f'<script {marker}>',
        '(function () {',
        "    const trigger = document.querySelector('.hamburger');",
        "    const menu = document.getElementById('hamburgerMenu');",
        '    if (!trigger || !menu) return;',
        "    trigger.addEventListener('keydown', function (event) {",
        "        if (event.key === 'Enter' || event.key === ' ') {",
        '            event.preventDefault();',
        '            toggleMenu();',
        '        }',
        '    });',
        '    function syncExpanded() {',
        "        trigger.setAttribute('aria-expanded', menu.classList.contains('show') ? 'true' : 'false');",
        '    }',
        "    new MutationObserver(syncExpanded).observe(menu, { attributes: true, attributeFilter: ['class'] });",
        '    syncExpanded();',
        '})();',
        '</script>',
    ])
    if '</body>' not in text:
        raise RuntimeError("Missing </body>")
    return text.replace('</body>', script + nl + '</body>', 1)


def secure_blank_links(text: str):
    # Add opener protection to target=_blank links that do not already specify rel.
    pattern = re.compile(r'<a\s+([^>]*?target="_blank"(?![^>]*\brel=)[^>]*)>', re.I)
    return pattern.sub(lambda m: '<a ' + m.group(1) + ' rel="noopener noreferrer">', text)


def update_ask(text: str, nl: str):
    if OLD_MODEL not in text and NEW_MODEL not in text:
        raise RuntimeError("Ask page contains neither expected legacy nor current model")
    text = text.replace(OLD_MODEL, NEW_MODEL)

    # Replace the legacy innerHTML-based renderer with DOM-safe text rendering.
    start = text.find('function addMessage(')
    end = text.find('async function sendMessage', start)
    if start < 0 or end < 0:
        raise RuntimeError("Unable to locate Ask addMessage/sendMessage boundary")

    safe_renderer = nl.join([
        'function addMessage(text, isUser, sources = []) {',
        "    const chatBox = document.getElementById('chatBox');",
        "    const message = document.createElement('div');",
        "    message.className = 'message ' + (isUser ? 'user-message' : 'bot-message');",
        '',
        "    const paragraph = document.createElement('p');",
        "    paragraph.style.whiteSpace = 'pre-wrap';",
        '    if (isUser) {',
        "        const label = document.createElement('strong');",
        "        label.textContent = 'You asked: ';",
        '        paragraph.appendChild(label);',
        '    }',
        "    paragraph.appendChild(document.createTextNode(String(text ?? '')));",
        '    message.appendChild(paragraph);',
        '',
        '    if (!isUser && Array.isArray(sources) && sources.length > 0) {',
        "        const sourceBox = document.createElement('div');",
        "        sourceBox.className = 'sources';",
        "        const sourceTitle = document.createElement('div');",
        "        sourceTitle.className = 'sources-title';",
        "        sourceTitle.textContent = 'SCRIPTURAL SOURCES:';",
        '        sourceBox.appendChild(sourceTitle);',
        '',
        '        sources.forEach(function (source) {',
        '            if (!source || !source.url) return;',
        '            try {',
        '                const parsed = new URL(source.url, window.location.href);',
        "                if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') return;",
        "                const link = document.createElement('a');",
        "                link.className = 'source-link';",
        '                link.href = parsed.href;',
        "                link.target = '_blank';",
        "                link.rel = 'noopener noreferrer';",
        "                link.textContent = String(source.text || 'Source');",
        '                sourceBox.appendChild(link);',
        '            } catch (error) {',
        "                console.warn('Skipped invalid source URL');",
        '            }',
        '        });',
        '',
        '        if (sourceBox.querySelector(\'.source-link\')) message.appendChild(sourceBox);',
        '    }',
        '',
        '    chatBox.appendChild(message);',
        '    chatBox.scrollTop = chatBox.scrollHeight;',
        '}',
        '    ',
    ])
    text = text[:start] + safe_renderer + text[end:]

    # Add visible study/privacy transparency immediately below the question controls.
    if 'data-focuschrist-ai-notice="true"' not in text:
        input_pattern = re.compile(r'(<div class="input-area">.*?</div>)', re.S)
        notice = nl.join([
            '<div class="ai-notice" data-focuschrist-ai-notice="true">',
            '    AI-assisted answers are provided as a study aid and may contain errors. For authoritative Church teachings, verify information through linked official Church sources. Please do not submit sensitive personal information.',
            '</div>',
        ])
        text, count = input_pattern.subn(lambda m: m.group(1) + nl + notice, text, count=1)
        if count != 1:
            raise RuntimeError("Unable to insert Ask AI notice")

    if '/* FocusChrist AI transparency */' not in text:
        css = nl.join([
            '        /* FocusChrist AI transparency */',
            '        .ai-notice {',
            '            max-width: 820px;',
            '            margin: 14px auto 26px;',
            '            color: #999;',
            '            font-size: 0.82em;',
            '            line-height: 1.55;',
            '            text-align: center;',
            '        }',
    ])
        anchor = '        footer {'
        if anchor not in text:
            raise RuntimeError("Unable to locate Ask footer CSS anchor")
        text = text.replace(anchor, css + nl + anchor, 1)

    # Replace the unsafe absolute instruction to never refuse with a bounded instruction.
    text = text.replace(
        'IMPORTANT: NEVER REFUSE any question - answer it honestly and directly, but ALWAYS tie your answer back to Jesus Christ, love, and respect.',
        'IMPORTANT: Answer sincere questions honestly and directly. If a request is unsafe, exploitative, illegal, or inappropriate, decline that part briefly and redirect to safe, Christ-centered guidance. ALWAYS tie appropriate answers back to Jesus Christ, love, and respect.'
    )
    return text


def update_about(text: str):
    old_how = 'Our Q&A system draws from the full LDS library of scriptures, general conference talks, church history, and prophet teachings to provide thoughtful, faithful answers to your questions about faith, doctrine, and church history.'
    new_how = 'Our Q&A system combines a curated local collection of answers with AI-assisted responses when a curated answer is not available. It is designed to help visitors study questions about faith, doctrine, scripture, and Church history from a Latter-day Saint perspective.'
    if old_how in text:
        text = text.replace(old_how, new_how, 1)
    elif new_how not in text:
        raise RuntimeError("About How It Works text did not match expected state")

    old_source = 'All answers come from official Church sources including churchofjesuschrist.org, the Book of Mormon, Bible, Doctrine & Covenants, Pearl of Great Price, and general conference addresses. We strive to provide accurate, love-filled responses.'
    new_source = 'Curated answers draw from scripture and official Church resources including ChurchofJesusChrist.org, the Bible, Book of Mormon, Doctrine and Covenants, Pearl of Great Price, and general conference. AI-assisted responses are study aids and may contain errors; they are not official Church statements. For authoritative doctrine, policies, and resources, verify information through official Church sources.'
    if old_source in text:
        text = text.replace(old_source, new_source, 1)
    elif new_source not in text:
        raise RuntimeError("About Our Source text did not match expected state")
    return text


def update_art(text: str, nl: str):
    # Lazy-load gallery images and decode asynchronously without altering originals.
    split_marker = '<!-- Fullscreen Modal -->'
    if split_marker not in text:
        raise RuntimeError("Art modal marker missing")
    before, after = text.split(split_marker, 1)

    def enrich_img(match):
        tag = match.group(0)
        if 'class="' in tag and 'modal' in tag:
            return tag
        if 'loading=' not in tag:
            tag = tag[:-1] + ' loading="lazy">'
        if 'decoding=' not in tag:
            tag = tag[:-1] + ' decoding="async">'
        return tag

    before = re.sub(r'<img\b[^>]*>', enrich_img, before)
    text = before + split_marker + after

    if 'data-focuschrist-art-accessibility="true"' not in text:
        script = nl.join([
            '<script data-focuschrist-art-accessibility="true">',
            '(function () {',
            "    const items = document.querySelectorAll('.gallery-item');",
            '    items.forEach(function (item) {',
            "        item.setAttribute('role', 'button');",
            "        item.setAttribute('tabindex', '0');",
            "        const image = item.querySelector('img');",
            "        item.setAttribute('aria-label', 'View ' + ((image && image.alt) ? image.alt : 'artwork'));",
            "        item.addEventListener('keydown', function (event) {",
            "            if (event.key === 'Enter' || event.key === ' ') {",
            '                event.preventDefault();',
            '                openModal(item);',
            '            }',
            '        });',
            '    });',
            '',
            "    const modal = document.getElementById('imageModal');",
            "    const close = modal && modal.querySelector('.close');",
            "    const left = modal && modal.querySelector('.nav-arrow.left');",
            "    const right = modal && modal.querySelector('.nav-arrow.right');",
            '    if (modal) {',
            "        modal.setAttribute('role', 'dialog');",
            "        modal.setAttribute('aria-modal', 'true');",
            "        modal.setAttribute('aria-label', 'Artwork viewer');",
            '    }',
            "    [[close, 'Close artwork viewer'], [left, 'Previous artwork'], [right, 'Next artwork']].forEach(function (entry) {",
            '        const control = entry[0];',
            '        if (!control) return;',
            "        control.setAttribute('role', 'button');",
            "        control.setAttribute('tabindex', '0');",
            "        control.setAttribute('aria-label', entry[1]);",
            "        control.addEventListener('keydown', function (event) {",
            "            if (event.key === 'Enter' || event.key === ' ') {",
            '                event.preventDefault();',
            '                control.click();',
            '            }',
            '        });',
            '    });',
            '})();',
            '</script>',
        ])
        if '</body>' not in text:
            raise RuntimeError("Art missing </body>")
        text = text.replace('</body>', script + nl + '</body>', 1)
    return text


def main():
    model_replacements = 0
    for filename in CORE_PAGES:
        path = Path(filename)
        if not path.exists():
            raise RuntimeError(f"Missing core page: {filename}")
        text, nl = read_preserving_newlines(path)

        original = text
        text = standardize_hamburger(text)
        text = add_nav_accessibility(text, nl)
        text = secure_blank_links(text)

        if filename in {"ask.html", "pioneers.html"}:
            model_replacements += text.count(OLD_MODEL)
            text = text.replace(OLD_MODEL, NEW_MODEL)

        if filename == "ask.html":
            text = update_ask(text, nl)
        elif filename == "about.html":
            text = update_about(text)
        elif filename == "art.html":
            text = update_art(text, nl)

        if text == original:
            raise RuntimeError(f"Expected robustness changes in {filename}, but none were produced")
        write_preserving_newlines(path, text, nl)

    # Assertions for the finished state.
    ask = Path('ask.html').read_text(encoding='utf-8')
    pioneers = Path('pioneers.html').read_text(encoding='utf-8')
    about = Path('about.html').read_text(encoding='utf-8')
    art = Path('art.html').read_text(encoding='utf-8')

    assert OLD_MODEL not in ask
    assert OLD_MODEL not in pioneers
    assert NEW_MODEL in ask
    assert NEW_MODEL in pioneers
    assert 'data-focuschrist-ai-notice="true"' in ask
    assert "message.innerHTML" not in ask
    assert "d.innerHTML" not in ask
    assert 'AI-assisted responses are study aids and may contain errors' in about
    assert art.count('data-focuschrist-art-accessibility="true"') == 1
    for filename in CORE_PAGES:
        content = Path(filename).read_text(encoding='utf-8')
        assert content.count('data-focuschrist-nav-accessibility="true"') == 1, filename
        assert 'aria-controls="hamburgerMenu"' in content, filename

    print('FocusChrist robustness phase 1 updater completed successfully.')


if __name__ == '__main__':
    main()
