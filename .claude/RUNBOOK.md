# Runbook — NBDHE flashcards in Obsidian

How to reproduce this project from scratch: book PDFs → flashcards → Steven's shared
iCloud Obsidian vault. Procedures first, then the decision log (why it's done this way).
**Keep this current** — every new procedure or decision gets recorded here as we go.

Quick facts
- Vault (Mac, iCloud, shared with another person): `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/bobbi/NBDHE`
- GitHub: `stvncx/obsidian-nbdhe` (private), branch `main`
- Server project: `~/apps/obsidian` (`app obsidian` opens it in tmux with Claude)
- Review plugin: Obsidian **Spaced Repetition** v1.15.x
- Source: StudentRDH NBDHE review guide, 16 scanned PDFs (`.source/RDH/`, server only)

---

## 1. Server project setup (one time)

1. Clone the vault repo into the app dir: `git clone git@github.com:stvncx/obsidian-nbdhe.git ~/apps/obsidian`
   (`app <name>` in `~/fleet-hub/app-switcher.sh` resolves `~/apps/<name>` automatically).
2. Book PDFs: Steven uploads them to `stvncx/exchange` → `to-claude/RDH/`. Copy to the
   project (exchange gets pruned): `cp -a ~/exchange/to-claude/RDH ~/apps/obsidian/.source/`
3. Official JCNDE docs (public, free) → `.source/official/` (gitignored; `.txt` made with
   `pdftotext -layout`): from https://jcnde.ada.org/nbdhe/nbdhe-prepare —
   `candidate_guide_2026.pdf` (test specifications, pre- AND post-Nov-2026), `sample_questions.pdf`
   (official item style), `test_item_dev_guide.pdf` (how JCNDE writes items), `exam_updates.pdf`,
   `technical_report.pdf`. Re-download yearly — the guide is updated (this one: 9/17/2026).
4. Tools env: `python3 -m venv .tools/.venv && .tools/.venv/bin/pip install pillow numpy scipy`
   (system needs `poppler-utils` for `pdftoppm`, and DejaVu fonts).
5. `.gitignore` keeps out: `.source/`, `.tools/.venv/`, `.tools/cache/`, `.DS_Store`,
   `.obsidian/workspace*.json`, `.trash/`.
6. Project files live in dot-folders (`.claude/`, `.tools/`) — Obsidian hides them, so the
   shared vault looks clean.
7. Listed in `~/fleet-hub/inventory.md` under "Not apps".

## 2. Mac ↔ GitHub sync setup (one time, on Steven's Mac)

Script: `.tools/mac/setup-vault-sync.sh` (also delivered via `exchange/from-claude/`).
Steven downloads it from GitHub (file view → "Download raw file") and runs
`bash ~/Downloads/setup-vault-sync.sh`. It:

1. Backs up the whole vault to `~/NBDHE-backup-<date>`.
2. Bare-clones the repo to `~/.obsidian-nbdhe.git` (**outside iCloud**) and sets
   `core.worktree` to the vault, `core.bare false`, `pull.rebase true`.
3. `git reset` + `git checkout -- .` — brings repo files into the vault. Where a file exists
   in both, the GitHub version wins (that's why step 1 backs up).
4. Installs `~/bin/vault-sync` and adds `~/bin` to PATH + a `vgit` alias in `~/.zshrc`.
5. Runs the first sync.

Prereqs: Mac can reach GitHub over **HTTPS** (credential in macOS keychain; no ssh key on
the Mac). Steven then sets the vault folder to Finder → **Keep Downloaded**.

Test before shipping changes to the script: run it on the server with a fake `HOME`, a fake
vault, and `url.<local bare clone>.insteadOf https://github.com/stvncx/obsidian-nbdhe.git`
in the fake `~/.gitconfig` (done 2026-10-08: first sync, edit sync, deletion guard all pass).

## 3. Daily sync flow

```
Claude (server) --push--> GitHub <--vault-sync--> Mac vault --iCloud--> iPhone / iPad / shared user
```
- **Claude, before any edit:** `git pull` in `~/apps/obsidian`. After: commit small, push,
  then tell Steven to run `vault-sync`.
- **Steven:** runs `vault-sync` after Claude announces new cards, and after study sessions
  (pushes review progress).
- `vault-sync` = refuse if iCloud placeholders (`*.icloud`) exist → `git add -A` → refuse if
  >5 deletions → commit "Sync from <host> <time>" → `pull --rebase` (abort + notify on
  conflict) → push. Failures notify via macOS notification; nothing is lost.

**Review progress lives in the notes.** The SR plugin appends `<!--SR:!2026-10-09,3,250-->`
after a reviewed card. Never regenerate a note wholesale — edit cards in place and keep each
SR comment with its card, or his progress is wiped.

## 4. Making cards for a book section

1. Read the pages: Read tool with `pages` on `.source/RDH/<Book>.pdf` (scans — no text layer).
   PDF page ≠ book page (Anatomy PDF p.1 = book p.147).
2. Write `Flashcards/<Book>/NN <Section title>.md`:
   - frontmatter `source: StudentRDH NBDHE guide — <Book>, pp. X–Y`
   - deck tag line `#flashcards/rdh/<book>`
   - headings mirror the book's subheadings
3. Card syntax (his plugin settings): `Q::A`, `term:::definition` (both ways), `==cloze==`,
   multi-line `?` / `??`. No end marker → **no blank lines inside a card**; a blank line ends it.
4. Image cards — see §5.
5. Correct the book's typos; flag (in the commit/chat) any place we deviate from the book's
   wording on substance.
6. `git pull && git add && git commit && git push`, tell Steven to `vault-sync`.

## 5. Image (occlusion) cards

1. Render the page: `occlude.py` renders on demand into `.tools/cache/<Book>-NNN.png` (200 dpi).
2. Find label boxes: `.tools/.venv/bin/python .tools/detect.py .tools/cache/<Book>-NNN.png`
   (finds pale-cyan `(~210,250,254)` and yellow label backgrounds). It **misses some** — add
   those by hand (sample pixel colors / crop to find coordinates).
3. Add an entry to `.tools/<book>-diagrams.json`: `name` (prefix per book, e.g. `anat-`),
   `pdf`, `pdf_page`, `crop`, `labels` [[box], "answer"] in reading order.
4. Build: `.tools/.venv/bin/python .tools/occlude.py .tools/<book>-diagrams.json Flashcards/<Book>/images`
   → `<name>.png` (answer) + `<name>-q.png` (labels covered by numbered orange boxes).
5. **Look at every `-q` image** before committing (missed boxes leak answers).
6. Cards: per label `![[<name>-q.png|600]]` / "<Diagram> — what is **#N**?" / `?` /
   answer + `![[<name>.png|600]]`, plus one "label all N" card per diagram.
7. Diagrams with plain-text labels (no boxes, e.g. Anatomy p.150 body planes) need boxes by hand.

---

## Decision log

| Date | Decision | Why |
|---|---|---|
| 10-07 | Spaced Repetition plugin format | Steven hadn't named a plugin; most common. He then installed it. |
| 10-07 | One note per book section, deck tag per book | mirrors the book; per-book decks |
| 10-07 | Image occlusion via numbered boxes on cropped diagrams | Steven asked for image cards; Obsidian has no native occlusion |
| 10-07 | Stay in Obsidian (not Anki / custom app) | Steven's choice, 10-08 |
| 10-08 | Server project in `~/apps/obsidian`, tools in hidden dot-folders | match fleet convention; keep shared vault clean |
| 10-08 | PDFs copied to gitignored `.source/` | exchange gets pruned; 35 MB of scans shouldn't sync to devices |
| 10-08 | Git data outside iCloud (`~/.obsidian-nbdhe.git` + `core.worktree`) | `.git` inside iCloud corrupts and would be shared with the other vault user |
| 10-08 | Only the Mac runs git; iCloud handles phones + shared user | iOS git is unreliable; nothing changes for the other person |
| 10-08 | Ignore `workspace*.json`, `.DS_Store` | change on every click / per device → pointless conflicts |
| 10-08 | `vault-sync` deletion guard (>5) and iCloud-placeholder guard | offloaded iCloud files look like deletions to git |
| 10-08 | Official JCNDE docs are the authority for scope + question style | the book is a study aid; the test specs define what's examined, sample questions define how |
| 10-08 | Write to the UPDATED test specs (effective 2026-11-01) | the student sits the exam ~January 2027 |
| 10-08 | Exam's adopted standards override the book (AHA 2021/2017, ASA 2020, IADT 2020, AAP 2017, no film, smoking cigs/day) | JCNDE "Recent and Forthcoming Updates" (9/23/2026); the book may be older |
| 10-08 | HTTPS to GitHub from the Mac | Mac has no GitHub ssh key; HTTPS credentials already worked |

## Open items
- **Card quality** (10-07: "the cards kind of suck") — reason not yet pinned down. Next.
- Auto-run `vault-sync` every 10 min via launchd — after manual runs prove reliable.
