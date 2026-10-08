"""Exercise the interactive card types (match/order/sort/label) as a user would, on the
cards Anki generates after a REAL import: tap answers (all right except one deliberate
mistake), press Check, assert the score text, screenshot front-after-check + back.
Usage: .tools/.venv/bin/python .tools/anki/interact_test.py deck.apkg OUTDIR [max_per_type]"""
import os, sys, tempfile, json, re
from anki.collection import Collection, ImportAnkiPackageRequest, ImportAnkiPackageOptions
from playwright.sync_api import sync_playwright
apkg, outdir = sys.argv[1], sys.argv[2]; nmax = int(sys.argv[3]) if len(sys.argv) > 3 else 1
os.makedirs(outdir, exist_ok=True)
d = tempfile.mkdtemp(); col = Collection(os.path.join(d, 'c.anki2'))
col.import_anki_package(ImportAnkiPackageRequest(package_path=os.path.abspath(apkg), options=ImportAnkiPackageOptions(with_scheduling=True)))
def page_for(pg, c, side):
    f = os.path.join(col.media.dir(), f'_{c.id}_{side}.html')
    open(f, 'w').write(f"<html><head><meta name=viewport content='width=device-width'><style>{c.note_type()['css']}</style></head>"
                       f"<body class='card'>{c.question() if side == 'q' else c.answer()}</body></html>")
    pg.goto('file://' + f); pg.wait_for_timeout(150)
def chip(pg, text, scope=''):
    return pg.locator(f'{scope} .chip', has_text=re.compile('^(\\d+)?' + re.escape(text) + '$')).first
results = []
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, device_scale_factor=2)
    errors = []; pg.on('pageerror', lambda e: errors.append(str(e)))
    for kind, model in (('match', 'NBDHE Matching'), ('order', 'NBDHE Ordering'), ('sort', 'NBDHE Sorting'), ('label', 'NBDHE Label Diagram')):
        for cid in col.find_cards(f'note:"{model}"')[:nmax]:
            c = col.get_card(cid); data = json.loads(re.search(r'class="nb-data">(.*?)</script>', c.question(), re.S).group(1))
            page_for(pg, c, 'q')
            if kind == 'match':
                P = data['pairs']; n = len(P)
                for i, (l, r) in enumerate(P):
                    rr = P[(i + 1) % n][1] if i == 0 else r          # first pair deliberately wrong
                    pg.locator('.cols > div').nth(0).locator('.chip').nth(i).tap()
                    pg.locator('.cols > div').nth(1).locator('.chip', has_text=rr).first.tap()
                expect = n - 1     # pair 0 wrong; pair 1 then reclaims its answer, leaving pair 0 unmatched
            elif kind == 'order':
                items = data['items']; n = len(items)
                for target in range(n):                       # selection-sort by tapping swaps
                    texts = [t.split(None, 0)[0] for t in pg.locator('.olist .chip').all_inner_texts()]
                    cur = [re.sub(r'^\d+\s*', '', t) for t in texts]
                    j = cur.index(items[target])
                    if j != target:
                        pg.locator('.olist .chip').nth(target).tap(); pg.locator('.olist .chip').nth(j).tap()
                if n > 1:                                         # one deliberate swap = 2 wrong
                    pg.locator('.olist .chip').nth(0).tap(); pg.locator('.olist .chip').nth(1).tap()
                expect = n - 2
            elif kind == 'sort':
                cats = data['cats']; n = sum(len(x[1]) for x in cats); first = True
                for ci, (cname, items) in enumerate(cats):
                    for t in items:
                        dest = (ci + 1) % len(cats) if first else ci; first = False
                        pg.locator('.pool .chip', has_text=t).first.tap()
                        pg.locator('.bin').nth(dest).locator('h4').tap()
                expect = n - 1
            else:
                S = data['slots']; n = len(S)
                for i, s in enumerate(S):
                    if i == 0: continue                               # leave slot 0 empty
                    pg.locator('.tray .chip:not(.used)', has_text=s['a']).first.tap(); pg.locator('.slot').nth(i).tap()
                expect = n - 1
            pg.locator('.nb-check').tap(); pg.wait_for_timeout(100)
            score = pg.locator('.nb-score').inner_text()
            got = int(score.split('/')[0])
            results.append((kind, c.note()['Prompt'] if 'Prompt' in c.note() else c.note()['Title'], score, 'OK' if got == expect else f'EXPECTED {expect}'))
            pg.screenshot(path=f'{outdir}/{kind}-{cid}-front.png', full_page=True)
            page_for(pg, c, 'a'); pg.screenshot(path=f'{outdir}/{kind}-{cid}-back.png', full_page=True)
    br.close()
for r in results: print(' | '.join(map(str, r)))
print('JS errors:', errors or 'none')
