"""Build the NBDHE Anki deck (.apkg) — image-occlusion cards, one label per card, answer
revealed in place on the image.

Custom note type "NBDHE Image Occlusion" (own HTML/CSS — renders the same on Anki desktop,
AnkiMobile, AnkiDroid). The back template does NOT include {{FrontSide}}: it redraws the
same image with the same box, now showing the term, so the reveal is in place.

IDs are fixed (model, deck) and note GUIDs derive from diagram name + label text, so
re-importing an updated deck UPDATES the notes and keeps the student's review history.
NEVER change MODEL_ID / DECK_ID / the guid recipe.

Usage: .tools/.venv/bin/python .tools/anki/build_deck.py OUT.apkg anat-oral-cavity anat-gingiva
"""
import json, sys
from pathlib import Path
import genanki
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from occlude import render

ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / '.tools' / 'anatomy-diagrams.json'
MEDIA = ROOT / '.tools' / 'anki' / 'media'
PAD = 4          # px on the 200-dpi page, around each label box
WIDTH = 1400     # px of the media image
MODEL_ID = 1728390001      # fixed forever
DECK_ID = 1728390101       # fixed forever: "NBDHE::Anatomy"
TITLES = {'anat-oral-cavity': 'Landmarks of the oral cavity',
          'anat-gingiva': 'Gingiva and surrounding structures',
          'anat-tongue-papillae': 'Tongue and papillae'}

CSS = """
.card { font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: #f6f5f2; color: #1d1d1f; margin: 0; padding: 12px; text-align: center; }
.io-title { font-size: 15px; font-weight: 600; letter-spacing: .02em; color: #6b6b70;
  margin: 4px 0 10px; text-transform: uppercase; }
.io { container-type: inline-size; position: relative; display: inline-block; width: 100%;
  max-width: 1000px; line-height: 0; border-radius: 10px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,.12), 0 6px 20px rgba(0,0,0,.06); }
.io img { width: 100%; height: auto; display: block; max-width: none; max-height: none; }
.io-box { position: absolute; display: flex; align-items: center; justify-content: center;
  box-sizing: border-box; border-radius: 6px; padding: 0 .35em; line-height: 1.1;
  font-size: 2.5cqw; font-weight: 700; text-align: center; white-space: normal; }
.io-box.ask { background: #e8781e; color: #fff; border: 2px solid #b85a0e; font-size: 3.6cqw; }
.io-box.show { background: #fff; color: #0b6bcb; border: 2px solid #0b6bcb;
  box-shadow: 0 0 0 4px rgba(11,107,203,.25); }
.io-extra { max-width: 1000px; margin: 12px auto 0; font-size: 16px; line-height: 1.45;
  text-align: left; color: #3a3a3c; }
.nightMode.card, .night_mode .card { background: #1c1c1e; color: #f2f2f7; }
.nightMode .io-title, .night_mode .io-title { color: #a1a1a6; }
.nightMode .io-extra, .night_mode .io-extra { color: #d1d1d6; }
"""

BOX = 'left:{{Left}}%;top:{{Top}}%;width:{{Width}}%;height:{{Height}}%'
FRONT = f"""<div class="io-title">{{{{Title}}}}</div>
<div class="io">{{{{Image}}}}<div class="io-box ask" style="{BOX}">?</div></div>"""
BACK = f"""<div class="io-title">{{{{Title}}}}</div>
<div class="io">{{{{Image}}}}<div class="io-box show" style="{BOX}">{{{{Answer}}}}</div></div>
{{{{#Extra}}}}<div class="io-extra">{{{{Extra}}}}</div>{{{{/Extra}}}}"""

MODEL = genanki.Model(
    MODEL_ID, 'NBDHE Image Occlusion',
    fields=[{'name': n} for n in ('Answer', 'Image', 'Title', 'Left', 'Top', 'Width', 'Height', 'Extra', 'Source')],
    templates=[{'name': 'Occlusion', 'qfmt': FRONT, 'afmt': BACK}],
    css=CSS, sort_field_index=0)

def media_for(spec):
    MEDIA.mkdir(parents=True, exist_ok=True)
    out = MEDIA / f"{spec['name']}.jpg"
    page = Image.open(render(spec['pdf'], spec['pdf_page'])).convert('RGB')
    im = page.crop(spec['crop'])
    im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS).save(out, 'JPEG', quality=88, optimize=True)
    return out

def notes_for(spec, book_page):
    cx0, cy0, cx1, cy1 = spec['crop']; w, h = cx1 - cx0, cy1 - cy0
    for box, answer in spec['labels']:
        x0, y0 = box[0] - cx0 - PAD, box[1] - cy0 - PAD
        bw, bh = box[2] - box[0] + 2 * PAD, box[3] - box[1] + 2 * PAD
        yield genanki.Note(
            model=MODEL,
            fields=[answer, f"<img src=\"{spec['name']}.jpg\">", TITLES[spec['name']],
                    f'{100*x0/w:.2f}', f'{100*y0/h:.2f}', f'{100*bw/w:.2f}', f'{100*bh/h:.2f}',
                    '', f'StudentRDH Anatomy p.{book_page}'],
            guid=genanki.guid_for('nbdhe-io', spec['name'], answer),
            tags=['anatomy', f'p{book_page}', spec['name']])

if __name__ == '__main__':
    out, names = sys.argv[1], sys.argv[2:]
    specs = {s['name']: s for s in json.load(open(SPECS))}
    deck = genanki.Deck(DECK_ID, 'NBDHE::Anatomy')
    media = []
    for n in names:
        s = specs[n]
        media.append(str(media_for(s)))
        for note in notes_for(s, 146 + s['pdf_page']):   # Anatomy PDF p.1 = book p.147
            deck.add_note(note)
    genanki.Package(deck, media_files=media).write_to_file(out)
    print(f'{out}: {len(deck.notes)} notes, {len(media)} images')
