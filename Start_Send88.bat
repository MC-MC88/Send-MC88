@echo off
title Send88 - Local File Transfer
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo  Python was not found on this PC.
    echo  Install it from https://python.org
    echo  and check "Add Python to PATH" during setup.
    echo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo.
    echo  Setting up Send88 for the first time, please wait...
    echo.
    python -m venv .venv
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip >nul
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

cls
python send88.py

pause