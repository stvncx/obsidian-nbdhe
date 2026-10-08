"""Build the NBDHE Anki deck (.apkg) from the spec files in a book folder.

Spec files: .tools/anki/<book>/*.json, each {"diagrams": [...], "cloze": [...], "mcq": [...]}
(format documented in .claude/RUNBOOK.md §6). Three note types, all custom HTML/CSS so they
render the same on Anki desktop / AnkiMobile / AnkiDroid:

- "NBDHE Image Occlusion": one label covered per card; the back removes the cover so the
  book's own label shows (no {{FrontSide}} -> the reveal is in place).
- "NBDHE Cloze": Anki cloze note type (Text with {{c1::...}}, Extra, Source).
- "NBDHE MCQ": 4-option question; back shows the key + explanation.

IDs are FIXED (models, decks) and note GUIDs come from stable keys (diagram name + answer,
cloze/mcq "id"), so re-importing an updated deck UPDATES notes and keeps review history.
NEVER change the ID constants or the guid recipes.

Usage: .tools/.venv/bin/python .tools/anki/build_deck.py OUT.apkg [book=anatomy] [--only NAME,...]
"""
import glob, hashlib, json, sys
from pathlib import Path
import genanki
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from occlude import render

ROOT = Path(__file__).resolve().parents[2]
MEDIA = ROOT / '.tools' / 'anki' / 'media'
PAD = 2          # px on the 200-dpi page around a fitted cover (hides the soft edge)
WIDTH = 1400     # px of each diagram's media image
IO_MODEL_ID = 1728390001       # fixed forever
CLOZE_MODEL_ID = 1728390002    # fixed forever
MCQ_MODEL_ID = 1728390003      # fixed forever
ROOT_DECK = 'NBDHE'
BOOKS = {'anatomy': {'pdf': 'Anatomy', 'deck': 'Anatomy', 'page0': 146}}   # book page = pdf page + page0

def deck_id(name):            # stable id derived from the full deck name
    return int(hashlib.sha1(name.encode()).hexdigest()[:8], 16) | (1 << 30)

# ---------------------------------------------------------------- shared look
BASE_CSS = """
.card { font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: #f6f5f2; color: #1d1d1f; margin: 0; padding: 14px; font-size: 20px; line-height: 1.45; }
.title { font-size: 14px; font-weight: 600; letter-spacing: .04em; color: #6b6b70;
  margin: 2px 0 12px; text-transform: uppercase; text-align: center; }
.panel { max-width: 720px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 18px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,.10), 0 6px 20px rgba(0,0,0,.05); text-align: left; }
.extra { max-width: 720px; margin: 12px auto 0; font-size: 16px; color: #3a3a3c; text-align: left;
  border-left: 3px solid #0b6bcb; padding: 4px 0 4px 12px; }
.source { max-width: 720px; margin: 10px auto 0; font-size: 12px; color: #8e8e93; text-align: right; }
.nightMode.card, .night_mode .card { background: #1c1c1e; color: #f2f2f7; }
.nightMode .panel, .night_mode .panel { background: #2c2c2e; box-shadow: none; }
.nightMode .title, .night_mode .title, .nightMode .source, .night_mode .source { color: #a1a1a6; }
.nightMode .extra, .night_mode .extra { color: #d1d1d6; }
"""

# ---------------------------------------------------------------- image occlusion
IO_CSS = BASE_CSS + """
.card { text-align: center; }
.io { container-type: inline-size; position: relative; display: inline-block; width: 100%;
  max-width: 1000px; line-height: 0; border-radius: 10px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,.12), 0 6px 20px rgba(0,0,0,.06); }
.io img { width: 100%; height: auto; display: block; max-width: none; max-height: none; }
.io-box { position: absolute; display: flex; align-items: center; justify-content: center;
  box-sizing: border-box; border-radius: 4px; padding: 0; line-height: 1.1;
  font-size: 2.5cqw; font-weight: 700; text-align: center; white-space: normal; }
.io-box.ask { background: #e8781e; color: #fff; border: 1px solid #b85a0e; font-size: 2.6cqw; }
.io-box.show { background: transparent; border: 3px solid #0b6bcb;
  box-shadow: 0 0 0 4px rgba(11,107,203,.25); }   /* cover removed: the book's own label shows */
"""
BOX = 'left:{{Left}}%;top:{{Top}}%;width:{{Width}}%;height:{{Height}}%;transform:rotate({{Rotate}}deg)'
IO_FRONT = f"""<div class="title">{{{{Title}}}}</div>
<div class="io">{{{{Image}}}}<div class="io-box ask" style="{BOX}">?</div></div>"""
IO_BACK = f"""<div class="title">{{{{Title}}}}</div>
<div class="io">{{{{Image}}}}<div class="io-box show" style="{BOX}"></div></div>
{{{{#Extra}}}}<div class="extra">{{{{Extra}}}}</div>{{{{/Extra}}}}"""
IO_MODEL = genanki.Model(
    IO_MODEL_ID, 'NBDHE Image Occlusion',
    fields=[{'name': n} for n in ('Answer', 'Image', 'Title', 'Left', 'Top', 'Width', 'Height', 'Extra', 'Source', 'Rotate')],
    templates=[{'name': 'Occlusion', 'qfmt': IO_FRONT, 'afmt': IO_BACK}], css=IO_CSS, sort_field_index=0)

