@echo off
cd /d "%~dp0\.."
python cliente\main.py
if errorlevel 1 pause
