"""Exact owner-authorized preview removal; keep owning artwork and every other byte protected."""
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
RETIRED_SOURCE='/assets/page-art/jesus-journey/modern-scripture-960.webp'
ORIGINAL_REFERENCE='<article aria-label="Related illustrated study: Read His words together" class="fc-study-visual" data-linked-picture-reference="modern-scripture"><a aria-label="Open study: Read His words together" href="/answers/jesus-christ-latter-day-saint-beliefs.html#picture-modern-scripture"><img alt="An adult listens as a teenage girl speaks beside an open Bible at the kitchen table." decoding="async" height="640" loading="lazy" src="/assets/page-art/jesus-journey/modern-scripture-960.webp" width="960"/></a><div style="flex:1 1 280px;min-width:0"><h3>Read His words together</h3><p>An adult listens beside open scriptures. Bring your own questions to the Savior’s words.</p><p><a class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/nt/john/5?lang=eng&amp;id=p39#p39" rel="noopener noreferrer" target="_blank">John 5:39</a></p><a class="fc-button" href="/answers/jesus-christ-latter-day-saint-beliefs.html#picture-modern-scripture">Read “Read His words together” in Jesus Christ →</a></div></article>'
TEXT_REFERENCE='<article aria-label="Related study: Read His words together" class="fc-study-promotion" data-linked-study-reference="modern-scripture"><h3>Read His words together</h3><p>Bring your own questions to the Savior’s words. Explore a study of reading scripture together.</p><p><a class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/nt/john/5?lang=eng&amp;id=p39#p39" rel="noopener noreferrer" target="_blank">John 5:39</a></p><div class="fc-actions fc-actions--content"><a class="fc-button" href="/answers/jesus-christ-latter-day-saint-beliefs.html#picture-modern-scripture">Read “Read His words together” in Jesus Christ →</a></div></article>'
def check_text_reference(soup):
 refs=soup.select('[data-linked-study-reference="modern-scripture"]')
 assert len(refs)==1 and str(refs[0])==TEXT_REFERENCE,'Exact reviewed text-only scripture promotion required'
 assert not soup.select('img[src="'+RETIRED_SOURCE+'"]'),'Retired preview must not return'
 owner=BeautifulSoup((ROOT/'answers/jesus-christ-latter-day-saint-beliefs.html').read_text(encoding='utf-8'),'html.parser')
 assert owner.select_one('#picture-modern-scripture img[src="'+RETIRED_SOURCE+'"]'),'Original owner artwork must remain'
 return refs[0]
def normalize_reviewed_reference(section):
 ref=check_text_reference(section)
 ref.replace_with(BeautifulSoup(ORIGINAL_REFERENCE,'html.parser').article)
 return section
