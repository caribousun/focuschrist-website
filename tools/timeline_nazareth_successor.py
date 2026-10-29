"""Exact new Nazareth section; restoring it is a historical projection only."""
import hashlib

BEFORE = '576c203f13bf3753fd511b78abe5891ae66e3966dd92ec0966beeaebe96908f9'
AFTER = 'dd071c356cb85d33bea1b717447446a2ab9f7f49d2fcb8e4eb4e458b3a7d6078'
MARKER = b'<h2>He Leads His Church and Will Return</h2>'
SECTION = ('<section class="fc-deep-study" id="nazareth-childhood"><h2>Growing up in Nazareth</h2>'
           '<p>Luke records that Mary and Joseph returned with Jesus to Nazareth. There He grew strong, '
           'was filled with wisdom, and the grace of God was upon Him.</p><p><a href="https://www.churchofjesuschrist.org/study/scriptures/nt/luke/2?lang=eng&amp;id=p39-p40#p39" '
           'target="_blank" rel="noopener noreferrer">Read Luke 2:39–40</a></p></section>').encode()


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
