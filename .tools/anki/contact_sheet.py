"""Render EVERY card's front (as Anki generates it after a real import) into one contact
sheet PNG, to eyeball that each cover hides its whole label and nothing else.
Usage: .tools/.venv/bin/python .tools/anki/contact_sheet.py deck.apkg out.png [width] [side]
side = q (fronts, default) or a (backs)"""
import os, sys, tempfile
from anki.collection import Collection, ImportAnkiPackageRequest, ImportAnkiPackageOptions
from playwright.sync_api import sync_playwright
from PIL import Image
apkg, out = sys.argv[1], sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 600
side = sys.argv[4] if len(sys.argv) > 4 else 'q'
d = tempfile.mkdtemp(); col = Collection(os.path.join(d, 'c.anki2'))
col.import_anki_package(ImportAnkiPackageRequest(package_path=os.path.abspath(apkg), options=ImportAnkiPackageOptions(with_scheduling=True)))
shots = []
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': width, 'height': 400})
    for i, cid in enumerate(col.find_cards('')):
        c = col.get_card(cid); html = c.question() if side == 'q' else c.answer()
        f = os.path.join(col.media.dir(), f'_c{i}.html')
        open(f, 'w').write(f"<html><head><style>{c.note_type()['css']}</style></head><body class='card'>{html}</body></html>")
        pg.goto('file://' + f); pg.wait_for_timeout(150)
        png = os.path.join(d, f'{i}.png'); pg.screenshot(path=png, full_page=True); shots.append(png)
    br.close()
ims = [Image.open(s) for s in shots]; cols = 3
cw = max(i.width for i in ims); ch = max(i.height for i in ims); rows = -(-len(ims) // cols)
sheet = Image.new('RGB', (cw * cols, ch * rows), 'white')
for k, im in enumerate(ims): sheet.paste(im, ((k % cols) * cw, (k // cols) * ch))
sheet.save(out); print(out, len(ims), 'cards')
