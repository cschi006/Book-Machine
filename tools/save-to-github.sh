#!/bin/bash
cd "$(dirname "$0")/.."

echo ""
echo " === Book Machine — Save to GitHub ==="
echo ""

git add .

if git diff --cached --quiet; then
  echo " Nothing new to save — already up to date."
  echo ""
  read -rp " Press Enter to close..."
  exit 0
fi

STAMP=$(date '+%Y-%m-%d %H:%M')

read -rp " Commit message (or press Enter for auto): " MSG
if [ -z "$MSG" ]; then
  MSG="Save: $STAMP"
fi

git commit -m "$MSG"
git push

if [ $? -eq 0 ]; then
  echo ""
  echo " Saved to GitHub successfully!"
else
  echo ""
  echo " Something went wrong — check the output above."
  echo " Common fix: run 'git pull' first if another device pushed changes."
fi

echo ""
read -rp " Press Enter to close..."
