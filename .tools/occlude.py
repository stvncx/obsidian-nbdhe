"""Build image-occlusion pairs from a JSON spec.

For each diagram writes <name>.png (labels visible) and <name>-q.png (labels covered
by numbered boxes) into the output dir. Spec entry:
  {"name": "anat-gingiva", "pdf": "Anatomy", "pdf_page": 2,
   "crop": [x0,y0,x1,y1], "labels": [[[x0,y0,x1,y1], "answer"], ...]}
Coordinates are pixels on the page rendered at 200 dpi (see render()).

Usage: .tools/.venv/bin/python .tools/occlude.py .tools/anatomy-diagrams.json Flashcards/Anatomy/images
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / '.tools' / 'cache'
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
PAD = 4
DPI = 200

def render(pdf, page):
    out = CACHE / f'{pdf}-{page:03d}.png'
    if not out.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        subprocess.run(['pdftoppm', '-r', str(DPI), '-png', '-singlefile', '-f', str(page), '-l', str(page),
                        str(ROOT / '.source' / 'RDH' / f'{pdf}.pdf'), str(out.with_suffix(''))], check=True)
    return out

def build(spec, outdir):
    page = Image.open(render(spec['pdf'], spec['pdf_page'])).convert('RGB')
    cx0, cy0, cx1, cy1 = spec['crop']
    orig = page.crop(spec['crop'])
    q = orig.copy(); d = ImageDraw.Draw(q)
    for i, (box, _) in enumerate(spec['labels'], 1):
        x0, y0, x1, y1 = box[0]-cx0-PAD, box[1]-cy0-PAD, box[2]-cx0+PAD, box[3]-cy0+PAD
        d.rounded_rectangle((x0, y0, x1, y1), radius=10, fill=(232, 120, 30), outline=(120, 50, 0), width=3)
        d.text(((x0+x1)/2, (y0+y1)/2), str(i), font=FONT, fill='white', anchor='mm')
    w = 900  # keep vault light
    for im, suffix in ((orig, ''), (q, '-q')):
        im.resize((w, round(im.height*w/im.width)), Image.LANCZOS).save(f"{outdir}/{spec['name']}{suffix}.png", optimize=True)

if __name__ == '__main__':
    for spec in json.load(open(sys.argv[1])): build(spec, sys.argv[2])
