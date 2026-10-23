"""Exact deterministic display-only delta. No artwork approval or generic waiver.

Historical bytes are recovered only from the exact pinned consumer candidate.
Unknown edits remain unnormalized and fail the original historical hash check.
New display rasters preserve named sources, plus exact proportional resampling.
"""
from pathlib import Path
import hashlib, json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
def sha(data): return hashlib.sha256(data).hexdigest()
def require(ok, message):
    if not ok: raise ValueError('Display delivery: ' + message)

CONSUMERS = {'index.html': 'ee2d3bfe99fb3617bb6514b08dc822315e340d4ef8c8c867e71dec993817014f', 'home-presentation.css': '08ce2b28f20963868cc093ad59b23d865282858009c262d976b2900019b99656', 'watch.html': 'f7cae4fd922eeca0f2faff144383d3fabe378b89150813f60e92a3c52523eb2e', 'come-follow-me.html': '11de2b2c31ab4dc9f784eb014df1bcb46188c7bb01a9191bef6875d0f33fadb3', 'tools/build_watch_shorts.py': '759bc6ba83e68350b2e0073915fd157b86581d2aaa4bd4688718c9e821fabd45'}
BASELINE = {'index.html': '07e35b3de16a22ff1bb23f15dd312c98d96666d6e21803135c05be9111e2ed4e', 'home-presentation.css': '40f23bc00b39bff593fe58c9f967e6f3750de43935547e88ef75249cd44866bc', 'watch.html': 'b41e4cdbd5fb3bf364f12d7759ba545948b62ff5c7323790b151257579bace74', 'come-follow-me.html': '18b214485760495f6104152126cc311e856c79e62e3103ed384fa5226e3ef540', 'tools/build_watch_shorts.py': 'def2ae7296dc49009b924b717764c83929f6737b9715729a4c31f8c94d6ffa59'}
ASSETS = [{'source': 'assets/heroes/home-christ-signature-approved-20260907.png', 'source_sha256': '4e9d4469bd9bd40d4e097eea887410a63f3c2f6dcc6ced3a3affd4813991b15b', 'source_bytes': 2440189, 'path': 'assets/heroes/home-christ-signature-approved-20260907-display.webp', 'sha256': 'f8c8877274bb3fe97e01ecffbc17b102cd47376444b49941610b6e6f7a325eb6', 'bytes': 1165988, 'dimensions': [2048, 684], 'source_decoded_rgba_sha256': '49c6dda8a8cafec36cc7cdbd2fabf72de1869de91ff901f7d35eebbe89e22dd9', 'decoded_rgba_sha256': '49c6dda8a8cafec36cc7cdbd2fabf72de1869de91ff901f7d35eebbe89e22dd9', 'method': 'same-dimension exact RGBA lossless WebP'}, {'source': 'assets/shorts/bednar-holy-ghost-or-me-approved-20261013.png', 'source_sha256': '440b4a9f6388dbb0a0791745e4d7a21a8763b908b82cf64a4b57a37ab3c9d6a0', 'source_bytes': 4140257, 'path': 'assets/shorts/bednar-holy-ghost-or-me-approved-20261013-display.webp', 'sha256': 'e6257d461722c0d8f9c722d818e6be8dbb121aabcad104de9fd18183076ea23f', 'bytes': 2281632, 'dimensions': [941, 1672], 'source_decoded_rgba_sha256': '714883fa94f2458af310c9ee9c33801bd9203918f9eda4e967a2c8aa355f2dc2', 'decoded_rgba_sha256': '714883fa94f2458af310c9ee9c33801bd9203918f9eda4e967a2c8aa355f2dc2', 'method': 'same-dimension exact RGBA lossless WebP'}, {'source': 'assets/shorts/god-is-at-your-side-portrait-20261012.png', 'source_sha256': '78f547b0f541f33e97cb8d8be33a7ea6dfdac8a10516c8712a8b08e19be1ab63', 'source_bytes': 2713244, 'path': 'assets/shorts/god-is-at-your-side-portrait-20261012-display.webp', 'sha256': '370556ca791ed494259ba327a0bd4c67f679d85a17fb529d47b7d9c51a9a0c91', 'bytes': 2051718, 'dimensions': [941, 1672], 'source_decoded_rgba_sha256': '95a57b1928d94995beb3db347a5de4f60d416d805eed4978f130851edf9a751b', 'decoded_rgba_sha256': '95a57b1928d94995beb3db347a5de4f60d416d805eed4978f130851edf9a751b', 'method': 'same-dimension exact RGBA lossless WebP'}, {'source': 'assets/page-art/home-seek-study-four-marks-20261011-full.webp', 'source_sha256': '5ad1e94b505079eadc34d6486fb3a2090feb74f756c7472a29de76a788b11ceb', 'source_bytes': 1667204, 'path': 'assets/page-art/home-seek-study-four-marks-20261011-640.webp', 'sha256': '061fa74114918d76c306b710faf8a2f104cddf91f1c3cc1bdbd33abfb6070607', 'bytes': 271500, 'dimensions': [640, 320], 'source_decoded_rgba_sha256': '8e036443974b57451cdaa204f35bb18830edb41c2af0d721679f5763277565e6', 'decoded_rgba_sha256': '9c40883c9c60361d2eaae85c2f01851b979c84e11aefa1d7bd2f05f7a91ac3e4', 'method': 'proportional Lanczos3 resampling followed by exact lossless WebP'}, {'source': 'assets/page-art/home-seek-study-four-marks-20261011-full.webp', 'source_sha256': '5ad1e94b505079eadc34d6486fb3a2090feb74f756c7472a29de76a788b11ceb', 'source_bytes': 1667204, 'path': 'assets/page-art/home-seek-study-four-marks-20261011-1280.webp', 'sha256': '67813d87651e8ae07f689eebcf15d19338264225334cfdfda03c267b27467151', 'bytes': 960388, 'dimensions': [1280, 640], 'source_decoded_rgba_sha256': '8e036443974b57451cdaa204f35bb18830edb41c2af0d721679f5763277565e6', 'decoded_rgba_sha256': '314542df4864004cc79668407fb060b5ff4466b9fd18248b9a87b8a7174de8c2', 'method': 'proportional Lanczos3 resampling followed by exact lossless WebP'}]

