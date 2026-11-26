#!/bin/bash
# =============================================
# 🚀 GitHub Push Script — Run this on your PC
# =============================================

REPO="https://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@github.com/alamin126666/Live-Unmuter-V2.git"

# Clone or init
if [ -d ".git" ]; then
  echo "✅ Already a git repo"
else
  git init
  git remote add origin "$REPO"
fi

# Config
git config user.email "bot@railway.app"
git config user.name "LiveUnmuterBot"

# Stage all files
git add .
git status

# Commit
git commit -m "✨ Premium UI v2.0 + Railway build fix (remove nixpacks)"

# Push
git branch -M main
git push -u origin main --force

echo ""
echo "✅ Done! Check your Railway dashboard — redeploy will start automatically."
