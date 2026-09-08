"""Protect scripture captions from mixed-content text reordering in source QA."""
from answer_study_qa import Document
doc=Document()
doc.feed('<main><p>Read <a href="source">Romans <em>12</em></a> with its setting.</p><article class="fc-resource-card"><p>Resource</p></article><p>Continue.</p></main>')
main=next(n for n in doc.root.walk() if n.tag=='main')
paragraph=next(n for n in main.walk() if n.tag=='p')
assert paragraph.text()=='Read Romans 12 with its setting.'
assert paragraph.words==['Read ',' with its setting.']
assert main.text(without_cards=True)=='Read Romans 12 with its setting.Continue.'
print('ANSWER STUDY PARSER QA PASS: inline scripture and nested emphasis preserve exact prose order')
