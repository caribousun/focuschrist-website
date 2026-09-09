"""Do not activate a gateway that requires a library not yet published by Pages."""
import hashlib, pathlib, time, urllib.request
expected = hashlib.sha256(pathlib.Path('scripture-data/catalog.json').read_bytes()).hexdigest()
for attempt in range(60):
    try:
        request = urllib.request.Request('https://focuschrist.com/scripture-data/catalog.json',headers={'Cache-Control':'no-cache'})
        with urllib.request.urlopen(request,timeout=10) as response:
            raw = response.read(500000)
        if hashlib.sha256(raw).hexdigest() == expected:
            print('Published scripture catalog matches this release'); break
    except Exception:
        pass
    time.sleep(10)
else:
    raise SystemExit('Matching scripture library is not published; existing Worker preserved')
