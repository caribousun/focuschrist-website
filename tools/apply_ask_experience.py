from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ASK = ROOT / "ask.html"
QA = ROOT / "tools/site_qa.py"

NEW_EXPERIENCE = r'''    <header class="ask-hero" data-focuschrist-ask-experience="true">
        <div class="ask-hero-content">
            <div class="ask-eyebrow">A place to seek and study</div>
            <h1>ASK. SEEK. STUDY.</h1>
            <p>Bring a sincere question about Jesus Christ, scripture, or Latter-day Saint belief. Explore an answer, follow the sources, and continue studying.</p>
            <span class="ask-scripture-line">“Ask, and it shall be given you; seek, and ye shall find.” — Matthew 7:7</span>
        </div>
    </header>

    <main class="ask-main">
        <section class="ask-study-card" aria-labelledby="ask-study-heading">
            <h2 class="ask-study-heading" id="ask-study-heading">What would you like to understand?</h2>
            <p class="ask-study-intro">Ask in your own words. Answers draw from scripture, established FocusChrist study material, and AI-assisted research where needed.</p>

            <div class="ask-input-area">
                <input type="text" id="userInput" placeholder="Ask a sincere question..." onkeypress="handleKeyPress(event)">
                <button class="ask-action" onclick="sendMessage()" id="sendBtn">Ask</button>
                <button class="ask-action secondary" onclick="clearChat()" id="clearBtn" title="Begin a new question">New Question</button>
            </div>

            <div class="ask-ai-notice" data-focuschrist-ai-notice="true">
                AI-assisted answers are study aids and may contain errors. For authoritative Church teaching, verify information through linked official Church sources. Please do not submit sensitive personal information.
            </div>

            <div class="ask-starters" data-focuschrist-starter-questions="true">
                <div class="ask-section-label">Start with a question</div>
                <div class="ask-starter-grid">
                    <button type="button" class="ask-starter" data-ask-starter data-question="Who is Jesus Christ, and why is He central to Latter-day Saint belief?">Who is Jesus Christ?</button>
                    <button type="button" class="ask-starter" data-ask-starter data-question="How can I recognize answers to prayer and personal revelation?">How can I recognize answers to prayer?</button>
                    <button type="button" class="ask-starter" data-ask-starter data-question="Why do Latter-day Saints build temples?">Why do Latter-day Saints build temples?</button>
                    <button type="button" class="ask-starter" data-ask-starter data-question="What do Latter-day Saints believe happens after death?">What happens after death?</button>
                    <button type="button" class="ask-starter" data-ask-starter data-question="How do the Bible and the Book of Mormon work together?">How do the Bible and Book of Mormon work together?</button>
                    <button type="button" class="ask-starter" data-ask-starter data-question="How can faith in Jesus Christ help during difficult times?">How can faith help during difficult times?</button>
                </div>
            </div>
        </section>

        <section class="ask-conversation-section" aria-labelledby="conversation-heading">
            <h2 class="ask-section-heading" id="conversation-heading">Your Study Conversation</h2>
            <p class="ask-section-copy">Follow the scripture and source links beneath an answer when they are available. Related permanent study pages may also appear after an answer.</p>
            <div class="chat-box ask-chat-box" id="chatBox" aria-live="polite">
                <div class="welcome ask-welcome">
                    <h3>Begin with a sincere question.</h3>
                    <p>You can type your own question above or choose one of the suggested questions. The purpose is to help you study more deeply and keep Jesus Christ at the center.</p>
                    <p class="welcome-sub">Scripture and official Church resources are linked whenever available.</p>
                </div>
            </div>
        </section>

        <section class="ask-topic-section" aria-labelledby="topic-heading" data-focuschrist-topic-explorer="true">
            <h2 class="ask-section-heading" id="topic-heading">Explore by Topic</h2>
            <p class="ask-section-copy">Open a study area to choose a more specific subject. These topics preserve the breadth of the original Ask page while making it easier to navigate.</p>
            <div class="ask-topic-grid">
                <article class="ask-topic-card">
                    <button type="button" class="ask-topic-toggle" aria-expanded="false">Scripture</button>
                    <div class="ask-topic-options">
                        <button class="ask-topic-option" data-ask-topic="Old Testament">Old Testament</button><button class="ask-topic-option" data-ask-topic="Genesis">Genesis</button><button class="ask-topic-option" data-ask-topic="Exodus">Exodus</button><button class="ask-topic-option" data-ask-topic="Psalms">Psalms</button><button class="ask-topic-option" data-ask-topic="Proverbs">Proverbs</button><button class="ask-topic-option" data-ask-topic="Isaiah">Isaiah</button><button class="ask-topic-option" data-ask-topic="New Testament">New Testament</button><button class="ask-topic-option" data-ask-topic="Matthew">Matthew</button><button class="ask-topic-option" data-ask-topic="Mark">Mark</button><button class="ask-topic-option" data-ask-topic="Luke">Luke</button><button class="ask-topic-option" data-ask-topic="John">John</button><button class="ask-topic-option" data-ask-topic="Romans">Romans</button><button class="ask-topic-option" data-ask-topic="Book of Mormon">Book of Mormon</button><button class="ask-topic-option" data-ask-topic="1 Nephi">1 Nephi</button><button class="ask-topic-option" data-ask-topic="2 Nephi">2 Nephi</button><button class="ask-topic-option" data-ask-topic="Alma">Alma</button><button class="ask-topic-option" data-ask-topic="Helaman">Helaman</button><button class="ask-topic-option" data-ask-topic="Moroni">Moroni</button><button class="ask-topic-option" data-ask-topic="Doctrine and Covenants">Doctrine &amp; Covenants</button><button class="ask-topic-option" data-ask-topic="Pearl of Great Price">Pearl of Great Price</button><button class="ask-topic-option" data-ask-topic="Bible Prophecy">Bible Prophecy</button>
                    </div>
                </article>
                <article class="ask-topic-card">
                    <button type="button" class="ask-topic-toggle" aria-expanded="false">Jesus Christ &amp; His Gospel</button>
                    <div class="ask-topic-options">
                        <button class="ask-topic-option" data-ask-topic="Jesus Christ">Jesus Christ</button><button class="ask-topic-option" data-ask-topic="Atonement">Atonement</button><button class="ask-topic-option" data-ask-topic="Baptism">Baptism</button><button class="ask-topic-option" data-ask-topic="Holy Ghost">Holy Ghost</button><button class="ask-topic-option" data-ask-topic="Resurrection">Resurrection</button><button class="ask-topic-option" data-ask-topic="Light of Christ">Light of Christ</button><button class="ask-topic-option" data-ask-topic="Son of Man">Son of Man</button><button class="ask-topic-option" data-ask-topic="Angels">Angels</button><button class="ask-topic-option" data-ask-topic="Spiritual Gifts">Spiritual Gifts</button><button class="ask-topic-option" data-ask-topic="Divine Nature">Divine Nature</button>
                    </div>
                </article>
                <article class="ask-topic-card">
                    <button type="button" class="ask-topic-toggle" aria-expanded="false">Prayer &amp; Revelation</button>
                    <div class="ask-topic-options">
                        <button class="ask-topic-option" data-ask-topic="Prayer">Prayer</button><button class="ask-topic-option" data-ask-topic="personal revelation vs secondhand testimony">Personal Revelation</button><button class="ask-topic-option" data-ask-topic="recognizing spirits whisperings">Recognizing the Spirit</button><button class="ask-topic-option" data-ask-topic="obedience unlocks revelation">Obedience &amp; Revelation</button><button class="ask-topic-option" data-ask-topic="Prophetic Revelation">Prophetic Revelation</button><button class="ask-topic-option" data-ask-topic="Prophets">Prophets</button><button class="ask-topic-option" data-ask-topic="holy ghost gift that stays">Gift of the Holy Ghost</button><button class="ask-topic-option" data-ask-topic="holy ghost guide to truth">Guide to Truth</button><button class="ask-topic-option" data-ask-topic="Let Your Light Shine">Let Your Light Shine</button>
                    </div>
                </article>
                <article class="ask-topic-card">
                    <button type="button" class="ask-topic-toggle" aria-expanded="false">Temples &amp; Covenants</button>
                    <div class="ask-topic-options">
                        <button class="ask-topic-option" data-ask-topic="Temples">Temples</button><button class="ask-topic-option" data-ask-topic="Temple Ordinances">Temple Ordinances</button><button class="ask-topic-option" data-ask-topic="Priesthood">Priesthood</button><button class="ask-topic-option" data-ask-topic="Priesthood Authority">Priesthood Authority</button><button class="ask-topic-option" data-ask-topic="Law of Chastity">Law of Chastity</button><button class="ask-topic-option" data-ask-topic="Spirit of Elijah">Spirit of Elijah</button>
                    </div>
                </article>
                <article class="ask-topic-card">
                    <button type="button" class="ask-topic-toggle" aria-expanded="false">Family &amp; Eternal Life</button>
                    <div class="ask-topic-options">
                        <button class="ask-topic-option" data-ask-topic="Plan of Salvation">Plan of Salvation</button><button class="ask-topic-option" data-ask-topic="Eternal Family">Eternal Family</button><button class="ask-topic-option" data-ask-topic="Resurrection">Resurrection</button><button class="ask-topic-option" data-ask-topic="Translation">Translation</button><button class="ask-topic-option" data-ask-topic="Divine Nature">Divine Nature</button>
                    </div>
                </article>
                <article class="ask-topic-card">
                    <button type="button" class="ask-topic-toggle" aria-expanded="false">Church History &amp; Restoration</button>
                    <div class="ask-topic-options">
                        <button class="ask-topic-option" data-ask-topic="Restoration">Restoration</button><button class="ask-topic-option" data-ask-topic="Joseph Smith">Joseph Smith</button><button class="ask-topic-option" data-ask-topic="First Vision">First Vision</button><button class="ask-topic-option" data-ask-topic="Prophets">Prophets</button><button class="ask-topic-option" data-ask-topic="Priesthood Authority">Priesthood Authority</button>
                    </div>
                </article>
            </div>
        </section>

        <section class="ask-continue-section" aria-labelledby="continue-heading" data-focuschrist-continue-study="true">
            <h2 class="ask-section-heading" id="continue-heading">Continue Your Study</h2>
            <p class="ask-section-copy">A question can be the beginning of a longer study path.</p>
            <div class="ask-continue-grid">
                <a class="ask-continue-card" href="answers.html"><strong>Answer Library</strong><span>Permanent, source-grounded explanations of common questions.</span></a>
                <a class="ask-continue-card" href="art.html"><strong>Inspirational Art</strong><span>Explore Christ-centered artwork and selected study paths.</span></a>
                <a class="ask-continue-card" href="watch.html"><strong>Watch &amp; Study</strong><span>Continue from video themes into deeper FocusChrist resources.</span></a>
                <a class="ask-continue-card" href="pioneers.html"><strong>Pioneers</strong><span>Explore faith, sacrifice, and Latter-day Saint history.</span></a>
                <a class="ask-continue-card" href="https://www.churchofjesuschrist.org/study?lang=eng" target="_blank" rel="noopener noreferrer"><strong>Official Church Study</strong><span>Continue in Gospel Library and official Church resources.</span></a>
            </div>
        </section>
    </main>
'''


