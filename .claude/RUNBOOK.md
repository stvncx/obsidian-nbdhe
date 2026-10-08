# Runbook — NBDHE flashcards

> **2026-10-08: moved to ANKI** (Steven: "Obsidian looks like shit"). §6 is the current card
> pipeline. §2–5 (Obsidian vault, vault-sync, SR plugin, CSS-snippet occlusion) are kept as
> the record of the Obsidian attempt; the vault + sync still work if notes are wanted there.

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

## 4a. Card design (v2, 2026-10-08 — DRAFT pending Steven's review; he is the pedagogy lead)

Steven is a trained teacher (25 yrs, adult learners, memory research); **his judgment on
learning design overrides these defaults.** Each section note has four parts:
1. **Exam-style**: 4-option MCQ in JCNDE format (stem, A–D, one key; "most likely",
   "EXCEPT one… Which is the EXCEPTION?"; clinical vignettes). Answer = key + one-line *why*
   + why the tempting distractor is wrong. Rotate the key position.
2. **Must-know facts**: minimum-information recall (one fact per card) for things that
   just have to be memorized (numbers, duct openings).
3. **Tell apart**: contrast cards for easily-confused pairs/triads (discrimination).
4. **Diagrams**: v3 image-occlusion cards (§5).
Target ~15–25 cards per section; skip low-yield trivia; weight sections by the test specs.
Add clinically relevant, exam-tested facts the book omits (e.g. attached gingiva width; IANB
landmark) when they belong to the section's topic.

## 5. Image (occlusion) cards — v3 (2026-10-08, Steven's design)

**Design:** same full-size diagram on every card, **one** label covered per card, and the
answer is revealed **in place** (inside the cover box, on the image) — no flip to a second
image. Other labels stay visible.

**Mechanism** (why it works in the SR plugin):
- SR *cloze* cards redraw the whole card on reveal (`drawBack`: `content.empty()` for cloze;
  other card types append the answer under an `<hr>`). So a cloze inside the cover box shows
  `[...]` on the front and the term on the back, in the same spot. Checked in the plugin's
  `main.js` (v1.15.4) — re-check if the plugin's major version changes.
- Each card is ONE line of HTML: `<div class="occ occ-<diagram>"><span class="occ-box"
  style="left/top/width/height in %">==Answer==</span></div>` (blank line between cards).
- The diagram is a CSS background, embedded as a JPEG data URI in the vault CSS snippet
  `.obsidian/snippets/rdh-occlusion.css` → renders on Mac/iPhone/iPad with no image-path
  issues. Snippet enabled via `.obsidian/appearance.json` → `enabledCssSnippets`.
- Text in the box scales with the image (`container-type: inline-size`, `font-size: 2.5cqw`)
  and wraps for long labels.
- In normal note view the cards show as raw HTML with `==Answer==` — expected; review via SR.

