"""Validate one spec file against the authoring rules (schema, ids, sizes, cloze syntax).
Usage: .tools/.venv/bin/python .tools/anki/validate_spec.py .tools/anki/anatomy/pNNN-NNN.json"""
import json, re, sys, glob, collections
f = sys.argv[1]; d = json.load(open(f)); errs = []; warn = []
DECKS = {'Head and Neck', 'Dental Anatomy', 'Quizzes'}
def need(o, keys, where):
    for k in keys:
        if k not in o or o[k] in ('', None, []): errs.append(f'{where}: missing {k}')
    if 'deck' in o and o['deck'] not in DECKS: errs.append(f"{where}: bad deck {o['deck']!r}")
for c in d.get('cloze', []):
    w = f"cloze {c.get('id')}"; need(c, ['id', 'deck', 'page', 'text'], w)
    t = c.get('text', '')
    if not re.search(r'\{\{c\d+::.+?\}\}', t): errs.append(f'{w}: no cloze')
    if t.count('{{') != t.count('}}'): errs.append(f'{w}: unbalanced braces')
    if len(set(re.findall(r'\{\{c(\d+)::', t))) > 5: warn.append(f'{w}: >5 deletions')
for q in d.get('basic', []):
    need(q, ['id', 'deck', 'page', 'front', 'back'], f"basic {q.get('id')}")
for q in d.get('typein', []):
    w = f"typein {q.get('id')}"; need(q, ['id', 'deck', 'page', 'question', 'answer'], w)
    if len(str(q.get('answer', ''))) > 25: warn.append(f'{w}: long typed answer {q["answer"]!r}')
for q in d.get('match', []):
    w = f"match {q.get('id')}"; need(q, ['id', 'deck', 'page', 'prompt', 'pairs'], w)
    P = q.get('pairs', [])
    if not 3 <= len(P) <= 7: errs.append(f'{w}: {len(P)} pairs (want 3–7)')
    if any(len(p) != 2 for p in P): errs.append(f'{w}: pair not [left,right]')
    if len({p[1] for p in P}) != len(P): errs.append(f'{w}: duplicate right-hand answers')
for q in d.get('order', []):
    w = f"order {q.get('id')}"; need(q, ['id', 'deck', 'page', 'prompt', 'items'], w)
    if not 3 <= len(q.get('items', [])) <= 12: errs.append(f'{w}: {len(q.get("items", []))} items (want 3–12)')
    if len(set(q.get('items', []))) != len(q.get('items', [])): errs.append(f'{w}: duplicate items')
for q in d.get('sort', []):
    w = f"sort {q.get('id')}"; need(q, ['id', 'deck', 'page', 'prompt', 'categories'], w)
    C = q.get('categories', []); items = [i for c in C for i in c[1]]
    if not 2 <= len(C) <= 4: errs.append(f'{w}: {len(C)} categories (want 2–4)')
    if not 4 <= len(items) <= 16: errs.append(f'{w}: {len(items)} items (want 4–16)')
    if len(set(items)) != len(items): errs.append(f'{w}: an item appears twice')
for q in d.get('mcq', []):
    w = f"mcq {q.get('id')}"; need(q, ['id', 'deck', 'page', 'question', 'options', 'answer'], w)
    if len(q.get('options', [])) != 4: errs.append(f'{w}: needs 4 options')
    if q.get('answer') not in q.get('options', []): errs.append(f'{w}: answer must equal one option exactly')
for g in d.get('diagrams', []):
    need(g, ['name', 'title', 'deck', 'pdf_page', 'crop', 'labels'], f"diagram {g.get('name')}")
# ids unique across ALL spec files of the book
allids = collections.Counter()
for ff in glob.glob(f.rsplit('/', 1)[0] + '/*.json'):
    dd = json.load(open(ff))
    for k in ('cloze', 'basic', 'typein', 'match', 'order', 'sort', 'mcq'):
        allids.update(x.get('id') for x in dd.get(k, []))
    allids.update(g.get('name') for g in dd.get('diagrams', []))
dups = [i for i, n in allids.items() if n > 1]
if dups: errs.append(f'duplicate ids across book: {dups[:10]}')
counts = {k: len(d.get(k, [])) for k in ('diagrams', 'cloze', 'basic', 'typein', 'match', 'order', 'sort', 'mcq')}
print('counts', counts)
for w in warn: print('WARN', w)
for e in errs: print('ERROR', e)
print('OK' if not errs else f'{len(errs)} errors'); sys.exit(1 if errs else 0)