def update_ask():
    text = ASK.read_text(encoding="utf-8")

    if '<link rel="stylesheet" href="ask-experience.css">' not in text:
        text = text.replace('<link rel="stylesheet" href="site-header.css">', '<link rel="stylesheet" href="site-header.css">\n    <link rel="stylesheet" href="ask-experience.css">', 1)
    if '<script src="ask-experience.js" defer></script>' not in text:
        text = text.replace('<script src="site-common.js" defer></script>', '<script src="site-common.js" defer></script>\n    <script src="ask-experience.js" defer></script>', 1)

    pattern = re.compile(r'\s*<div class="banner">.*?</section>\s*(?=<footer>)', re.S)
    text, count = pattern.subn('\n' + NEW_EXPERIENCE + '\n', text, count=1)
    if count != 1:
        raise SystemExit(f"Expected one legacy Ask experience block, replaced {count}")

    required = [
        'data-focuschrist-ask-experience="true"',
        'data-focuschrist-starter-questions="true"',
        'data-focuschrist-topic-explorer="true"',
        'data-focuschrist-continue-study="true"',
        'id="chatBox"',
        'id="userInput"',
        'id="sendBtn"',
        'id="clearBtn"',
    ]
    for marker in required:
        if text.count(marker) != 1:
            raise SystemExit(f"Ask marker missing/duplicated after migration: {marker}")

    ASK.write_text(text, encoding="utf-8")