# ---------------------------------------------------------------- cloze
CLOZE_CSS = BASE_CSS + """
.cloze { font-weight: 700; color: #0b6bcb; }
.nightMode .cloze, .night_mode .cloze { color: #5eaeff; }
.panel ul, .panel ol { margin: .3em 0 .3em 1.2em; padding: 0; }
"""
CLOZE_MODEL = genanki.Model(
    CLOZE_MODEL_ID, 'NBDHE Cloze',
    fields=[{'name': n} for n in ('Text', 'Section', 'Extra', 'Source')],
    templates=[{'name': 'Cloze',
                'qfmt': '<div class="title">{{Section}}</div><div class="panel">{{cloze:Text}}</div>',
                'afmt': '<div class="title">{{Section}}</div><div class="panel">{{cloze:Text}}</div>'
                        '{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}<div class="source">{{Source}}</div>'}],
    css=CLOZE_CSS, model_type=genanki.Model.CLOZE, sort_field_index=0)

# ---------------------------------------------------------------- multiple choice
MCQ_CSS = BASE_CSS + """
.opts { margin: 12px 0 0; padding: 0; list-style: none; }
.opts li { padding: 8px 12px; margin: 6px 0; border-radius: 8px; background: #f0f0f3; }
.key { margin-top: 14px; font-weight: 700; color: #0b6bcb; }
.nightMode .opts li, .night_mode .opts li { background: #3a3a3c; }
.nightMode .key, .night_mode .key { color: #5eaeff; }
"""
MCQ_MODEL = genanki.Model(
    MCQ_MODEL_ID, 'NBDHE MCQ',
    fields=[{'name': n} for n in ('Question', 'Options', 'Answer', 'Explanation', 'Section', 'Source')],
    templates=[{'name': 'MCQ',
                'qfmt': '<div class="title">{{Section}}</div><div class="panel">{{Question}}<ul class="opts">{{Options}}</ul></div>',
                'afmt': '<div class="title">{{Section}}</div><div class="panel">{{Question}}<ul class="opts">{{Options}}</ul>'
                        '<div class="key">{{Answer}}</div></div>'
                        '{{#Explanation}}<div class="extra">{{Explanation}}</div>{{/Explanation}}<div class="source">{{Source}}</div>'}],
    css=MCQ_CSS, sort_field_index=0)

# ---------------------------------------------------------------- cover fitting
def tight_box(page, box, fit='bg', slack=10):
    """Fit a cover to a label.
    fit='bg'  : EXACTLY the label's pale-blue (or yellow) background — mask that colour inside
                box+slack, 3x3 closing (bigger bridges to neighbours), fill holes, largest blob.
    fit='text': plain-text label (no coloured background) — near-black pixels (max channel <100)
                strictly inside the given box (no slack), +4 px.
    fit='none': use the box as given."""
    import numpy as np
    from scipy import ndimage as nd
    if fit == 'none':
        return box
    if fit == 'rtext':
        return rotated_text_box(page, box)
    if fit == 'rbg':
        return rotated_bg_box(page, box, slack)
    if fit == 'text':
        x0, y0, x1, y1 = box
        a = np.asarray(page.crop((x0, y0, x1, y1)).convert('RGB')).max(axis=2)
        ys, xs = np.nonzero(a < 100)
        if len(xs) < 10:
            return box
        return [x0 + xs.min() - 4, y0 + ys.min() - 4, x0 + xs.max() + 5, y0 + ys.max() + 5]
    x0, y0, x1, y1 = box[0] - slack, box[1] - slack, box[2] + slack, box[3] + slack
    a = np.asarray(page.crop((x0, y0, x1, y1)).convert('RGB')).astype(int)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    m = ((R > 180) & (R < 232) & (G > 232) & (B > 238)) | ((R > 240) & (G > 225) & (B < 170))
    m = nd.binary_closing(m, structure=np.ones((3, 3)))   # small: must not bridge to neighbour labels/arrows
    m = nd.binary_fill_holes(m)
    lab, n = nd.label(m)
    if n == 0:
        return box
    sizes = nd.sum(m, lab, range(1, n + 1)); k = int(np.argmax(sizes)) + 1
    ys, xs = np.nonzero(lab == k)
    return [x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1]

