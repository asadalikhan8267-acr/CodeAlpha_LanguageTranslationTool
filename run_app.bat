@echo off
title CodeAlpha Language Translation Tool - Web UI
echo ========================================================
echo Launching CodeAlpha Language Translation Tool (Streamlit)...
echo ========================================================
cd /d "%~dp0"
"C:\Users\hp\anaconda3\envs\myenv\python.exe" -m streamlit run app.py
pause
