"""Exact new Nazareth section; restoring it is a historical projection only."""
import hashlib

BEFORE = '576c203f13bf3753fd511b78abe5891ae66e3966dd92ec0966beeaebe96908f9'
AFTER = 'a07b2055489fed927f90ba5ed6ebde5900d46f4c6fe9c58fc7bbbf305ef4c901'
MARKER = b'<h2>He Leads His Church and Will Return</h2>'
SECTION = ('<section class="fc-deep-study" id="nazareth-childhood"><h2>Growing up in Nazareth</h2>'
           '<p>Luke records that Mary and Joseph returned with Jesus to Nazareth. There He grew strong, '
           'was filled with wisdom, and the grace of God was upon Him.</p><p><a href="https://www.churchofjesuschrist.org/study/scriptures/nt/luke/2?lang=eng&amp;id=p39-p40#p39" '
           'target="_blank" rel="noopener noreferrer">Read Luke 2:39–40</a></p><p><a href="/assets/page-art/birth-of-christ/23-nazareth-return-800.webp" '
           'data-full-image-viewer data-full-image-alt="Joseph carries the young Jesus beside Mary at a village doorway.">'
           'View the family in Nazareth</a></p></section>').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def restore(raw):
    assert sha(raw) == AFTER, 'Unreviewed Nazareth successor source'
    assert raw.count(SECTION + MARKER) == 1, 'Nazareth successor context changed'
    previous = raw.replace(SECTION + MARKER, MARKER, 1)
    assert sha(previous) == BEFORE, 'Nazareth predecessor mismatch'
    return previous


def advance(raw):
    assert sha(raw) == BEFORE, 'Unreviewed Nazareth predecessor'
    assert raw.count(MARKER) == 1
    current = raw.replace(MARKER, SECTION + MARKER, 1)
    assert sha(current) == AFTER, 'Nazareth successor mismatch'
    return current