def update_qa():
    text = QA.read_text(encoding="utf-8")
    anchor = '''    if ask.count('data-focuschrist-ai-notice="true"') != 1:\n        fail(errors, "Ask AI/privacy transparency notice missing/duplicated")\n'''
    addition = anchor + '''    for marker in (\n        'data-focuschrist-ask-experience="true"',\n        'data-focuschrist-starter-questions="true"',\n        'data-focuschrist-topic-explorer="true"',\n        'data-focuschrist-continue-study="true"',\n    ):\n        if ask.count(marker) != 1:\n            fail(errors, f"Ask redesigned experience marker missing/duplicated: {marker}")\n    if '<link rel="stylesheet" href="ask-experience.css">' not in ask:\n        fail(errors, "Ask experience stylesheet missing")\n    if '<script src="ask-experience.js" defer></script>' not in ask:\n        fail(errors, "Ask experience controller missing")\n    if ask.count('data-ask-starter') < 6:\n        fail(errors, "Ask starter question set unexpectedly incomplete")\n    if ask.count('class="ask-topic-card"') != 6:\n        fail(errors, "Ask topic explorer must contain exactly six study groups")\n    if ask.count('data-ask-topic=') < 40:\n        fail(errors, "Ask topic explorer unexpectedly lost topic breadth")\n    for asset in ("ask-experience.css", "ask-experience.js"):\n        asset_path = ROOT / asset\n        if not asset_path.exists() or asset_path.stat().st_size == 0:\n            fail(errors, f"Ask experience asset missing or empty: {asset}")\n    ask_js_path = ROOT / "ask-experience.js"\n    if ask_js_path.exists():\n        ask_js = ask_js_path.read_text(encoding="utf-8")\n        for js_marker in ("MutationObserver", "data-focuschrist-related-study", "initStarterQuestions", "initTopicCards"):\n            if js_marker not in ask_js:\n                fail(errors, f"Ask experience controller missing required behavior: {js_marker}")\n'''
    if 'Ask redesigned experience marker missing/duplicated' not in text:
        if anchor not in text:
            raise SystemExit("Ask QA anchor not found")
        text = text.replace(anchor, addition, 1)
    QA.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    update_ask()
    update_qa()
    print("FocusChrist Ask experience migration applied.")