PRELOAD = '<link rel="preload" as="image" type="image/webp" href="assets/heroes/home-christ-signature-approved-20260907-display.webp" fetchpriority="high">\n'
CSS = '\n/* Exact approved Home hero pixels, served as a lossless display copy. */\nbody.fc-home-presentation .fc-home-hero::before {\n    background-image: url("assets/heroes/home-christ-signature-approved-20260907-display.webp");\n}\n'
OLD_IMAGE = '<img src="assets/page-art/home-seek-study-four-marks-20261011-full.webp"'
NEW_IMAGE = '<img src="assets/page-art/home-seek-study-four-marks-20261011-640.webp" srcset="assets/page-art/home-seek-study-four-marks-20261011-640.webp 640w, assets/page-art/home-seek-study-four-marks-20261011-1280.webp 1280w, assets/page-art/home-seek-study-four-marks-20261011-full.webp 1774w" sizes="(max-width: 900px) 100vw, 640px"'

def inverse(name, data):
    """Return old bytes only for the complete, exact reviewed consumer delta."""
    from timeline_source_import import restore_consumers
    data = restore_consumers(name, data)
    if name == 'site-search-index.json':
        from timeline_source_import import restore_search
        data = restore_search(data)
    # Exact generated search delta for the sole reviewed CFM wording change.
    # No other record, source, metadata or unknown byte change is normalized.
    if name == 'site-search-index.json' and sha(data) == '038391c9f469c4c7a24894c629b915851ec097d305e880bdfe12e6f24b3c9e0d':
        current = b'Explore the October 2026 General Conference study collection.'
        previous = b'Explore the April 2026 General Conference study collection.'
        require(data.count(current) == 1, 'ambiguous generated search inverse')
        restored = data.replace(current, previous, 1)
        require(sha(restored) == '5744d3b23308c419732bac77811620c2ca68b30e4dc22a1eb0775a120ddbd103', 'search inverse failed original binding')
        return restored
    if name == 'tools/build_art_gallery.py' and sha(data) == '4489874fcbe0aeac68eab1de36b9cd0739fec65ca3981edbb961ce236baa78a1':
        current = "        from artwork_display_delivery import inverse\n        # Display-only Home sizes do not replace the gallery's full original.\n        name = page.lstrip('/')\n        if name == 'missionary.html':\n            # The commission hand successor is a reviewed content delivery\n            # change, not a presentation layer: the gallery records the\n            # renditions the page actually serves, so parse it as served.\n            doc.feed((ROOT / name).read_bytes().decode('utf-8'))\n        else:\n            doc.feed(inverse(name, (ROOT / name).read_bytes()).decode('utf-8'))"
        previous = "        doc.feed((ROOT / page.lstrip('/')).read_text(encoding='utf-8'))"
        text = data.decode('utf8')
        require(text.count(current) == 1, 'ambiguous gallery builder inverse')
        restored = text.replace(current, previous, 1).encode('utf8')
        require(sha(restored) == 'f21b8a39171e7f9a998c34f66896bdcba922146f80825bae3f7d60372b3d804c', 'gallery builder inverse drift')
        return restored
    if name not in CONSUMERS or sha(data) != CONSUMERS[name]: return data
    text = data.decode('utf8')
    changes = []
    if name == 'index.html':
        changes = [(PRELOAD, ''), ('home-presentation.css?v=20261019-image-delivery-1', 'home-presentation.css?v=20261010-emma-reference-1'), (NEW_IMAGE, OLD_IMAGE)]
    elif name == 'home-presentation.css': changes = [(CSS, '')]
    elif name == 'come-follow-me.html': changes = [('Explore the October 2026 General Conference study collection.', 'Explore the April 2026 General Conference study collection.')]
    elif name == 'watch.html':
        # Bind each wrapper AND exact original img. Other sources are not eligible.
        for source, title in [('bednar-holy-ghost-or-me-approved-20261013', 'Is It the Holy Ghost or Me?'), ('god-is-at-your-side-portrait-20261012', 'God Is at Your Side')]:
            image = f'<img src="assets/shorts/{source}.png" width="941" height="1672" alt="{title}: YouTube Short preview" loading="lazy" decoding="async">'
            wrapper = f'<picture style="display: block; width: 100%; height: 100%;"><source srcset="assets/shorts/{source}-display.webp" type="image/webp">{image}</picture>'
            changes.append((wrapper, image))
    else: return data # The builder is current-bound, never historical-normalized.
    for current, previous in changes:
        require(text.count(current) == 1, 'ambiguous inverse ' + name)
        text = text.replace(current, previous, 1)
    restored = text.encode('utf8')
    require(sha(restored) == BASELINE[name], 'inverse failed original binding ' + name)
    return restored

