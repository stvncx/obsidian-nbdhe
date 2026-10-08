"""Import an .apkg into a throwaway collection with Anki's REAL importer and report what
landed: notes, cards, and which referenced media files actually exist after import.
Usage: .tools/.venv/bin/python .tools/anki/test_import.py deck.apkg"""
import sys, tempfile, os, re
from anki.collection import Collection, ImportAnkiPackageRequest, ImportAnkiPackageOptions
d = tempfile.mkdtemp(); col = Collection(os.path.join(d, 'collection.anki2'))
col.import_anki_package(ImportAnkiPackageRequest(package_path=os.path.abspath(sys.argv[1]), options=ImportAnkiPackageOptions(with_scheduling=True)))
mdir = col.media.dir(); have = set(os.listdir(mdir))
print('notes', col.note_count(), 'cards', col.card_count(), 'media in collection:', sorted(have))
for cid in col.find_cards('')[:1]:
    c = col.get_card(cid); html = c.question()
    srcs = re.findall(r'src="([^"]+)"', html)
    print('front img src:', srcs, '-> present' if all(s in have for s in srcs) and srcs else '-> MISSING')
col.close()

def screenshot(apkg, out_png, width=390, n=2):
    """Render the first n cards (front+back) exactly as Anki generates them, from the imported
    collection's media folder, with Playwright."""
    from playwright.sync_api import sync_playwright
    d = tempfile.mkdtemp(); col = Collection(os.path.join(d, 'collection.anki2'))
    col.import_anki_package(ImportAnkiPackageRequest(package_path=os.path.abspath(apkg), options=ImportAnkiPackageOptions(with_scheduling=True)))
    parts = []
    for cid in col.find_cards('')[:n]:
        c = col.get_card(cid); css = c.note_type()['css']
        parts += [c.question(), c.answer()]
    html = f"<html><head><style>{css}</style></head><body class='card'>" + '<hr>'.join(parts) + '</body></html>'
    page_path = os.path.join(col.media.dir(), '_preview.html'); open(page_path, 'w').write(html)
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={'width': width, 'height': 900})
        pg.goto('file://' + page_path); pg.wait_for_timeout(300); pg.screenshot(path=out_png, full_page=True); br.close()
    col.close()

if len(sys.argv) > 2:
    screenshot(sys.argv[1], sys.argv[2])
