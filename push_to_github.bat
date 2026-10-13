@echo off
title Push CodeAlpha Task 1 to GitHub
echo ========================================================
echo Pushing CodeAlpha Task 1 (Language Translation Tool)...
echo Target: https://github.com/asadalikhan8267-acr/CodeAlpha_LanguageTranslationTool
echo ========================================================
cd /d "C:\Users\hp\Desktop\Task#1\CodeAlpha_LanguageTranslationTool"
git push -u origin main
echo.
echo ========================================================
echo Push command finished.
echo If it succeeded, your repository is now live!
echo If it asked for login, authorize in the browser window.
echo ========================================================
pause
