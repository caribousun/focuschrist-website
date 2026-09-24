"""Render the four verified public Shorts after the channel publication check."""
import argparse
import datetime
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- WATCH SHORTS START -->'
END = '<!-- WATCH SHORTS END -->'

def render(data):
    assert data['channel'] == 'https://www.youtube.com/@theRisen636/shorts'
    datetime.date.fromisoformat(data['verified_at'])
    records = data['shorts']
    assert len(records) == 4 and len({s['id'] for s in records}) == 4, 'Exactly four distinct published Shorts required'
    esc = html.escape
    cards = []
    for s in records:
        assert re.fullmatch(r'[A-Za-z0-9_-]{11}', s['id']), 'Invalid video identity'
        u = urlsplit(s['thumbnail'])
        assert u.scheme == 'https' and u.netloc == 'i.ytimg.com' and u.path.startswith('/vi/' + s['id'] + '/'), 'Thumbnail must belong to this YouTube video'
        assert all(isinstance(s[k], str) and s[k].strip() for k in ('title', 'speaker', 'description'))
        url = 'https://www.youtube.com/shorts/' + s['id']
        cards.append(f'''<article class="watch-short" data-short-id="{s['id']}">
<div class="watch-short-media"><a class="watch-short-preview" data-short-play="{s['id']}" href="{url}" aria-label="Watch {esc(s['title'])}" target="_blank" rel="noopener noreferrer"><img src="{esc(s['thumbnail'])}" width="405" height="720" alt="{esc(s['title'])} — YouTube Short preview" loading="lazy" decoding="async"></a></div>
<div class="watch-short-copy"><a class="watch-short-open" data-short-play="{s['id']}" href="{url}" aria-label="Play {esc(s['title'])}" target="_blank" rel="noopener noreferrer">▶ Watch Short</a><p class="watch-short-speaker">{esc(s['speaker'])}</p><h3>{esc(s['title'])}</h3><p>{esc(s['description'])}</p><a href="{url}" target="_blank" rel="noopener noreferrer">Open on YouTube →</a></div>
</article>''')
    date = datetime.date.fromisoformat(data['verified_at'])
    date_text = f'{date.day} {date:%B %Y}'
    return f'''{START}
<section class="watch-shorts fc-container--standard" id="latest-shorts" data-watch-shorts aria-labelledby="latest-shorts-title">
<p class="fc-eyebrow">A moment to turn toward Him</p>
<h2 class="fc-section-heading" id="latest-shorts-title">Latest from Focus Shorts</h2>
<p class="fc-section-intro">Four recent messages from our YouTube channel. Take a moment to listen, and carry a thought about the Savior into your day.</p>
<div class="watch-shorts-layout"><div class="watch-shorts-grid">{cards[0]}</div>
<details class="watch-shorts-more" data-shorts-more><summary class="fc-button"><span data-shorts-toggle-label>Show 3 more Shorts</span></summary><div class="watch-shorts-grid">
{''.join(cards[1:])}</div><button class="fc-button watch-shorts-collapse" type="button" data-shorts-collapse>Hide 3 Shorts</button></details></div>
<div class="fc-actions fc-actions--center"><a class="fc-button fc-button--primary" href="{data['channel']}" target="_blank" rel="noopener noreferrer">Watch all our Shorts on YouTube →</a></div>
<p class="watch-shorts-updated">Latest four checked <time datetime="{data['verified_at']}">{date_text}</time> · @theRisen636</p>
</section>
{END}'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    content = render(json.loads((ROOT / 'docs/watch-shorts.json').read_text(encoding='utf-8')))
    page = ROOT / 'watch.html'
    old = page.read_text(encoding='utf-8')
    if START in old:
        assert old.count(START) == old.count(END) == 1
        new = old[:old.index(START)] + content + old[old.index(END) + len(END):]
    else:
        assert old.count('<main>') == 1
        new = old.replace('<main>', '<main>\n' + content, 1)
    if args.check:
        if new != old:
            raise SystemExit('Watch Shorts markup is stale; run tools/build_watch_shorts.py')
        print('Watch Shorts markup matches the four verified records.')
    else:
        page.write_text(new, encoding='utf-8', newline='\n')
        print('Updated four Watch Shorts cards.')

if __name__ == '__main__':
    main()
