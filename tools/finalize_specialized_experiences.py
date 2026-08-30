from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def wire_art():
    path = ROOT / 'art.html'
    text = path.read_text(encoding='utf-8')
    if 'art-experience.css' not in text:
        text = text.replace('<link rel="stylesheet" href="site-system.css">', '<link rel="stylesheet" href="site-system.css">\n    <link rel="stylesheet" href="art-experience.css">', 1)
    path.write_text(text, encoding='utf-8')


def wire_pioneers():
    path = ROOT / 'pioneers.html'
    text = path.read_text(encoding='utf-8')
    if 'pioneer-experience.css' not in text:
        text = text.replace('<link rel="stylesheet" href="site-system.css">', '<link rel="stylesheet" href="site-system.css">\n    <link rel="stylesheet" href="pioneer-experience.css">', 1)

    # Preserve visible conversation when Tell My Story finds a match.
    multi_old = """                // Show selection menu to user\n                document.getElementById('chatBox').innerHTML = '';\n                addMessage(query, true);\n                addMessage(storyMatch[0].story, false, [{text:'📖 Tell My Story Too', url:'tell-my-story-too.txt'}]);\n                // Store choices for selection\n                window.storyChoices = storyMatch[0].choices;\n                return { answer: storyMatch[0].story, sources: [] };"""
    multi_new = """                // Show selection menu without erasing earlier conversation.\n                addMessage(storyMatch[0].story, false, [{text:'Tell My Story Too', url:'tell-my-story-too.txt'}]);\n                window.storyChoices = storyMatch[0].choices;\n                return { answer: storyMatch[0].story, sources: [], alreadyDisplayed: true };"""
    text = text.replace(multi_old, multi_new)

    full_old = """                    document.getElementById('chatBox').innerHTML = '';\n                    addMessage(query, true);\n                    // Use fullStory if available, otherwise truncated version"""
    full_new = """                    // Keep prior conversation visible.\n                    // Use fullStory if available, otherwise truncated version"""
    text = text.replace(full_old, full_new)

    text = text.replace("        document.getElementById('chatBox').innerHTML = '';\n        addMessage(\"Tell My Story\", true);", "        addMessage(\"Tell My Story\", true);")

    # Normalize visible terminology and remove malformed historical leftovers.
    text = text.replace('You are a helpful assistant for the focusChrist website about Mormon pioneers.', 'You are a helpful assistant for the focusChrist website about Latter-day Saint pioneers.')
    text = text.replace('</script></script>', '</script>')
    text = text.replace(' <!-- Hero -->\n\n <!-- Hero removed -->\n>\n', '')

    if 'pioneer-experience.js' not in text:
        text = text.replace('</body>', '    <script src="pioneer-experience.js" defer></script>\n</body>', 1)
    path.write_text(text, encoding='utf-8')


def main():
    wire_art()
    wire_pioneers()
    print('wired Art and Pioneer unified experiences after source-transparency QA correction')


if __name__ == '__main__':
    main()
