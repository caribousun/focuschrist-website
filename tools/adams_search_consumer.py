"""Exact existing standalone is indexed, but is not a shared-search consumer."""
from adams_standalone_opening import ADAMS_ROUTE, assert_adams_opening


def is_adams_standalone_search_owner(path, source, indexed_pages):
    # Every other route keeps the ordinary shared-header search assertions.
    if path != '/' + ADAMS_ROUTE:
        return False
    assert_adams_opening(ADAMS_ROUTE, source)
    assert len(indexed_pages) == len(set(indexed_pages)) == 137, 'Exact current indexed-page inventory'
    assert indexed_pages.count(path) == 1, 'Adams must remain indexed exactly once'
    assert {'/index.html', '/timeline.html'} <= set(indexed_pages), 'Both real shared-header continuations remain indexed'
    text = source.decode('utf-8')
    assert all(token not in text for token in ('data-site-search-trigger', 'site-search.js', 'site-search.css')), 'Exact standalone is not a shared-search consumer'
    return True
