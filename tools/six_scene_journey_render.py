"""Exact two reviewed six-family additions retained by strict journey generation."""
import hashlib,json
def apply(root,route,rendered,strict):
    routes={'jesus-christ/miracles-and-compassion.html','jesus-christ/parables/good-samaritan.html'}
    if not strict or route not in routes:return rendered
    from six_scene_legacy_contracts import bound
    bound(root)
    raw=(root/'docs/six-scene-artwork/journey-render-additions.json').read_bytes()
    sha=lambda b:hashlib.sha256(b).hexdigest()
    if sha(raw)!='da015de8ac27d816dff207791e0d7a2a3db2ed0f65f3ce39bf816def7ca464bf':raise ValueError('Exact reviewed journey additions changed')
    records=json.loads(raw)
    if set(records)!=routes:raise ValueError('Unexpected journey addition owner')
    row=records[route]
    if sha(rendered.encode())!=row['baseline_render_sha256']:raise ValueError('Reviewed journey baseline render changed')
    for anchor,insertion in [(row['section_anchor'],row['section']),('</head>',row['style']),('</body>',row['script'])]:
        if rendered.count(anchor)!=1:raise ValueError('Missing or duplicate exact journey insertion anchor')
        rendered=rendered.replace(anchor,insertion+anchor,1)
    if sha(rendered.encode())!=row['reviewed_render_sha256']:raise ValueError('Strict journey result differs from reviewed bytes')
    return rendered
