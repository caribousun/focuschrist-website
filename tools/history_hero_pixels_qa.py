"""Inspect screenshot pixels, not image decode/DOM geometry alone."""
import json
import math
from collections import Counter
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageStat


def measure(image):
    sample = image.convert('RGB')
    sample.thumbnail((240, 100))
    pixels = list(sample.get_flattened_data())
    buckets = Counter(tuple(channel // 16 for channel in pixel) for pixel in pixels)
    # Several similar navy shades from a fade must still count as blank background.
    candidates = [tuple(channel * 16 + 8 for channel in key) for key, _ in buckets.most_common(12)]
    solid_fraction = max(sum(max(abs(a-b) for a, b in zip(pixel, center)) <= 18 for pixel in pixels) / len(pixels) for center in candidates)
    thirds = []
    for index in range(3):
        region = sample.crop((index*sample.width//3, 0, (index+1)*sample.width//3, sample.height))
        thirds.append({'max_channel_stddev': max(ImageStat.Stat(region).stddev), 'quantized_colors': len({tuple(c//16 for c in p) for p in region.get_flattened_data()})})
    failures = []
    if solid_fraction >= .8:
        failures.append('At least80% of hero is near one solid color')
    if any(region['max_channel_stddev'] < 4 or region['quantized_colors'] < 12 for region in thirds):
        failures.append('A broad third of the hero lacks expected scene variation')
    return {'near_solid_fraction': solid_fraction, 'thirds': thirds, 'failures': failures}


if '--self-test' in sys.argv:
    good = Image.new('RGB', (300, 100))
    good.putdata([(x*3 % 256, y*7 % 256, (x+y)*5 % 256) for y in range(100) for x in range(300)])
    assert not measure(good)['failures']
    broken = good.copy()
    ImageDraw.Draw(broken).rectangle((0, 0, 259, 99), fill=(28, 55, 67))
    assert measure(broken)['near_solid_fraction'] > .8 and measure(broken)['failures']
    assert measure(Image.new('RGB', (300, 100), (28, 55, 67)))['failures']
    print('PASS: varied scene accepted; reproduced navy86%/right-strip and fully blank fixtures rejected')
else:
    screenshot = Path(sys.argv[1])
    bounds = json.loads(sys.argv[2])
    with Image.open(screenshot) as image:
        box = (math.ceil(bounds['x']), math.ceil(bounds['y']), math.floor(bounds['x']+bounds['width']), math.floor(bounds['y']+bounds['height']))
        assert box[0] >= 0 and box[1] >= 0 and box[2] <= image.width and box[3] <= image.height
        result = measure(image.crop(box))
    print(json.dumps(result))
    raise SystemExit(bool(result['failures']))
