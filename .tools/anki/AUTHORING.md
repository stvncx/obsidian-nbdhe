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
- Slanted labels: `"rbg"` (rotated cover fitted to a slanted pale-blue/yellow label box) or
  `"rtext"` (rotated cover fitted to slanted text on any other background). The cover rotates
  with the label — use these instead of a big straight box.
- If the same label text appears twice on one figure, add `"key": "<text> (2)"` to the second.
- Skip figures the book prints twice (e.g. "14 facial bones" on pp.151 and 154) — one copy only.
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

---

# v2 — the full card-type mix (2026-10-08)

Steven asked for every useful card type, chosen by what is pedagogically best. Defaults below
are Claude's; **Steven leads learning design** and may change them. Principles:
- **Recall is the backbone** (cloze, basic, type-in): producing an answer beats recognising it.
- **Recognition formats are add-ons for a purpose**: matching/sorting train *discrimination*
  between easily-confused items; ordering trains *sequences*; label-diagram trains the *whole
  figure*; MCQ trains the *exam format* (transfer).
- **No fact in more than two places**: at most one atomic card (cloze / basic / type-in /
  occlusion) + at most one integrative card (match / order / sort / label / MCQ).
- Atomic beats compound; a card should be answerable in a few seconds (integrative cards: <1 min).

## Choosing the atomic type for each fact
| Fact looks like | Use | Notes |
|---|---|---|
| term ⇄ short definition, unambiguous BOTH ways | **basic** with `"reverse": true` | e.g. Fossa ⇄ "broad, deep depression in bone". Only if the definition identifies the term uniquely — otherwise cloze. Replaces (delete) the cloze for it. |
| why / how / clinical reasoning ("Why…?", "What happens if…?") | **basic** (no reverse) | answer 1–2 lines; the book's Tips/Board Alerts are the source |
| a number, age, count, code, single short token | **type-in** | answer must be short & exact ("3", "6–7 years", "C2") — give the format in the question if needed ("in years") |
| anything else (most facts) | **cloze** (unchanged) | keep existing ids |

```json
"basic":  [{"id":"anat-p151-b-01","deck":"Head and Neck","section":"Depressions","page":151,
            "front":"Fossa","back":"A broad, deep depression in a bone","reverse":true,"extra":""}],
"typein": [{"id":"anat-p150-t-01","deck":"Head and Neck","section":"Skull","page":150,
            "question":"How many bones form the skull?","answer":"22","extra":"8 cranial + 14 facial"}]
```

## Integrative types (add a FEW per page range — quality over quantity)
| Type | When | Size |
|---|---|---|
| **match** | 3–7 parallel pairs that are commonly confused (nerve⇄function, gland⇄duct, node⇄area drained, muscle⇄action, stain⇄cause) | short items both sides; every right side distinct |
| **order** | a real sequence the exam asks about (CN I–XII, eruption order, drainage pathway, layers, developmental stages) | 3–12 items |
| **sort** | items that fall into 2–4 categories (motor/sensory/both; serous/mucous/mixed; intrinsic/extrinsic stain; cranial/facial bone) | 4–16 items, each in exactly one category |
| **mcq** (exam-style) | 1–3 per *section*: NBDHE-style clinical vignette or "most likely"/"EXCEPT" question, answerable from the book's facts | 4 options, plausible distractors from the same category, `answer` = the exact option text, `explanation` says why the key is right and why the best distractor is wrong |

```json
"match": [{"id":"anat-p172-m-01","deck":"Head and Neck","section":"Salivary glands","page":172,
           "prompt":"Match each gland to its duct.","pairs":[["Parotid","Stensen's duct"],["Submandibular","Wharton's duct"],["Sublingual","Bartholin's & Rivinus' ducts"]]}],
"order": [{"id":"anat-p169-o-01", "...":"...", "prompt":"Put the cranial nerves in order (I → XII).","items":["Olfactory","Optic","..."]}],
"sort":  [{"id":"anat-p169-s-01", "...":"...", "prompt":"Sort the cranial nerves by type.",
           "categories":[["Sensory",["Olfactory","Optic","Vestibulocochlear"]],["Motor",["..."]],["Both",["..."]]]}],
"mcq":   [{"id":"anat-p164-mcq-01","deck":"Head and Neck","section":"Maxillary artery","page":164,
           "question":"A patient develops a rapidly swelling hematoma after a PSA injection. Which structure was most likely punctured?",
           "options":["A. Facial artery","B. Pterygoid venous plexus","C. Lingual vein","D. Inferior alveolar artery"],
           "answer":"B. Pterygoid venous plexus","explanation":"..."}]
```
- Integrative cards may repeat facts that have an atomic card (that is their point) — but not
  facts that already appear in another integrative card.
- Exam-style MCQ go in the topic's deck ("Head and Neck"/"Dental Anatomy"); the book's bonus
  quizzes stay in "Quizzes".

## Diagrams
- Every diagram with ≥3 labels automatically also gets one **label-the-diagram** card (all
  labels in a tray, tap to place) — nothing to author. Set `"label_all": false` on a diagram
  where that would be silly.
- Do NOT occlude reference charts where neighbours give the answer away (e.g. the tooth-numbering
  charts): delete those diagrams and test the content with type-in / match instead.

## Ids
New ids: `anat-p<page>-b-NN` (basic), `-t-NN` (type-in), `-m-NN`, `-o-NN`, `-s-NN`, `-mcq-NN`.
Never reuse an id; keep the ids of cloze notes you leave alone.

## Validate
`.tools/.venv/bin/python .tools/anki/validate_spec.py <yourfile>` must print OK. Do not run
build_deck.py (other authors run in parallel).
