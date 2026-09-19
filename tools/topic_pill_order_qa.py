"""Keep unordered topic selectors alphabetical in source and keyboard order."""
from pathlib import Path
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
CLASSES = {'fc-answers-jump-links', 'fc-history-topic-links', 'pioneer-topic-grid',
           'ask-topic-options', 'watch-theme-tabs'}


def check():
    errors, groups = [], 0
    for path in ROOT.rglob('*.html'):
        if set(path.relative_to(ROOT).parts) & {'docs', 'tools', '.git', 'node_modules'}:
            continue
        doc = Document()
        doc.feed(path.read_text(encoding='utf-8'))
        for node in doc.root.walk():
            if not CLASSES.intersection(node.attrs.get('class', '').split()):
                continue
            groups += 1
            labels = [' '.join(child.text().split()) for child in node.children
                      if child.tag in {'a', 'button'}
                      and child.attrs.get('onclick') != 'askTellMyStory()']
            if labels != sorted(labels, key=str.casefold):
                errors.append(f'{path.relative_to(ROOT)}: topic pills must be alphabetical: {labels}')
    assert groups >= 10, f'Expected topic directories were lost: found {groups}'
    assert not errors, '\n'.join(errors)
    print(f'TOPIC PILL ORDER PASS: {groups} topic groups')


if __name__ == '__main__':
    check()
