"""Exact owner-directed links/questions; existing answer behavior remains unchanged."""
from pathlib import Path
import json
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
s=BeautifulSoup((ROOT/'church-history.html').read_text(encoding='utf-8'),'html.parser');d=json.loads((ROOT/'docs/reviews/2026-09-27-mobile-history-choices.json').read_text(encoding='utf-8'))
links=[[a['href'],a.get_text()] for a in s.select('.fc-history-topic-links a')];questions=[[a['data-history-question'],a.get_text()] for a in s.select('[data-history-question]')]
assert links==d['final_links'] and len(links)==16 and len({x[0] for x in links})==16
assert questions==d['final_questions'] and len(questions)==13 and len({x[0] for x in questions})==13
assert all(x in links for x in d['original_links']) and all(x in questions for x in d['original_questions'])
assert all(s.find(id=url[1:]) for url,label in links),'Every topic opens an existing real section'
assert all(b.get('type')=='button' for b in s.select('[data-history-question]'))
print('History choices PASS:16 distinct existing destinations,13 real questions, all original13links/10questions preserved')
