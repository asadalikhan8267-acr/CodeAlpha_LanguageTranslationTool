@echo off
title Push CodeAlpha Task 1 to GitHub
echo ========================================================
echo Pushing CodeAlpha Task 1 (Language Translation Tool)...
echo Repository: https://github.com/asadalikhan8267-acr/CodeAlpha_LanguageTranslationTool
echo ========================================================
cd /d "%~dp0"
git push -u origin main
echo.
echo ========================================================
echo If a browser window opened, click Sign In / Authorize.
echo Once the push finishes, press any key to close.
echo ========================================================
pause
