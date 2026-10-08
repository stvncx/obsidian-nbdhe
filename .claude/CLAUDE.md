# Obsidian vault — NBDHE / RDH study

**Runbook: `.claude/RUNBOOK.md` — record every new procedure and decision there as we work.**

This directory IS Steven's Obsidian vault (repo `stvncx/obsidian-nbdhe`, branch `main`).
He studies for the NBDHE (dental hygiene boards) from the StudentRDH review guide and
reviews cards with the **Spaced Repetition** community plugin (v1.15.x) in Obsidian on his
MacBook, iPhone and iPad. Open this project with `app obsidian`.

## Layout

| Path | What | Synced to vault? |
|---|---|---|
| `Flashcards/<Book>/NN Section.md` | one note per book section | yes |
| `Flashcards/<Book>/images/` | diagram images for image cards | yes |
| `.obsidian/` | his Obsidian settings + plugins (he commits these from the Mac) | yes — don't edit unless asked |
| `.claude/`, `.tools/` | this file + card-building scripts (Obsidian hides dot-folders) | yes, but invisible in Obsidian |
| `.source/RDH/*.pdf` | the 16 book PDFs (copy of `~/exchange/to-claude/RDH/`) | **no** — gitignored, server only |
| `.tools/.venv/`, `.tools/cache/` | Python env (pillow, numpy, scipy) + rendered pages | no — gitignored |

The PDFs are **scans** (copier images, no text layer) — read them with the Read tool's
`pages` parameter. Book pages ≠ PDF pages: Anatomy.pdf p.1 = book p.147.

## Git sync — he edits from the Mac at the same time

- **Always `git pull` before touching anything**, commit small, push right away.
- His Mac pushes "Sync from MacBook-…" commits (settings + review progress).
- The SR plugin writes review state into the notes as `<!--SR:!2026-10-09,3,250-->` after a
  card. **Never drop or rewrite these** — regenerating a note wholesale wipes his progress.
  Edit cards in place; carry the SR comment along with its card.

## Card format (Spaced Repetition plugin, his settings)

- `Q::A` basic · `term:::definition` both directions · `==cloze==` (each highlight = a card)
- multi-line: question lines, `?` line, answer lines; `??` = reversed. No end marker is set —
  a card ends at the next blank line, so **no blank lines inside a card**.
- Deck tag at the top of each note: `#flashcards/rdh/<book>` (e.g. `#flashcards/rdh/anatomy`).
- Frontmatter `source:` gives the book pages the note came from.

## Image cards (labeled diagrams)

`.tools/occlude.py` crops a diagram from a page and covers each label with a numbered
orange box → `<name>-q.png` (question) + `<name>.png` (answer). Specs live in
`.tools/<book>-diagrams.json`; `.tools/detect.py` finds the book's pale-cyan/yellow label
boxes but misses some — **always look at the `-q` image before committing**. Diagrams whose
labels are plain text (no boxes, e.g. body planes, Anatomy p.150) need boxes by hand.

## Status / open questions (keep updated)

- 2026-10-07: sample = Anatomy section 01 (book pp. 148–150) + 3 image diagrams.
  Steven's verdict: "the cards kind of suck" — **reason not yet pinned down**. Candidates:
  shallow (definitions, not NBDHE-style application), messy note, trivia, repetitive image
  cards. Ask before mass-producing more.
- He considered Anki / a custom web app; as of 2026-10-08 he chose to stay in Obsidian.
- 2026-10-08: Mac sync live (`vault-sync`, see RUNBOOK §2–3); first Mac sync 52b1fbb.
