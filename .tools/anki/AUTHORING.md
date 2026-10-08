# Authoring spec files — NBDHE Anki decks

You are turning pages of a scanned review book (StudentRDH NBDHE guide) into Anki cards for a
dental-hygiene student sitting the NBDHE ~January 2027. Steven (an experienced adult educator)
leads the learning design; follow these rules exactly.

## Inputs
- Rendered pages (200 dpi, 1700×2200 px): `.tools/cache/<Book>-NNN.png` (NNN = PDF page, 3 digits).
  View a page or a zoomed crop with the Read tool. Make zoomed crops with PIL into your own
  scratch dir — never write inside `.tools/` except your one spec file.
- Book pages (use these in every `page` field and in ids/names): Anatomy.pdf has TWO chapters —
  Head & Neck: book page = PDF page + 146 (PDF 2 → 148 … PDF 30 → 176);
  Dental Anatomy: book page = PDF page + 200 (PDF 34 → 234 … PDF 49 → 249).
  The printed page number in the page corner is the truth — check it.
- Label-box detector: `.tools/.venv/bin/python -c "import sys; sys.path.insert(0,'.tools'); from detect import boxes; print(boxes('.tools/cache/Anatomy-006.png'))"`
  → (colour, x0, y0, x1, y1) of pale-cyan/yellow label boxes. It MISSES some and merges some.

## Output: ONE file `.tools/anki/anatomy/pNNN-NNN.json` (book pages) — write nothing else
```json
{"diagrams": [...], "cloze": [...], "mcq": [...]}
```

### Image occlusion — every labeled figure
```json
{"name": "anat-p152-temporal-bone", "title": "Temporal and zygomatic bones", "deck": "Head and Neck",
 "pdf_page": 6, "page": 152, "crop": [x0, y0, x1, y1],
 "labels": [{"box": [x0, y0, x1, y1], "answer": "Zygomatic process", "fit": "bg"}, ...]}
```
- `name`: `anat-p<bookpage>-<slug>`, unique. `deck`: "Head and Neck" or "Dental Anatomy".
- `crop`: the whole figure incl. all its labels, little else (page px).
- One label entry per label on the figure, in reading order. `answer` = the label text
  exactly as printed (fix obvious typos; spell out nothing extra).
- `fit`: `"bg"` if the label sits on a pale-blue/yellow box (cover snaps to that box — the
  rough `box` may be a bit loose, ±10 px); `"text"` for plain text labels with no coloured box
  (cover snaps to the near-black text strictly INSIDE `box` — so `box` must contain the whole
  label text and NO leader lines/arrows/other text); `"none"` = use `box` exactly (coloured
  labels other than pale blue/yellow, e.g. green/red/white-on-colour).
- If the same label text appears twice on one figure, add `"key": "<text> (2)"` to the second.
- Skip figures with no labels (photos without callouts) and pure decoration.
- **Verify every figure**: `.tools/.venv/bin/python .tools/anki/diagram_check.py <yourfile> <scratchdir>`
  then Read each `<scratchdir>/<name>.png`. Every orange cover must hide its whole label and
  nothing else (no neighbour text, no anatomy). Fix boxes/fit and re-run until all are right.

### Cloze — all the text content
```json
{"id": "anat-p152-007", "deck": "Head and Neck", "section": "Temporal bone", "page": 152,
 "text": "The {{c1::mastoid process}} is the attachment for the {{c2::sternocleidomastoid}} muscle.",
 "extra": "Tip from the book or one line of context (optional)"}
```
- Cover EVERY fact on the page: bullets, definitions, table rows, "Tip"/"WakeUpMemory"/
  "Board Alert"/"Don't be confused" boxes (those usually go in `extra` of the related card,
  or become their own card if they state a testable fact; mnemonics go in `extra`).
- **Minimum information**: each cloze deletion tests ONE fact. Delete the key term or the key
  attribute (number, location, function, nerve, drains-to…), never filler words.
- Several clozes per note (c1, c2, c3 → separate cards) only for facts that belong in one
  sentence; max ~4. Use `{{c1::x}}` … `{{c1::y}}` (same number) only when two blanks must be
  recalled together.
- The sentence must make the answer unambiguous — include enough context (e.g. "On the
  lateral skull, the {{c1::coronoid process}} is the anterior process of the mandibular ramus").
- Tables: one note per row (or per key cell), stating the row as a sentence.
- Hints are allowed when a blank could have several right answers: `{{c1::masseter::muscle}}`.
- `id`: `anat-p<bookpage>-NNN`, unique, never reused. Keep plain text; `<b>`, `<i>`, `<br>`,
  `<ul><li>` allowed. No markdown.
- Fix typos. If the book conflicts with current exam standards (2021 AHA antibiotic
  prophylaxis, 2020 ASA, 2020 IADT, 2017 AAP perio classification, 2017 AHA BP, no film/
  darkroom, smoking in cigarettes/day) follow the standard and say so in `extra`.
- Skip: page furniture (headers, © lines, page numbers, "Progress made / To do next",
  "Thoughts", "Practice questions — see your dashboard").

### MCQ — the book's bonus-quiz questions only
```json
{"id": "anat-quiz-hn-01", "deck": "Quizzes", "section": "Head & Neck bonus quiz", "page": 175,
 "question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
 "answer": "C. ...", "explanation": "from the book's answer key (it is printed upside down on the next page — rotate the image 180° to read it)"}
```

## Before you finish
- `python3 -m json.tool <yourfile> > /dev/null` passes; ids/names unique.
- Every diagram checked visually (see above). Report: counts (diagrams / labels / cloze /
  mcq), any figure you skipped and why, anything you were unsure of.
