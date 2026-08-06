#!/bin/bash
# Double-click launcher for the CV Generator web app (macOS/Linux).
# Portable: runs the app from whatever folder this script lives in.
# Keep the Terminal window open while using the app; closing it stops the app.

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
URL="http://127.0.0.1:8000"

cd "$APP_DIR" || { echo "Could not find the app folder: $APP_DIR"; read -r; exit 1; }

if lsof -ti tcp:8000 >/dev/null 2>&1; then
  echo "CV Generator is already running."
  open "$URL" 2>/dev/null || xdg-open "$URL" 2>/dev/null
  echo "Opened $URL in your browser. You can close this window."
  exit 0
fi

echo "Starting CV Generator..."
echo "Your browser will open at $URL in a moment."
echo "Keep this window open while using the app. Close it (or press Ctrl+C) to stop."
echo

( sleep 2; open "$URL" 2>/dev/null || xdg-open "$URL" 2>/dev/null ) &

python3 app.py