def rotated_text_box(page, box, pad=5):
    """Slanted label: fit a ROTATED rectangle to the near-black text inside `box` (PCA of the
    text pixels gives the angle). Returns [x0,y0,x1,y1, angle_deg]: the UNROTATED rectangle
    (centred on the text) plus the angle to rotate it about its centre."""
    import numpy as np, math
    x0, y0, x1, y1 = box
    rgb = np.asarray(page.crop((x0, y0, x1, y1)).convert('RGB')).astype(int)
    # label text = dark AND not reddish (illustration shading is dark red/brown)
    a = (rgb.max(axis=2) < 85) & (rgb[..., 0] - rgb[..., 2] < 40)
    ys, xs = np.nonzero(a)
    pts = np.stack([xs, ys], 1).astype(float)
    c = np.median(pts, 0); u, sv, vt = np.linalg.svd(pts - c, full_matrices=False)
    ax = vt[0]; ang = math.degrees(math.atan2(ax[1], ax[0]))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    r = math.radians(ang); R = np.array([[math.cos(r), math.sin(r)], [-math.sin(r), math.cos(r)]])
    q = (pts - c) @ R.T
    # trim strays: gently along the text (keep first/last letters), hard across it (text height)
    lo = np.array([np.percentile(q[:, 0], 0.5), np.percentile(q[:, 1], 4)]) - pad
    hi = np.array([np.percentile(q[:, 0], 99.5), np.percentile(q[:, 1], 96)]) + pad
    mid = c + ((lo + hi) / 2) @ R            # rect centre back in crop coords
    w, h = hi - lo
    cx, cy = x0 + mid[0], y0 + mid[1]
    return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, ang]

def _pca_rect(pts, x0, y0, pad, along=(0.5, 99.5), across=(0.5, 99.5)):
    import numpy as np, math
    c = np.median(pts, 0); _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    ang = math.degrees(math.atan2(vt[0][1], vt[0][0]))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    r = math.radians(ang); R = np.array([[math.cos(r), math.sin(r)], [-math.sin(r), math.cos(r)]])
    q = (pts - c) @ R.T
    lo = np.array([np.percentile(q[:, 0], along[0]), np.percentile(q[:, 1], across[0])]) - pad
    hi = np.array([np.percentile(q[:, 0], along[1]), np.percentile(q[:, 1], across[1])]) + pad
    mid = c + ((lo + hi) / 2) @ R; w, h = hi - lo
    cx, cy = x0 + mid[0], y0 + mid[1]
    return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, ang]

def rotated_bg_box(page, box, slack=10):
    """Slanted label on a pale-blue/yellow background: rotated rectangle fitted to the
    background blob (same colour mask as fit='bg'), so it covers exactly the label."""
    import numpy as np
    from scipy import ndimage as nd
    x0, y0, x1, y1 = box[0] - slack, box[1] - slack, box[2] + slack, box[3] + slack
    a = np.asarray(page.crop((x0, y0, x1, y1)).convert('RGB')).astype(int)
    R_, G, B = a[..., 0], a[..., 1], a[..., 2]
    m = ((R_ > 180) & (R_ < 232) & (G > 232) & (B > 238)) | ((R_ > 230) & (G > 200) & (B < 170))
    m = nd.binary_fill_holes(nd.binary_closing(m, structure=np.ones((3, 3))))
    lab, n = nd.label(m)
    if n == 0:
        return box
    k = int(np.argmax(nd.sum(m, lab, range(1, n + 1)))) + 1
    ys, xs = np.nonzero(lab == k)
    return _pca_rect(np.stack([xs, ys], 1).astype(float), x0, y0, pad=1)

