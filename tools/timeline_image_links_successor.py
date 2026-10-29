"""Exact timeline-link changes, reversible for historical review only."""
import hashlib

BEFORE='2b0601379d8f5416f4fc8353820c0e1e3c54cc80661cab5dd2f29b1b2fa55e2f'
AFTER='4bbc34438e1e10e4507d10f690572aeb75228105aa5912ed71aeb3e6249ab27b'
CHANGES=(
 ('/birth-of-christ.html#wise-men-and-egypt','/answers/jesus-christ-latter-day-saint-beliefs.html#nazareth-childhood'),
 ('/art.html#art-gallery','/art-gallery.html?picture=art-4f5759d8edad'),
 ('/ask.html#topic-heading','/art-gallery.html?picture=art-3b1016debbad'),
 ('/art.html#art-gallery','/art-gallery.html?picture=art-838305f993f7'),
 ('/church-history.html','/art-gallery.html?picture=art-6e45c602be15'),
 ('/art.html#art-gallery','/art-gallery.html?picture=art-d12945c2d847'),
)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def restore(raw):
 assert sha(raw)==AFTER, 'Unreviewed timeline image-link source'
 for before,after in CHANGES:
  old=('"href": "'+before+'"').encode();new=('"href": "'+after+'"').encode()
  assert raw.count(new)==1,'Timeline image-link context changed'
  raw=raw.replace(new,old,1)
 assert sha(raw)==BEFORE,'Timeline image-link predecessor mismatch'
 return raw
