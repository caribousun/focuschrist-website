"""Fail-closed two-stage evidence integrity for new artwork; not aesthetic detection.

preflight validates one exact proposed generation; use/release additionally require
all added repository rasters to be covered, both finished reviews, and root rendered
evidence. Baseline rasters and PDFs remain byte-frozen. Receipts are review records,
not authenticated signatures. Undisclosed ancestry cannot be inferred from pixels.
"""
import argparse
import datetime as dt
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '6f9a0c9d68f60bbb8e277662220a87f7d295ade5'
REJECTED = {'5059b4aa414bf57dc9c46608c5c05255810c81faafb472808dfbd9370efdea73'}
RASTERS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.avif', '.bmp', '.tif', '.tiff'}
REVIEWERS = {'Fermi', 'Newton'}
MANDATES = {'AGENTS.md', 'docs/historical-character-identity.md', 'docs/focuschrist-enrichment-and-stewardship-prompt.md'}
CHECKS = {'identity', 'age', 'expression_gaze', 'atmosphere', 'environment', 'characters_realism', 'period_sources', 'anatomy', 'uniqueness', 'desktop_phone'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def stamp(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(parsed.tzinfo is not None, 'Timestamp requires timezone')
    return parsed


def local(root, name):
    path = (root / name).resolve()
    require(path.is_relative_to(root.resolve()), 'Evidence must be inside repository: ' + name)
    require(path.is_file(), 'Missing evidence file: ' + name)
    return path


def checked_overrides(root, overrides, mode='use'):
    if overrides is None:
        return {}
    require(mode == 'use', 'Prospective pages only supported in use mode')
    require(isinstance(overrides, dict), 'Page overrides must be a mapping')
    for name, data in overrides.items():
        require(isinstance(name, str) and re.fullmatch(r'[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*\.html', name), 'Invalid prospective HTML route')
        local(root, name)
        require(isinstance(data, bytes), 'Prospective HTML must be exact UTF-8 bytes')
        data.decode('utf-8')
    return overrides


def content_bytes(root, name, page_overrides=None):
    if page_overrides and name in page_overrides:
        return page_overrides[name]
    return local(root, name).read_bytes()


def files(root, entries, rejected, page_overrides=None):
    require(isinstance(entries, list) and entries, 'Missing evidence files')
    names = set()
    for entry in entries:
        name = entry['path']
        require(name not in names, 'Duplicate evidence path: ' + name)
        names.add(name)
        actual = hashlib.sha256(content_bytes(root, name, page_overrides)).hexdigest()
        require(actual == entry['sha256'], 'Stale evidence hash: ' + name)
        require(actual not in rejected, 'Owner-rejected evidence: ' + name)
    return names


def reviews(entries, binding, stage, rejected, root):
    require(isinstance(entries, list) and len(entries) == 2, stage + ': exactly two reviewers required')
    require({r['reviewer'] for r in entries} == REVIEWERS, stage + ': distinct Fermi and Newton required')
    require(len({r['receipt_id'] for r in entries}) == 2 and all(r['receipt_id'].strip() for r in entries), 'Duplicate/empty receipt id')
    for review in entries:
        require(review['stage'] == stage and review['verdict'] == 'PASS' and review.get('withdrawn') is False, stage + ': negative, withdrawn or wrong-stage review')
        require(review['binding_sha256'] == binding, stage + ': stale review binding')
        stamp(review['reviewed_at'])
        require(isinstance(review.get('observations'), str) and review['observations'].strip(), 'Missing actual review observations')
        if stage == 'finished':
            require(set(review.get('checks', {})) == CHECKS and all(isinstance(v, str) and v.strip() for v in review['checks'].values()), 'Incomplete finished pixel checks')
            require(review.get('full_resolution_inspected') is True and review.get('face_details_inspected') is True, 'Missing original-resolution/face inspection')
            files(root, review['evidence'], rejected)


def validate_preflight(root, preflight, rejected):
    spec = preflight['spec']
    require(isinstance(spec['id'], str) and spec['id'].strip(), 'Missing generation id')
    require(spec.get('role') in {'hero', 'body', 'reference'}, 'Missing artwork role')
    require(isinstance(spec.get('route'), str) and spec['route'].strip(), 'Missing route')
    files(root, [spec['prompt']], rejected)
    require(files(root, spec['mandates'], rejected) == MANDATES, 'Exact current mandate set required')
    files(root, spec['references'], rejected)
    if 'edit_target' in spec:
        files(root, [spec['edit_target']], rejected)
        require(Path(spec['edit_target']['path']).suffix.lower() in RASTERS, 'Edit target must be raster')
    files(root, [spec['source_record']], rejected)
    chronology = spec.get('chronology')
    if chronology is None:
        date = dt.date.fromisoformat(spec['scene_date'])
    else:
        require('scene_date' not in spec, 'Do not mix exact and qualified chronology')
        require(chronology.get('kind') in {'approximate-historical', 'scripture-devotional', 'contemporary-application'}, 'Unknown qualified chronology')
        require(all(isinstance(chronology.get(k), str) and chronology[k].strip() for k in ('period', 'basis')), 'Missing qualified chronology evidence')
        require(isinstance(chronology.get('source_urls'), list) and chronology['source_urls'] and all(isinstance(u, str) and u.startswith('https://') for u in chronology['source_urls']), 'Missing chronology sources')
        date = None
    require(spec.get('characters'), 'Missing scene characters')
    require(len({c['name'] for c in spec['characters']}) == len(spec['characters']), 'Duplicate character')
    reference_names = {r['path'] for r in spec['references']}
    for character in spec['characters']:
        if date is not None:
            born = dt.date.fromisoformat(character['birth_date'])
            age = date.year - born.year - ((date.month, date.day) < (born.month, born.day))
            require(character['age'] == age and age >= 0, 'Scene date/age mismatch: ' + character['name'])
        else:
            require('birth_date' not in character and 'age' not in character, 'Qualified chronology cannot assert exact age or birth date')
            age_context = character.get('age_context', {})
            require(age_context.get('status') in {'approximate', 'unknown', 'illustrative'}, 'Missing qualified age status')
            require(all(isinstance(age_context.get(k), str) and age_context[k].strip() for k in ('depiction', 'basis')), 'Missing qualified age evidence')
        require(character['reference_path'] in reference_names, 'Character reference missing')
        require(character.get('identity_authority') in {'owner-approved', 'owner-linked-expression-correction', 'researched-no-owner-master'}, 'Unresolved identity authority')
        require(character.get('owner_evidence', '').strip(), 'Missing identity provenance')
    require(spec.get('period_clothing_setting', '').strip() and spec.get('interaction', '').strip(), 'Missing historical/interaction requirements')
    binding = canonical(spec)
    reviews(preflight['reviews'], binding, 'preflight', rejected, root)
    return binding


def pixel_hash(path):
    from PIL import Image
    with Image.open(path) as image:
        require(getattr(image, 'n_frames', 1) == 1, 'New animated artwork requires explicit frame review support')
        pixels = image.convert('RGBA')
        return hashlib.sha256(str(pixels.size).encode() + pixels.tobytes()).hexdigest()


def page_dependencies(root, route, page_overrides=None):
    """Bind the route and all static local stylesheet dependencies, including imports."""
    origin = 'https://focuschrist.com/'
    required = set()
    def resolve(url, parent):
        target = urlsplit(urljoin(origin + parent, url))
        if target.hostname not in {'focuschrist.com', 'www.focuschrist.com'}:
            return None
        name = unquote(target.path).lstrip('/')
        local(root, name)
        return name
    def css(name):
        if name in required:
            return
        required.add(name)
        content = re.sub(r'/\*.*?\*/', '', local(root, name).read_text(encoding='utf-8'), flags=re.S)
        imports(content, name)
    def imports(content, parent):
        for match in re.finditer(r'''@import\s+(?:url\(\s*)?["']?([^\s"');]+)''', content, re.I):
            dependency = resolve(match.group(1), parent)
            if dependency:
                css(dependency)
    class Page(HTMLParser):
        in_style = False
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            require(tag != 'base', 'Base URL requires explicit artwork context support')
            if tag == 'link' and 'stylesheet' in attrs.get('rel', '').lower().split():
                dependency = resolve(attrs.get('href', ''), route)
                if dependency:
                    css(dependency)
            if tag == 'style':
                self.in_style = True
        def handle_endtag(self, tag):
            if tag == 'style':
                self.in_style = False
        def handle_data(self, data):
            if self.in_style:
                imports(data, route)
    required.add(route)
    Page().feed(content_bytes(root, route, page_overrides).decode('utf-8'))
    return required


def validate_creation(root, creation, preflight, rejected, preflights=None, page_overrides=None):
    page_overrides = checked_overrides(root, page_overrides)
    binding = validate_preflight(root, preflight, rejected)
    spec = creation['spec']
    require(spec['id'] == preflight['spec']['id'] and spec['preflight_sha256'] == binding, 'Creation preflight mismatch')
    require(spec['route'] == preflight['spec']['route'] and spec['role'] == preflight['spec']['role'], 'Creation placement mismatch')
    generated = stamp(spec['generated_at'])
    require(all(stamp(r['reviewed_at']) < generated for r in preflight['reviews']), 'Generation preceded preflight')
    require(spec.get('owner_status') in {'not-reviewed', 'approved'}, 'Owner-rejected or unknown owner status')
    ancestors = spec['ancestor_sha256']
    require(isinstance(ancestors, list) and all(isinstance(v, str) and len(v) == 64 for v in ancestors), 'Malformed ancestry')
    require(not (set(ancestors) & rejected), 'Owner-rejected ancestor')
    require({r['sha256'] for r in preflight['spec']['references']} <= set(ancestors), 'Reference lineage missing')
    assets = [spec['original'], *spec['derivatives']]
    require(spec['derivatives'], 'Missing delivered derivatives')
    files(root, assets, rejected)
    for asset in assets:
        require(pixel_hash(local(root, asset['path'])) == asset['pixel_sha256'], 'Stale decoded pixels: ' + asset['path'])
    generations = spec.get('derivative_generations', [])
    require(isinstance(generations, list), 'Derivative generations must be a list')
    # Initial generation and each later edit retain their distinct genuine preflights.
    available = {spec['original']['path']: (spec['original']['sha256'], generated)}
    derivative_paths = {a['path'] for a in spec['derivatives']}
    asset_by_path = {a['path']: a for a in assets}
    used_preflights = {spec['id']}
    all_preflight_receipts = list(preflight['reviews'])
    latest_generated = generated
    for generation in generations:
        identity = generation['preflight_id']
        require(identity not in used_preflights, 'Duplicate derivative preflight')
        matches = [p for p in (preflights or []) if p['spec']['id'] == identity]
        require(len(matches) == 1, 'Missing unique derivative preflight')
        edit = matches[0]; edit_spec = edit['spec']
        edit_binding = validate_preflight(root, edit, rejected)
        require(edit_binding == generation['preflight_sha256'], 'Stale derivative preflight binding')
        require(edit_spec['role'] == spec['role'] and edit_spec['route'] == spec['route'], 'Derivative placement mismatch')
        require(edit_spec['characters'] == preflight['spec']['characters'] and edit_spec.get('scene_date') == preflight['spec'].get('scene_date') and edit_spec.get('chronology') == preflight['spec'].get('chronology'), 'Derivative character or event drift')
        target = edit_spec.get('edit_target', {})
        require(target.get('path') in available, 'Edit target is not original or prior generated output')
        target_hash, target_time = available[target['path']]
        require(target.get('sha256') == target_hash, 'Edit target lineage mismatch')
        edited_at = stamp(generation['generated_at'])
        require(all(target_time < stamp(r['reviewed_at']) < edited_at for r in edit['reviews']), 'Derivative chronology requires target then preflight then generation')
        require({r['sha256'] for r in edit_spec['references']} <= set(ancestors), 'Derivative reference lineage missing')
        outputs = generation['outputs']
        require(isinstance(outputs, list) and outputs and len(set(outputs)) == len(outputs), 'Missing or duplicate derivative outputs')
        require(set(outputs) <= derivative_paths and not (set(outputs) & set(available)), 'Derivative outputs must be new delivered derivatives')
        for name in outputs:
            available[name] = (asset_by_path[name]['sha256'], edited_at)
        used_preflights.add(identity)
        all_preflight_receipts.extend(edit['reviews'])
        latest_generated = max(latest_generated, edited_at)
    all_ids = [r['receipt_id'] for r in all_preflight_receipts]
    require(len(set(all_ids)) == len(all_ids), 'Receipt reused across generation preflights')
    context = files(root, spec['page_context'], rejected, page_overrides)
    required = page_dependencies(root, spec['route'].lstrip('/'), page_overrides)
    require(required <= context, 'Applicable page/CSS missing from review context: ' + ', '.join(sorted(required - context)))
    current = canonical(spec)
    reviews(creation['reviews'], current, 'finished', rejected, root)
    require(all(stamp(r['reviewed_at']) > latest_generated for r in creation['reviews']), 'Finished review predates generation')
    require(not ({r['receipt_id'] for r in creation['reviews']} & {r['receipt_id'] for r in all_preflight_receipts}), 'Receipt reused across stages')
    assembled = creation['root_review']
    require(assembled['reviewer'] == 'Albert' and assembled['verdict'] == 'PASS' and assembled['binding_sha256'] == current, 'Missing current Albert assembled review')
    require(assembled.get('observations', '').strip(), 'Missing assembled observations')
    require(set(assembled['evidence']) == {'desktop', 'phone'}, 'Desktop and phone evidence required')
    for evidence in assembled['evidence'].values():
        files(root, evidence, rejected)
    return {a['path'] for a in assets}


def git_inventory(root, commit):
    raw = subprocess.check_output(['git', 'ls-tree', '-rz', commit], cwd=root)
    return {name.decode(): meta.decode().split()[2] for entry in raw.split(b'\0') if entry for meta, name in [entry.split(b'\t', 1)] if Path(name.decode()).suffix.lower() in RASTERS | {'.pdf'}}


def baseline_check(root, baseline):
    require(baseline.get('schema') == 1 and baseline.get('commit') == BASELINE, 'Immutable baseline changed')
    require(REJECTED <= set(baseline.get('rejected_sha256', [])), 'Owner rejection removed')
    inventory = git_inventory(root, BASELINE)
    require(inventory, 'Baseline inventory unavailable')
    for name, blob in inventory.items():
        data = local(root, name).read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(actual == blob, 'Frozen baseline artwork/PDF changed: ' + name)
    return inventory


NATIVE_CONFERENCE_LEDGER = 'docs/general-conference-source-ledger.json'
NATIVE_CONFERENCE_REVIEW = 'docs/conference-2026-10-native-review.json'
NATIVE_CONFERENCE_ITEMS_SHA256 = 'fe829c991e76048e6b7d138b3d003023fe430aa3aab9751f68ab69d25088a1ba'
NATIVE_CONFERENCE_LEDGER_SHA256 = '2c3c7d4f75f508f5cafb1aede25069a2c561f9ba9fa1a1ddfbfb1e97aea60c80'


def validate_native_conference(root, rejected):
    """Source evidence for this exact native Church set, never generation evidence."""
    review_path = root / NATIVE_CONFERENCE_REVIEW
    if not review_path.exists():
        return set()
    record = json.loads(review_path.read_text(encoding='utf-8'))
    require(record.get('schema') == 1, 'Unknown native source review schema')
    for historical in record.get('prior_page_context_bindings', []):
        require(canonical(historical['spec']) == historical.get('binding_sha256'), 'Stale historical native context binding')
    spec = record['spec']
    require(spec.get('kind') == 'official-native-conference-thumbnails', 'Wrong native source kind')
    collection = 'https://www.churchofjesuschrist.org/study/general-conference/2026/10?lang=eng'
    require(spec.get('collection') == collection, 'Wrong native conference collection')
    require(spec.get('ledger_sha256') == digest(local(root, NATIVE_CONFERENCE_LEDGER)) == NATIVE_CONFERENCE_LEDGER_SHA256, 'Native source ledger differs from independently reviewed bytes')
    ledger = json.loads(local(root, NATIVE_CONFERENCE_LEDGER).read_text(encoding='utf-8'))
    items = ledger['items']
    require(spec.get('items_sha256') == canonical(items) == NATIVE_CONFERENCE_ITEMS_SHA256, 'Unreviewed native source item manifest')
    require(ledger['official_collection'] == collection and ledger['item_count'] == len(items) == 38, 'Native source collection must contain exact 38 records')
    paths = set()
    from PIL import Image
    for item in items:
        name = item['local_thumbnail']
        require(name == 'assets/resources/conference-2026-10/' + item['id'] + '.jpg' and name not in paths, 'Unexpected or duplicate native resource path')
        require(item['url'] == collection.replace('?lang=eng', '/' + item['id'] + '?lang=eng'), 'Wrong native message month or identity')
        require(re.fullmatch(r'https://www\.churchofjesuschrist\.org/imgs/[a-z0-9]+/full/%21768%2C/0/default', item['thumbnail_url']) is not None, 'Untrusted native thumbnail source')
        require(re.fullmatch(r'[0-9a-f]{64}', item['source_sha256']) is not None, 'Missing exact official page evidence')
        asset = local(root, name)
        require(digest(asset) == item['sha256'] and item['sha256'] not in rejected and asset.stat().st_size == item['bytes'], 'Native thumbnail bytes differ from source review')
        with Image.open(asset) as image:
            require(image.format == 'JPEG' and image.size == (item['width'], item['height']), 'Native thumbnail format or dimensions changed')
        paths.add(name)
    require(files(root, spec['page_context'], rejected) == {'general-conference.html', 'general-conference-section.css'}, 'Native source review requires exact page and stylesheet context')
    binding = canonical(spec)
    reviews(record['reviews'], binding, 'official-source', rejected, root)
    for review in record['reviews']:
        require(review.get('pixels_inspected') is True, 'Native source contact pixels not inspected')
        files(root, review['evidence'], rejected)
    assembled = record['root_review']
    require(assembled.get('reviewer') == 'Albert' and assembled.get('verdict') == 'PASS' and assembled.get('binding_sha256') == binding and assembled.get('pixels_inspected') is True and assembled.get('withdrawn') is False, 'Missing or stale native assembled review')
    require(isinstance(assembled.get('observations'), str) and assembled['observations'].strip(), 'Missing native assembled observations')
    stamp(assembled['reviewed_at'])
    files(root, assembled['desktop'], rejected)
    files(root, assembled['phone'], rejected)
    return paths


def run(root, mode='release', scene=None, page_overrides=None):
    page_overrides = checked_overrides(root, page_overrides, mode)
    baseline = json.loads((root / 'docs/artwork-creation-baseline.json').read_text(encoding='utf-8'))
    registry = json.loads((root / 'docs/artwork-creation-reviews.json').read_text(encoding='utf-8'))
    require(registry.get('schema') == 1, 'Unknown review schema')
    inventory = baseline_check(root, baseline)
    rejected = set(baseline['rejected_sha256']) | REJECTED
    preflights = registry['preflights']; creations = registry['creations']
    for rows in (preflights, creations):
        require(len({r['spec']['id'] for r in rows}) == len(rows), 'Duplicate scene record')
    if mode == 'preflight':
        selected = [p for p in preflights if p['spec']['id'] == scene]
        require(len(selected) == 1, 'Exactly one requested preflight required')
        validate_preflight(root, selected[0], rejected)
        return {'stage': mode, 'scene': scene, 'evidence_integrity': 'PASS', 'aesthetic_acceptance': False}
    # Scan tracked AND untracked public content, so omitting a new raster record fails.
    candidates = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root).decode().split('\0')
    # .qa-artifacts is the workflow's explicitly separate browser-evidence output.
    # No generic dot-file exclusion: assets/.new.png and nested dot directories count.
    raster_paths = {p for p in candidates if p and Path(p).suffix.lower() in RASTERS and Path(p).parts[0] != '.qa-artifacts'}
    added = raster_paths - set(inventory)
    covered = set(); originals = set(); original_pixels = set(); receipt_ids = set()
    for creation in creations:
        selected = [p for p in preflights if p['spec']['id'] == creation['spec']['id']]
        require(len(selected) == 1, 'Missing unique creation preflight')
        assets = validate_creation(root, creation, selected[0], rejected, preflights, page_overrides)
        require(not (assets & covered), 'Asset used by duplicate creation records')
        require(assets <= added, 'Creation assets must be new, not frozen body artwork')
        covered |= assets
        related_ids = {g['preflight_id'] for g in creation['spec'].get('derivative_generations', [])}
        related_reviews = [r for p in preflights if p['spec']['id'] in related_ids for r in p['reviews']]
        for receipt in selected[0]['reviews'] + related_reviews + creation['reviews']:
            require(receipt['receipt_id'] not in receipt_ids, 'Receipt id reused between scenes')
            receipt_ids.add(receipt['receipt_id'])
        scene_assets = [creation['spec']['original'], *creation['spec']['derivatives']]
        hashes = {a['sha256'] for a in scene_assets}
        pixels = {a['pixel_sha256'] for a in scene_assets}
        require(not (hashes & originals) and not (pixels & original_pixels), 'Duplicate artwork across new scenes')
        originals |= hashes; original_pixels |= pixels
    native = validate_native_conference(root, rejected)
    require(not (native & covered) and native <= added, 'Native source coverage must be new and separate from generated artwork')
    covered |= native
    # Exact historical/correction lineage is distinct from current precreation.
    # Filled only after actual independent/root review of the complete ledger.
    from artwork_historical_delivery import validate as validate_historical_delivery
    approved_historical_binding = '65b50f0ea7fde8444f7ac6191b9d9267fc1c867060cc8c83502e0a357ab6b895'
    historical_record = json.loads((root / 'docs/artwork-historical-delivery-reviews.json').read_text(encoding='utf-8'))
    historical, historical_hashes, historical_pixels = validate_historical_delivery(
        root, historical_record, approved_historical_binding, added, covered, rejected, pixel_hash)
    require(not (historical_hashes & originals) and not (historical_pixels & original_pixels), 'Historical family duplicates a new creation')
    covered |= historical
    originals |= historical_hashes
    original_pixels |= historical_pixels
    # Local corrections preserve frozen originals and historical coverage.
    # Pending until the complete separate packet receives exact review.
    from artwork_reviewed_corrections import validate as validate_reviewed_corrections
    approved_corrections_binding = '6f9510c88845fbef288289a33beab1a841f414ea65ab1212577c02e284d27a75'
    correction_record = json.loads((root / 'docs/artwork-correction-reviews.json').read_text(encoding='utf-8'))
    corrections, correction_hashes, correction_pixels = validate_reviewed_corrections(
        root, correction_record, approved_corrections_binding, added, covered, rejected, pixel_hash, inventory)
    require(not (correction_hashes & originals) and not (correction_pixels & original_pixels), 'Correction family duplicates another creation')
    covered |= corrections
    originals |= correction_hashes
    original_pixels |= correction_pixels
    require(added == covered, 'New artwork missing exact review coverage: ' + ', '.join(sorted(added - covered)))
    if creations or historical or corrections:
        for name in inventory:
            path = root / name
            if path.suffix.lower() in RASTERS:
                require(digest(path) not in originals, 'New artwork duplicates existing artwork')
                # Existing animated assets have no new-original equivalent in this gate.
                from PIL import Image
                with Image.open(path) as image:
                    if getattr(image, 'n_frames', 1) > 1:
                        continue
                require(pixel_hash(path) not in original_pixels, 'New artwork duplicates existing decoded pixels')
    return {'stage': mode, 'frozen_files': len(inventory), 'new_creations': len(creations), 'native_source_thumbnails': len(native), 'new_rasters': len(added), 'evidence_integrity': 'PASS', 'aesthetic_acceptance': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['preflight', 'use', 'release'], nargs='?', default='release')
    parser.add_argument('--scene')
    args = parser.parse_args()
    try:
        print(json.dumps(run(ROOT, args.mode, args.scene), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, 'Artwork evidence gate FAIL: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
