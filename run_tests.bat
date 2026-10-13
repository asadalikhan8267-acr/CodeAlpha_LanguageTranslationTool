@echo off
title CodeAlpha Language Translation Tool - Test Suite
echo ========================================================
echo Running Automated Unit Tests (pytest)...
echo ========================================================
cd /d "%~dp0"
"C:\Users\hp\anaconda3\envs\myenv\python.exe" -m pytest -v
echo.
echo ========================================================
echo Test execution complete.
echo ========================================================
pause