**Procedure:**
1. Label boxes: `.tools/.venv/bin/python .tools/detect.py .tools/cache/<Book>-NNN.png` (finds the
   book's pale-cyan `(~210,250,254)` / yellow callouts; **misses some** — add by hand).
   Pages render on demand at 200 dpi into `.tools/cache/` (via `occlude.render`).
2. Spec entry in `.tools/<book>-diagrams.json`: `name` (prefix per book, e.g. `anat-`), `pdf`,
   `pdf_page`, `crop`, `labels` [[x0,y0,x1,y1], "answer"] — answer = the book's label text
   (typos fixed), so it fits the box.
3. Generate: `.tools/.venv/bin/python .tools/occlusion_cards.py .tools/<book>-diagrams.json <name> [<name>…] > cards.md`
   — rewrites the CSS snippet for the named diagrams and prints one card per label.
   ⚠ The snippet holds ONLY the diagrams named in that run — pass ALL diagrams in use.
4. **Verify visually** before committing: render front/back with Playwright (installed in
   `.tools/.venv`, chromium headless) — simulate SR by replacing `==X==` with
   `<span style='color:#2196f3'>[...]</span>` (front) / `…X…` (back); check at 700 px and 390 px.
5. Paste cards into the section note, commit, push, Steven runs `vault-sync`.

(v1, 10-07: numbered boxes on every label + separate answer image; v2: one "name all N"
card per diagram. Both dropped — too many numbers, images too big, answer not in place.
`.tools/occlude.py` is the v1 builder, kept only for `render()`.)

## 6. Anki deck (current pipeline)

**Delivery:** build `.apkg` → copy to `~/exchange/from-claude/` → Steven downloads from GitHub →
the student imports it (double-click on desktop, or Files → share to AnkiMobile).
Re-importing an updated `.apkg` **updates notes in place and keeps review history**, because
note GUIDs are stable. Student needs: Anki desktop (free), AnkiMobile for iPhone/iPad
($24.99 one-time, one Apple ID), free AnkiWeb account to sync between them.

**Build:** `.tools/.venv/bin/python .tools/anki/build_deck.py .tools/anki/build/<name>.apkg <diagram> [<diagram>…]`
(needs `genanki` in the venv). Reads `.tools/anatomy-diagrams.json`, crops each diagram
from the rendered page (1400 px JPEG → `.tools/anki/media/`), one note per label.

**Note type "NBDHE Image Occlusion"** (custom HTML/CSS, not Anki's built-in IO notetype — the
built-in one is meant to be authored inside Anki; a custom type renders identically on
desktop/AnkiMobile/AnkiDroid and can be previewed off-device):
- Fields: Answer, Image, Title, Left, Top, Width, Height (box, % of image), Extra, Source.
- Front: title + image + orange "?" box over ONE label. Back: same image + same box showing
  the term (blue) — back template has no `{{FrontSide}}`, so the reveal is in place.
- Night mode via `.nightMode` / `.night_mode`. Box text scales with the image (`cqw`).
- **Fixed IDs — never change:** `MODEL_ID 1728390001`, `DECK_ID 1728390101` (`NBDHE::Anatomy`),
  GUID = `guid_for('nbdhe-io', diagram name, answer)`. Changing an answer's text creates a new
  note (old one orphaned) — fix label text before the student starts reviewing.

**Media rule (bit us 2026-10-08):** Anki's importer DROPS media not referenced by an
`<img src="…">` *inside a field*. A bare filename in a field + `<img src="{{Image}}">` in the
template imports cards with NO images. So the Image field holds the full `<img src="x.jpg">`
and the template uses `{{Image}}`.

**Verify before shipping (mandatory):**
`.tools/.venv/bin/python .tools/anki/test_import.py <deck>.apkg [preview.png]` — imports into a
throwaway collection with Anki's REAL importer (`pip install anki`), checks every referenced
image survived, and (with a 2nd arg) screenshots the first cards from the HTML Anki itself
generates. Look at the screenshot. Unzipping the .apkg and filling templates yourself is NOT
enough — it misses importer behaviour.

**Changing the note type's templates/fields:** Anki may keep the old templates on re-import.
For a test deck with no reviews: have them delete the note type (Tools → Manage Note Types →
NBDHE Image Occlusion → Delete) and re-import. Once she has review history, never do that —
change templates only with a deliberate migration plan.

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
| 10-08 | Card design v2 (exam-style MCQ + must-know + tell-apart + 1 diagram card) | v1 "kind of sucks": definition recall ≠ how the NBDHE tests. Steven to review |
| 10-08 | Image cards v3: one label covered per card, revealed in place; images full width | Steven: images too big, too many numbers; wants same image, one occlusion, in-place reveal |
| 10-08 | All other cards deleted; focus on p.148 images first, then rescope | Steven's call — get the image mechanism right before scaling |
| 10-08 | **Switch flashcards to Anki** | Obsidian SR review UI can't be made to look good; Anki has a polished reviewer, full HTML/CSS card templates, FSRS, updates keep history |
| 10-08 | Custom Anki note type for occlusion (not built-in IO) | generated off-device reliably; previewable; same render on every Anki client |
| 10-08 | Image must be `<img>` inside the field; verify with Anki's real importer | first test deck shipped with no images — preview skipped the importer |
| 10-08 | HTTPS to GitHub from the Mac | Mac has no GitHub ssh key; HTTPS credentials already worked |

## Open items
- **Card quality** (10-07: "the cards kind of suck") — reason not yet pinned down. Next.
- Auto-run `vault-sync` every 10 min via launchd — after manual runs prove reliable.
