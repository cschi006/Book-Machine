# Book Machine — Saving to GitHub

Your Book Machine files live in OneDrive (auto-sync) and GitHub (version history + safety net).
Use the scripts here to push to GitHub whenever you finish a session.

---

## Windows (laptop / desktop)

**Double-click** `save-to-github.bat`

A terminal window opens, shows what it's committing, asks for an optional message, then pushes and closes. That's it.

First time only: make sure git is installed and you've run `git push` at least once from this machine so your credentials are cached.

---

## Mac (Mac Mini)

**One-time setup** — open Terminal and run:

```
chmod +x ~/OneDrive/Book\ Machine/tools/save-to-github.sh
```

This makes the script executable. You only do this once.

**To run it:** double-click `save-to-github.sh` in Finder, or run it from Terminal:

```
~/OneDrive/Book\ Machine/tools/save-to-github.sh
```

If double-clicking opens it in a text editor instead of running it, right-click → Open With → Terminal.

---

## When to save

- End of any writing or editing session
- Before switching to a different device
- Before asking Claude to make big changes to the manuscript or dashboard
- Any time you want a checkpoint you can return to

---

## If it says "rejected" or "failed to push"

Another device pushed changes that you don't have yet. Fix:

```
git pull
```

Then run the save script again.

---

## From Claude Code

You can also just say: **"save my work to GitHub"** in any Claude Code session and it will commit and push for you.

---

## What gets saved

Everything in `C:\Users\cschi\OneDrive\Book Machine\` that isn't in `.gitignore` — manuscripts, skills, dashboard files, dossiers, session reports, all of it.
