"""Strict FOUR featured Art-route evidence/count acceptance; not whole-site QA.

Exit 1 for deficient OR unverified evidence. Existing preservation regression
remains separate. Passing numeric evidence cannot certify pixels/source truth,
native behavior, or owner aesthetic acceptance. No threshold/waiver switches.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote

PAGES = frozenset('art-study/' + name + '.html' for name in (
    'the-living-christ', 'the-good-shepherd', 'suffer-the-little-children', 'be-still'))
MINIMUM = 10


# Exact compatibility for the four independently reviewed shared-CSS URL changes.
# Asset, coverage, ownership and source-review hashes remain strict below.
REVIEWED_PAGE_HASHES = {'art-study/be-still.html': 'ed90acad612bc12e0008d498a37f3f8d2a9b27e068212bec475555ee5a723423', 'art-study/suffer-the-little-children.html': '4d2dfed3b3443118c8908736b3048a410b2e80217509e42465ee8894a7ca10d2', 'art-study/the-good-shepherd.html': '5fe506ab086c140fef457e9f53f3b3cc5a54ee0711885e4a72144a4cd689cf55', 'art-study/the-living-christ.html': '1c1c6310ec7469244b87d4cdc7c79086a93c945b237346d2341132532a05c83b'}
OLD_SHARED_STYLE = b'<link rel="stylesheet" href="../site-system.css?v=20260930-study-alignment-1">'
CURRENT_SHARED_STYLE = b'<link rel="stylesheet" href="../site-system.css?v=20261005-mobile-study-rows-1">'
OLD_COMMON_SCRIPT = b'site-common.js?v=20261002-timeline-1'
CURRENT_COMMON_SCRIPT = b'site-common.js?v=20261006-balanced-opening-1'
OLD_ANSWER_STYLE = b'answer-styles.css?v=20260909-warm'
CURRENT_ANSWER_STYLE = b'answer-styles.css?v=20261005-centered-pill-labels-1'
BUFFER_ANSWER_STYLE = b'answer-styles.css?v=20261006-art-study-buffer-2'
CONTAINED_ANSWER_STYLE = b'answer-styles.css?v=20261006-art-study-nav-width-1'
OLD_ART_STYLE = b'art-study-enrichment.css?v=20260927-anchor-alignment-1'
PREVIOUS_ART_STYLE = b'art-study-enrichment.css?v=20261006-static-study-nav-1'
CURRENT_ART_STYLE = b'art-study-enrichment.css?v=20261006-caption-prose-gap-1'
OLD_HERO_SCRIPT = b'hero-details.js?v=20260927-plan-study-1'
CURRENT_HERO_SCRIPT = b'hero-details.js?v=20261006-visible-art-1'
VISIBLE_IMAGE_HELPER = b'<script src="../hero-image-source.js?v=20261006-visible-art-1" defer></script>\n'
VIEWER_TOKEN_INVERSES = (
    (b'full-image-viewer.js?v=20261006-versions-1', b'full-image-viewer.js?v=20260914-reopen-1'),
    (b'full-image-viewer.css?v=20261006-versions-1', b'full-image-viewer.css?v=20260905-viewport'),
)
VISIBLE_ART_ROUTES = frozenset({
    'art-study/be-still.html',
    'art-study/suffer-the-little-children.html',
    'art-study/the-good-shepherd.html',
})


def reviewed_page_binding(page, route, expected):
    raw = page.read_bytes()
    if hashlib.sha256(raw).hexdigest() == expected:
        return True
    if expected != REVIEWED_PAGE_HASHES.get(route):
        return False
    inverse = raw
    topic_current = b'topic-artwork-details.js?v=20261007-scoped-root-1'
    if inverse.count(topic_current) != 1:
        return False
    inverse = inverse.replace(topic_current, b'topic-artwork-details.js?v=20261004-study-return-1', 1)
    current_viewer = b'full-image-viewer.css?v=20261007-viewer-controls-1'
    if inverse.count(current_viewer) != 1:
        return False
    previous_viewer = b'full-image-viewer.css?v=' + (b'20261006-versions-1' if route in VISIBLE_ART_ROUTES else b'20260905-viewport')
    inverse = inverse.replace(current_viewer, previous_viewer, 1)
    for current, previous in VIEWER_TOKEN_INVERSES:
        if current in inverse:
            if route not in VISIBLE_ART_ROUTES or inverse.count(current) != 1 or previous in inverse:
                return False
            inverse = inverse.replace(current, previous, 1)
    if b'hero-image-source.js' in inverse:
        if route not in VISIBLE_ART_ROUTES or inverse.count(VISIBLE_IMAGE_HELPER) != 1:
            return False
        inverse = inverse.replace(VISIBLE_IMAGE_HELPER, b'', 1)
    # Restore only enumerated URL tokens to the existing review's byte identity.
    # This preserves page inventory evidence, not an independent CSS acceptance.
    for current, previous in (
        (CURRENT_COMMON_SCRIPT, OLD_COMMON_SCRIPT),
        (CONTAINED_ANSWER_STYLE, BUFFER_ANSWER_STYLE),
        (BUFFER_ANSWER_STYLE, CURRENT_ANSWER_STYLE),
        (CURRENT_ART_STYLE, PREVIOUS_ART_STYLE),
        (PREVIOUS_ART_STYLE, OLD_ART_STYLE),
        (CURRENT_HERO_SCRIPT, OLD_HERO_SCRIPT),
    ):
        if current not in inverse:
            continue
        if current == CURRENT_HERO_SCRIPT and route not in VISIBLE_ART_ROUTES:
            return False
        if inverse.count(current) != 1 or previous in inverse:
            return False
        inverse = inverse.replace(current, previous, 1)
    if CURRENT_ANSWER_STYLE in inverse:
        if inverse.count(CURRENT_ANSWER_STYLE) != 1 or OLD_ANSWER_STYLE in inverse:
            return False
        inverse = inverse.replace(CURRENT_ANSWER_STYLE, OLD_ANSWER_STYLE, 1)
    if CURRENT_SHARED_STYLE in inverse:
        if inverse.count(CURRENT_SHARED_STYLE) != 1 or OLD_SHARED_STYLE in inverse:
            return False
        inverse = inverse.replace(CURRENT_SHARED_STYLE, OLD_SHARED_STYLE, 1)
    return hashlib.sha256(inverse).hexdigest() == expected


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(root, route, href):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        raise ValueError('nonlocal artwork/evidence')
    path = (root / (unquote(parsed.path).lstrip('/') if parsed.path.startswith('/')
                    else str(Path(route).parent / unquote(parsed.path)))).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('path outside site')
    return path


class Inventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.destinations = []
        self.placements = []
        self.ids = set()
        self.contexts = []
        self.placement_links = {}
        self.placement_sections = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('figure', 'section'):
            self.contexts.append((tag, [], a.get('id')))
        if a.get('id'):
            self.ids.add(a['id'])
        if tag != 'a' or not a.get('href'):
            return
        context = self.contexts[-1][1] if self.contexts else []
        context.append(a['href'])
        if 'data-artwork-detail' in a and a['href'].startswith('art-study/'):
            self.destinations.append(a['href'])
        classes = set(a.get('class', '').split())
        if 'fc-art-study-hero' in classes or 'data-art-study-supporting' in a:
            self.placements.append(a['href'])
            self.placement_links.setdefault(a['href'], []).append(context)
            ancestors = {item[2] for item in self.contexts if item[2]}
            if a.get('id'):
                ancestors.add(a['id'])
            self.placement_sections.setdefault(a['href'], []).append(ancestors)

    def handle_endtag(self, tag):
        if tag in ('figure', 'section') and self.contexts:
            if self.contexts[-1][0] == tag:
                self.contexts.pop()


def parsed(path):
    result = Inventory()
    result.feed(path.read_text(encoding='utf-8'))
    return result


def bound_json(root, reference):
    """Review files are evidence claims, never instructions or inferred approval."""
    if not isinstance(reference, dict):
        raise ValueError('missing evidence reference')
    path = local(root, 'index.html', reference['path'])
    if digest(path) != reference.get('sha256'):
        raise ValueError('changed evidence bytes')
    return json.loads(path.read_text(encoding='utf-8'))


def evaluate(root, registry):
    root = root.resolve()
    errors, rows = [], []
    gallery = parsed(root / 'art.html')
    if set(gallery.destinations) != PAGES or len(gallery.destinations) != len(PAGES):
        errors.append('featured destination inventory changed; explicitly reconcile scope')
    if registry.get('schema_version') != 1 or set(registry.get('pages', {})) != PAGES:
        errors.append('registry must cover exactly the four featured Art routes')
    if registry.get('minimum_unique_originals') != MINIMUM:
        errors.append('current mandate minimum must remain ten')
    if registry.get('christ_ratio') != 'ceil(total/2)':
        errors.append('current mandate ratio must remain ceil(total/2)')
    # No exceptions apply to these four routes. Other page exceptions are out of scope.
    if registry.get('exceptions'):
        errors.append('no owner-authorized exception established for these four routes')
    all_owners, all_hashes = {}, {}
    for route in sorted(PAGES):
        missing, defects = [], []
        page = root / route
        html = parsed(page)
        observed = [local(root, route, p).relative_to(root).as_posix() for p in html.placements]
        data = registry.get('pages', {}).get(route, {})
        entries = data.get('placements', [])
        if not reviewed_page_binding(page, route, data.get('html_sha256')):
            missing.append('page bytes changed since inventory')
        if Counter(observed) != Counter(e.get('asset') for e in entries):
            missing.append('observed hero/support placement coverage mismatch')
        # Slot discovery is not proof that unmarked imagery is absent. Require a
        # separately inspected complete-inventory receipt before any strict pass.
        try:
            coverage = bound_json(root, data.get('coverage_evidence'))
            if (coverage.get('route') != route or not reviewed_page_binding(page, route, coverage.get('html_sha256'))
                    or coverage.get('complete_page_image_inventory_reviewed') is not True
                    or coverage.get('no_unregistered_qualifying_originals') is not True
                    or set(coverage.get('reviewers', [])) != {'Fermi', 'Newton'}):
                raise ValueError('incomplete page inventory review')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            missing.append('complete inventory evidence: ' + str(exc))
        candidate_hashes, original_ids, verified, christ = set(), set(), [], 0
        for entry in entries:
            asset = entry.get('asset', '')
            try:
                path = local(root, 'index.html', asset)
                actual = digest(path)
            except (OSError, ValueError) as exc:
                missing.append(f'{asset}: unreadable asset ({exc})')
                continue
            # Distinct bytes are only an upper bound; derivatives can differ.
            candidate_hashes.add(actual)
            if actual != entry.get('sha256'):
                missing.append(f'{asset}: changed artwork bytes')
                continue
            kind = entry.get('kind')
            if kind in ('reference', 'resource'):
                # Excluded, never promoted into receiving-page originals.
                try:
                    exclusion = bound_json(root, entry.get('evidence'))
                    keys = ('asset', 'sha256', 'kind') + (('reference_target',) if kind == 'reference' else ())
                    if any(exclusion.get(k) != entry.get(k) for k in keys):
                        raise ValueError('exclusion review does not bind asset/classification')
                    if (set(exclusion.get('reviewers', [])) != {'Fermi', 'Newton'}
                            or exclusion.get('exclusion_classification_reviewed') is not True):
                        raise ValueError('independent exclusion review missing')
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    missing.append(f'{asset}: exclusion evidence ({exc})')
                if kind == 'reference':
                    try:
                        target = entry['reference_target']
                        owner = local(root, route, target)
                        fragment = urlsplit(target).fragment
                        if owner == page or not owner.is_file() or not fragment or fragment not in parsed(owner).ids:
                            raise ValueError('reference must resolve to another actual owning page/section')
                        contexts = [links for href, groups in html.placement_links.items()
                                    if local(root, route, href).relative_to(root).as_posix() == asset
                                    for links in groups]
                        if not contexts or any(target not in links for links in contexts):
                            raise ValueError('owning target link absent from picture figure/section')
                    except (OSError, ValueError, KeyError, TypeError) as exc:
                        missing.append(f'{asset}: reference ownership ({exc})')
                continue
            if kind != 'original':
                missing.append(f'{asset}: original/reference/resource classification unverified')
                continue
            oid = entry.get('original_id')
            if not isinstance(oid, str) or not oid:
                missing.append(f'{asset}: original lineage unverified')
                continue
            if oid in original_ids:
                defects.append(f'{asset}: duplicate original or derivative placement')
            original_ids.add(oid)
            if oid in all_owners and all_owners[oid] != route:
                defects.append(f'{asset}: original claimed by multiple routes')
            all_owners[oid] = route
            if actual in all_hashes:
                defects.append(f'{asset}: duplicate original bytes')
            all_hashes[actual] = route
            if (entry.get('owner_route') != route or not entry.get('owner_section')
                    or entry['owner_section'] not in html.ids):
                missing.append(f'{asset}: owning route/section unverified')
                continue
            containing = [sections for href, groups in html.placement_sections.items()
                          if local(root, route, href).relative_to(root).as_posix() == asset
                          for sections in groups]
            if not containing or any(entry['owner_section'] not in sections for sections in containing):
                defects.append(f'{asset}: claimed owning section does not contain artwork placement')
                continue
            if type(entry.get('depicts_christ')) is not bool:
                missing.append(f'{asset}: Christ classification unverified')
                continue
            try:
                review = bound_json(root, entry.get('evidence'))
                for key in ('kind', 'original_id', 'asset', 'sha256', 'owner_route',
                            'owner_section', 'depicts_christ'):
                    if review.get(key) != entry.get(key):
                        raise ValueError('review does not bind ' + key)
                if (set(review.get('reviewers', [])) != {'Fermi', 'Newton'}
                        or review.get('lineage_and_cross_page_ownership_reviewed') is not True
                        or review.get('ownership_scope') != 'all canonical site routes'
                        or review.get('pixels_reviewed_for_christ_classification') is not True):
                    raise ValueError('required independent evidence missing')
            except (OSError, ValueError, KeyError, TypeError) as exc:
                missing.append(f'{asset}: original evidence ({exc})')
                continue
            verified.append(oid)
            christ += entry['depicts_christ']
        upper = len(candidate_hashes)
        if upper < MINIMUM:
            defects.append(f'at most {upper} candidate originals in inventoried slots; requires {MINIMUM}')
        count = len(set(verified))
        if not missing and count < MINIMUM:
            defects.append(f'{count} evidenced originals; requires {MINIMUM}')
        if not missing and christ < (count + 1) // 2:
            defects.append(f'{christ} Christ originals; requires {(count + 1) // 2}')
        rows.append(dict(route=route, candidate_original_upper_bound_in_slots=upper,
                         evidenced_unique_originals=count, evidenced_christ_originals=christ,
                         minimum=MINIMUM, required_christ_for_evidenced_total=(count + 1) // 2,
                         status='FAIL' if defects else 'UNVERIFIED' if missing else 'PASS',
                         defects=defects, unverified=missing))
    ok = not errors and all(row['status'] == 'PASS' for row in rows)
    return dict(scope='four featured Art routes only', status='PASS' if ok else 'INCOMPLETE',
                limitations='Evidence consistency/count gate; no new pixel, source, native, aesthetic, or 130-route acceptance.',
                errors=errors, pages=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--registry', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    registry = args.registry or args.root / 'docs/art-study-current-mandate-inventory.json'
    try:
        result = evaluate(args.root, json.loads(registry.read_text(encoding='utf-8')))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = dict(scope='four featured Art routes only', status='INCOMPLETE', errors=[str(exc)])
    output = json.dumps(result, indent=2)
    if args.report:
        args.report.write_text(output + '\n', encoding='utf-8')
    print(output)
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
