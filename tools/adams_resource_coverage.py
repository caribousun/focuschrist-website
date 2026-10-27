"""One exact empty-card owner; preserve all existing resource registrations."""
import hashlib
import json
from html.parser import HTMLParser

ADAMS_ROUTE = 'timelines/adams-1881-chart.html'
PAGE_SHA = '95802a989d818d0ff7297660274c62f18140950b0bf58fc96a90277ef1e1cb90'
PREDECESSOR_SHA = '41e8c241f18b942db2c0f8f566e2e833261128a358b4bd600e7d373ea81fd393'


class Cards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.keys = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and 'data-resource-key' in attrs:
            self.keys.append(attrs['data-resource-key'])


def without_adams_resource_owner(coverage, routes, source):
    assert isinstance(source, bytes)
    assert len(source) == 62030 and hashlib.sha256(source).hexdigest() == PAGE_SHA, 'Exact V9 resource owner changed'
    assert len(routes) == len(set(routes)) == 138, 'Exact current route count and uniqueness'
    assert routes.count(ADAMS_ROUTE) == 1 and set(coverage) == set(routes), 'Missing or unexpected coverage owner'
    assert coverage[ADAMS_ROUTE] == [], 'Adams resource registration must match actual zero cards'
    parser = Cards(); parser.feed(source.decode('utf-8'))
    assert parser.keys == coverage[ADAMS_ROUTE], 'Actual Adams cards differ'
    old = {key: value for key, value in coverage.items() if key != ADAMS_ROUTE}
    assert len(old) == 137
    assert hashlib.sha256(json.dumps(old, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == PREDECESSOR_SHA, 'Existing 137 mappings changed'
    return old, [route for route in routes if route != ADAMS_ROUTE]
