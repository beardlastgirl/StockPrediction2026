@echo off
setlocal
cd /d %~dp0

echo Ensure git repo...
git init

echo Rename branch to main (optional)...
git branch -M main

echo Authenticate GitHub CLI if needed...
gh auth status || exit /b 1

echo Create and push repo...
gh repo create beardlastgirl/StockPrediction2026 --public --source=. --remote=origin --push
if errorlevel 1 (
    echo If repo exists, pushing instead...
    git remote add origin https://github.com/beardlastgirl/StockPrediction2026.git 2>nul
    git push -u origin main
)
pause
