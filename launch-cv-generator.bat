@echo off
REM Double-click launcher for the CV Generator web app (Windows).
REM Runs the app from whatever folder this script lives in.
REM Keep this window open while using the app; close it to stop.

cd /d "%~dp0"

echo Starting CV Generator...
echo Your browser will open at http://127.0.0.1:8000 in a moment.
echo Keep this window open while using the app. Close it (or press Ctrl+C) to stop.
echo.

REM Open the browser a few seconds after the server starts.
start "" /min cmd /c "timeout /t 3 >nul & explorer http://127.0.0.1:8000"

REM Run the server in the foreground so this window represents the running app.
python app.py

pause
