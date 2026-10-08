#!/bin/bash
# setup-vault-sync.sh — connect the iCloud Obsidian vault bobbi/NBDHE to GitHub
# (stvncx/obsidian-nbdhe) and install the `vault-sync` command. Run once, on the Mac:
#     bash ~/Downloads/setup-vault-sync.sh
# Safe: backs up the whole vault first, stops at the first problem, keeps all git
# data OUTSIDE iCloud (~/.obsidian-nbdhe.git) so nothing git-related enters the shared vault.
set -e
VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/bobbi/NBDHE"
GITDIR="$HOME/.obsidian-nbdhe.git"
[ -d "$VAULT/.obsidian" ] || { echo "STOP: vault not found at $VAULT"; exit 1; }
[ ! -e "$GITDIR" ] || { echo "STOP: $GITDIR already exists (setup already ran?)"; exit 1; }

# 1. full backup of the vault first
BK="$HOME/NBDHE-backup-$(date +%Y%m%d-%H%M)"; cp -Rp "$VAULT" "$BK"; echo "backup: $BK"

# 2. git data outside iCloud, pointed at the vault
git clone -q --bare https://github.com/stvncx/obsidian-nbdhe.git "$GITDIR"
export GIT_DIR="$GITDIR"
git config core.bare false
git config core.worktree "$VAULT"
git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git config pull.rebase true
git fetch -q origin && git branch -q -u origin/main main
cd "$VAULT" && git reset -q && git checkout -- .   # bring the flashcards etc. into the vault

# 3. the sync command
mkdir -p "$HOME/bin"
cat > "$HOME/bin/vault-sync" <<'SYNC'
#!/bin/bash
# vault-sync: sync the iCloud vault bobbi/NBDHE <-> GitHub stvncx/obsidian-nbdhe
VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/bobbi/NBDHE"
export GIT_DIR="$HOME/.obsidian-nbdhe.git" GIT_WORK_TREE="$VAULT"
say() { osascript -e "display notification \"$1\" with title \"Vault sync\"" >/dev/null 2>&1; echo "vault-sync: $1"; }
cd "$VAULT" || { say "vault folder missing"; exit 1; }
if find . -name '*.icloud' | grep -q .; then say "iCloud has offloaded files - set the vault to Keep Downloaded, then retry"; exit 1; fi
git add -A
DEL=$(git diff --cached --diff-filter=D --name-only | wc -l | tr -d ' ')
if [ "$DEL" -gt 5 ]; then git reset -q; say "STOPPED: $DEL files would be deleted - nothing synced, ask Claude"; exit 1; fi
git diff --cached --quiet || git commit -q -m "Sync from $(hostname -s) $(date '+%F %T')"
if ! git pull -q --rebase; then git rebase --abort 2>/dev/null; say "conflict with GitHub - nothing lost, ask Claude"; exit 1; fi
git push -q && say "ok"
SYNC
chmod +x "$HOME/bin/vault-sync"
grep -q 'vault-sync' "$HOME/.zshrc" 2>/dev/null || cat >> "$HOME/.zshrc" <<'RC'
# Obsidian vault <-> GitHub (vault-sync)
export PATH="$HOME/bin:$PATH"
alias vgit='git --git-dir=$HOME/.obsidian-nbdhe.git --work-tree="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/bobbi/NBDHE"'
RC

# 4. first sync
"$HOME/bin/vault-sync"
echo
echo "Done. Open a NEW iTerm window, then run:  vault-sync"
