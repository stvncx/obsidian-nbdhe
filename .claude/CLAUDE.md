# nbdhe — NBDHE board-exam study decks (Anki)

**Runbook: `.claude/RUNBOOK.md` — record every new procedure and decision there as we work.**
**Card-authoring rules: `.tools/anki/AUTHORING.md`.**

The **student is a woman Steven is helping** (name not given — don't guess; she/her). She sits
the NBDHE (dental hygiene boards) **~January 2027** and studies from the StudentRDH review
guide (16 scanned PDFs). **Steven leads the learning design** (trained teacher, 25 yrs adult
ed, memory research) — propose, don't impose; his calls are final. Open with `app nbdhe`.

**Cards are built for ANKI** (since 2026-10-08): `.apkg` decks generated from JSON spec files,
delivered via `~/exchange/from-claude/`. Three note types: image occlusion (Steven's design —
one label covered per card, revealed in place), cloze, MCQ (bonus quizzes). See RUNBOOK §6.

**Scope = the UPDATED NBDHE test specifications (implemented 2026-11-01)** in
`.source/official/candidate_guide_2026.txt` ("After Update", pp. 8–10). Where the book conflicts
with the exam's adopted standards (`exam_updates.txt`: AHA 2021 antibiotic prophylaxis, ASA
2020, IADT 2020, AAP 2017 perio classification, AHA 2017 BP, no film/darkroom, smoking =
cigs/day, 1 pack = 20) **the exam's standard wins** — say so on the card.

## Layout
| Path | What | In git? |
|---|---|---|
| `.tools/anki/build_deck.py` | builds the .apkg from `.tools/anki/<book>/*.json` | yes |
| `.tools/anki/<book>/*.json` | card specs (diagrams / cloze / mcq) | yes |
| `.tools/anki/{test_import,contact_sheet,diagram_check}.py` | verification tools | yes |
| `.tools/cache/<Book>-NNN.png` | pages rendered at 200 dpi | no |
| `.source/RDH/*.pdf`, `.source/official/` | book PDFs, JCNDE docs | no (server only) |
| `Flashcards/`, `.obsidian/`, `Welcome.md` | the student's Obsidian vault (old card attempt + her notes) — synced with Steven's Mac via `vault-sync` | yes — don't touch unless asked |

The repo is also the Obsidian vault (`stvncx/obsidian-nbdhe`): **`git pull` before any commit**
— Steven's Mac pushes "Sync from MacBook-…" commits.

## Status
- 2026-10-08: Anki pipeline approved on p.148 diagrams. Building the WHOLE Anatomy PDF (Head &
  Neck pp.148–176 + Dental Anatomy pp.234–249): occlusion for every labeled figure, cloze for all
  text, MCQ for the bonus quizzes.
- Obsidian card attempt (SR plugin) abandoned 2026-10-08 — history in RUNBOOK §2–5.
