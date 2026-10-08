# Obsidian vault — NBDHE / RDH study

**Runbook: `.claude/RUNBOOK.md` — record every new procedure and decision there as we work.**

This directory IS Steven's Obsidian vault (repo `stvncx/obsidian-nbdhe`, branch `main`).
The **student is a woman who shares this vault with Steven** (name not given — don't guess;
she/her). She sits the NBDHE (dental hygiene boards) **~January 2027** and studies from the
StudentRDH review guide. Steven runs the project (setup, sync, working with Claude). Cards are
reviewed with the **Spaced Repetition** community plugin (v1.15.x) in Obsidian (Mac, iPhone, iPad).

**Scope = the UPDATED NBDHE test specifications (implemented 2026-11-01)** in
`.source/official/candidate_guide_2026.txt` ("After Update", pp. 8–10). Question style =
`.source/official/sample_questions.txt`. Where the book conflicts with the exam's adopted
standards (`exam_updates.txt`: AHA 2021 antibiotic prophylaxis, ASA 2020, IADT 2020, AAP 2017
perio classification, AHA 2017 BP, no film/darkroom, smoking = cigs/day, 1 pack = 20), **the
exam's standard wins** — note the correction on the card. Open this project with `app obsidian`.

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

## Image cards

v3 in-place image occlusion — see RUNBOOK §5 (mechanism, procedure, verification).

## Status / open questions (keep updated)

- 2026-10-07: sample = Anatomy section 01 (book pp. 148–150) + 3 image diagrams.
  Steven's verdict: "the cards kind of suck" — **reason not yet pinned down**. Candidates:
  shallow (definitions, not NBDHE-style application), messy note, trivia, repetitive image
  cards. Ask before mass-producing more.
- He considered Anki / a custom web app; as of 2026-10-08 he chose to stay in Obsidian.
- 2026-10-08: ALL text cards deleted at Steven's request; Anatomy 01 now = 17 image cards for the
  two p.148 diagrams only. Get images right first, then rescope.
- 2026-10-08: Mac sync live (`vault-sync`, see RUNBOOK §2–3); first Mac sync 52b1fbb.
