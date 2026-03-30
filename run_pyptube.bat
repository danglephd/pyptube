@echo off
REM ============================================
REM pyptube - YouTube Link Tracker
REM Clipboard Monitoring Service Launcher
REM ============================================

REM Activate virtual environment
call .\.venv\Scripts\activate.bat
IF ERRORLEVEL 1 (
    echo Error: Could not activate virtual environment.
    echo Please ensure .venv is created in the project directory.
    exit /b 1
)

REM Run pyptube
python pyptube.py

exit /b 0
