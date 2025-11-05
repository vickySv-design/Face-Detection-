@echo off
echo ========================================
echo Pushing to GitHub
echo ========================================

cd /d "%~dp0"

echo.
echo [1/5] Initializing Git repository...
git init

echo.
echo [2/5] Adding all files...
git add .

echo.
echo [3/5] Creating commit...
git commit -m "Initial commit: Face Detection Birthday App with AI-powered celebrations"

echo.
echo [4/5] Setting up remote...
git remote add origin https://github.com/vickySv-design/Face-Detection-.git

echo.
echo [5/5] Pushing to GitHub...
git branch -M main
git push -u origin main --force

echo.
echo ========================================
echo Done! Check: https://github.com/vickySv-design/Face-Detection-
echo ========================================
pause