def reviewed_bytes(path):
    try: name = path.resolve().relative_to(ROOT).as_posix()
    except ValueError: return path.read_bytes()
    return inverse(name, path.read_bytes())

def validate_pixels(root):
    paths = set()
    for row in ASSETS:
        source = root / row['source']; target = root / row['path']
        require(row['path'] not in paths and source.is_file() and target.is_file() and not source.is_symlink() and not target.is_symlink(), 'missing, duplicate or linked raster')
        require(sha(source.read_bytes()) == row['source_sha256'], 'source bytes changed: ' + row['source'])
        require(sha(target.read_bytes()) == row['sha256'], 'display bytes changed: ' + row['path'])
        with Image.open(source) as original, Image.open(target) as display:
            require(display.format == 'WEBP' and display.size == tuple(row['dimensions']) and getattr(display, 'n_frames', 1) == 1, 'display dimensions or format changed')
            require(sha(original.convert('RGBA').tobytes()) == row['source_decoded_rgba_sha256'], 'source decoded pixels changed')
            wanted = original if row['method'].startswith('same-dimension') else original.resize(tuple(row['dimensions']), Image.Resampling.LANCZOS)
            require(display.convert('RGBA').tobytes() == wanted.convert('RGBA').tobytes(), 'decoded display or alpha drift')
            require(sha(display.convert('RGBA').tobytes()) == row['decoded_rgba_sha256'], 'display decoded digest changed')
        paths.add(row['path'])
    return paths

def validate(root, added, covered):
    paths = validate_pixels(root)
    require(paths <= added and not paths & covered, 'display coverage overlap or omission')
    require(paths == added - covered, 'unsupported additional display raster')
    from continue_motion_binding import restore as before_motion
    for name, expected in CONSUMERS.items():
        require(sha(before_motion(name,(root / name).read_bytes())) == expected, 'current consumer drift: ' + name)
    record = json.loads((root / 'docs/image-delivery-20261019.json').read_text(encoding='utf8'))
    require(record['schema'] == 1 and record['assets'] == ASSETS and record['consumers'] == CONSUMERS, 'unreviewed delivery manifest')
    binding = sha(json.dumps({'assets': ASSETS, 'consumers': CONSUMERS}, sort_keys=True, separators=(',', ':')).encode())
    reviewers = record['reviews']
    require(len(reviewers) == 3 and {r['reviewer'] for r in reviewers} == {'Fermi','Newton','Albert'}, 'three actual finished reviewers required')
    for review in reviewers:
        require(review['decision'] == 'CONCUR' and review['binding_sha256'] == binding and review['source_and_derivative_pixels_inspected'] is True and review['desktop_phone_inspected'] is True and review['observations'] and review['limits'], 'unfinished display review')
        for item in review['evidence']:
            path = Path(item['path'])
            require(not path.is_absolute() and '..' not in path.parts and ':' not in item['path'] and '\\' not in item['path'], 'unsafe display evidence')
            from timeline_source_import import restore_code_evidence
            require(sha(restore_code_evidence(item['path'], (root / path).read_bytes())) == item['sha256'], 'display review evidence changed')
        require(review['evidence'], 'missing actual review evidence')
    return paths