def covers(spec, page):
    """[(label dict, [x0,y0,x1,y1] fitted cover in PAGE coords)] for a diagram spec."""
    return [(l, tight_box(page, l['box'], l.get('fit', 'bg'))) for l in spec['labels']]

# ---------------------------------------------------------------- notes
def media_for(spec, pdf):
    MEDIA.mkdir(parents=True, exist_ok=True)
    out = MEDIA / f"{spec['name']}.jpg"
    page = Image.open(render(pdf, spec['pdf_page'])).convert('RGB')
    im = page.crop(spec['crop'])
    w = min(WIDTH, im.width * 2)
    im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(out, 'JPEG', quality=88, optimize=True)
    return out

def io_notes(spec, pdf, page0):
    cx0, cy0, cx1, cy1 = spec['crop']; w, h = cx1 - cx0, cy1 - cy0
    page = Image.open(render(pdf, spec['pdf_page'])).convert('RGB')
    bp = spec.get('page', page0 + spec['pdf_page'])          # book page (Dental Anatomy: pdf+200)
    src = f"StudentRDH {pdf} p.{bp}"
    for l, b in covers(spec, page):
        rot = b[4] if len(b) > 4 else 0
        x0, y0 = b[0] - cx0 - PAD, b[1] - cy0 - PAD
        bw, bh = b[2] - b[0] + 2 * PAD, b[3] - b[1] + 2 * PAD
        yield genanki.Note(
            model=IO_MODEL,
            fields=[l['answer'], f'<img src="{spec["name"]}.jpg">', spec['title'],
                    f'{100*x0/w:.2f}', f'{100*y0/h:.2f}', f'{100*bw/w:.2f}', f'{100*bh/h:.2f}',
                    l.get('extra', ''), src, f'{rot:.1f}'],
            guid=genanki.guid_for('nbdhe-io', spec['name'], l.get('key', l['answer'])),   # 'key' disambiguates repeated labels
            tags=[pdf.lower(), f"p{bp}", 'image-occlusion'])

def cloze_note(c, pdf):
    return genanki.Note(model=CLOZE_MODEL, fields=[c['text'], c.get('section', ''), c.get('extra', ''),
                        f"StudentRDH {pdf} p.{c['page']}"],
                        guid=genanki.guid_for('nbdhe-cloze', c['id']),
                        tags=[pdf.lower(), f"p{c['page']}", 'cloze'])

def mcq_note(q, pdf):
    opts = ''.join(f'<li>{o}</li>' for o in q['options'])
    return genanki.Note(model=MCQ_MODEL, fields=[q['question'], opts, q['answer'], q.get('explanation', ''),
                        q.get('section', ''), f"StudentRDH {pdf} p.{q['page']}"],
                        guid=genanki.guid_for('nbdhe-mcq', q['id']),
                        tags=[pdf.lower(), f"p{q['page']}", 'quiz'])

def load(book):
    specs = {'diagrams': [], 'cloze': [], 'mcq': []}
    for f in sorted(glob.glob(str(ROOT / '.tools' / 'anki' / book / '*.json'))):
        d = json.load(open(f))
        for k in specs:
            specs[k] += d.get(k, [])
    return specs

if __name__ == '__main__':
    out = sys.argv[1]; book = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'anatomy'
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
    cfg = BOOKS[book]; specs = load(book)
    decks, media, counts = {}, [], {'io': 0, 'cloze': 0, 'mcq': 0}
    def deck(sub):
        name = f"{ROOT_DECK}::{cfg['deck']}::{sub}"
        if name not in decks:
            decks[name] = genanki.Deck(deck_id(name), name)
        return decks[name]
    for s in specs['diagrams']:
        if only and s['name'] not in only:
            continue
        media.append(str(media_for(s, cfg['pdf'])))
        for n in io_notes(s, cfg['pdf'], cfg['page0']):
            deck(s['deck']).add_note(n); counts['io'] += 1
    if not only:
        for c in specs['cloze']:
            deck(c['deck']).add_note(cloze_note(c, cfg['pdf'])); counts['cloze'] += 1
        for q in specs['mcq']:
            deck(q['deck']).add_note(mcq_note(q, cfg['pdf'])); counts['mcq'] += 1
    ids = [n.guid for d in decks.values() for n in d.notes]
    assert len(ids) == len(set(ids)), 'duplicate note GUIDs — two notes share a diagram+answer or an id'
    genanki.Package(list(decks.values()), media_files=media).write_to_file(out)
    print(f"{out}: {counts} in {len(decks)} decks, {len(media)} images")
