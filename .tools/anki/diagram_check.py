"""Check diagram specs BEFORE building: for each diagram, draw every fitted cover (numbered,
semi-transparent orange) on the crop and print the numbered answers. Look at every image:
each cover must hide its whole label and nothing else; the crop must include the whole figure.
Usage: .tools/.venv/bin/python .tools/anki/diagram_check.py SPEC.json OUTDIR [name ...]"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build_deck import covers, BOOKS, PAD
from occlude import render
spec_file, outdir = sys.argv[1], Path(sys.argv[2]); names = sys.argv[3:]
outdir.mkdir(parents=True, exist_ok=True)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
for s in json.load(open(spec_file)).get('diagrams', []):
    if names and s['name'] not in names: continue
    page = Image.open(render(BOOKS['anatomy']['pdf'], s['pdf_page'])).convert('RGB')
    cx0, cy0 = s['crop'][:2]
    im = page.crop(s['crop']).convert('RGBA'); ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    print(f"== {s['name']}  ({s['title']})  page {s['pdf_page']}  crop {s['crop']}")
    for i, (l, b) in enumerate(covers(s, page), 1):
        import math
        r = (b[0]-cx0-PAD, b[1]-cy0-PAD, b[2]-cx0+PAD, b[3]-cy0+PAD)
        a = math.radians(b[4]) if len(b) > 4 else 0; mx, my = (r[0]+r[2])/2, (r[1]+r[3])/2
        poly = [(mx + (x-mx)*math.cos(a) - (y-my)*math.sin(a), my + (x-mx)*math.sin(a) + (y-my)*math.cos(a))
                for x, y in ((r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3]))]
        d.polygon(poly, fill=(232, 120, 30, 150), outline=(180, 60, 0, 255), width=2)
        d.text((r[0] + 3, r[1] + 1), str(i), font=F, fill=(0, 0, 0, 255))
        print(f"  {i:2}. {l['answer']}   [fit={l.get('fit','bg')} cover {b[2]-b[0]:.0f}x{b[3]-b[1]:.0f}{' rot %.0f' % b[4] if len(b) > 4 else ''}]")
    Image.alpha_composite(im, ov).convert('RGB').save(outdir / f"{s['name']}.png")
