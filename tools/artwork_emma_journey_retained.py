"""Current Emma ownership plus explicitly historical retained-art evidence.

This validates source and unique ownership, not actual rendered review or
owner acceptance. The existing schema-2 receipt retains its historical scope;
new-journey delivery and the real owner release gate remain separate and held.
"""
from owner_integration_contract import Document, STORIES, assert_emma_semantics, validate_file
from artwork_emma_story_delivery import local, require
import owner_journey_successor as journey


def validate_current(root):
    """Check actual 138-route corpus, 20 owners and four story references."""
    sitemap=local(root,'sitemap.xml').read_bytes()
    routes=journey.validate_canonical(sitemap)
    hub=local(root,journey.HUB).read_bytes()
    journey.validate_hub(hub,root)
    journey.validate_redirect(local(root,journey.RETIRED).read_bytes())
    journey.validate_hymns(local(root,journey.HYMNS).read_bytes())
    expected=journey.OLD | journey.NEW | {journey.ORIGIN}
    found={key:[] for key in expected}
    for route in routes:
        raw=local(root,route).read_bytes()
        if route in STORIES and route != journey.RETIRED:
            validate_file(route,raw,root)
            assert_emma_semantics(route,raw.decode('utf-8'))
        for node in Document(raw.decode('utf-8')).root.walk():
            key=node.attrs.get('data-exclusive-artwork')
            if key in found:
                require(node.tag=='figure','unexpected current Emma owner element')
                found[key].append(route)
    require(all(paths==[journey.HUB] for paths in found.values()),
            'missing/duplicate current Emma journey ownership in canonical corpus')
    return routes


def validate(root, record, added, covered, rejected, pixel_hash, page_dependencies, historical_validate):
    validate_current(root)
    # Actual current validation precedes a deliberately named predecessor view.
    # Preserve only these exact prior sources, and never expose the prior pages as
    # a current route, figure census, rendered pass, or new approval.
    names=(journey.HUB,journey.RETIRED,journey.HYMNS)
    prior={route:journey.historical_fixture(route,local(root,route).read_bytes(),root) for route in names}
    from artwork_emma_hub_delivery import validate_explicit_historical
    return validate_explicit_historical(root,record,added,covered,rejected,pixel_hash,
                                        page_dependencies,historical_validate,prior)
