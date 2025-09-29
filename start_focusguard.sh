#!/bin/bash

# --- IMPORTANT: EDIT THESE TWO VARIABLES ---
# 1. The full, absolute path to your project directory
PROJECT_DIR="/home/manish/shared_space/FocusGuard"

# 2. Your Google API Key
export GENAI_API_KEY_1="AIzaSyCnPOPM61T8fT37tLsz8Glt7h-w"
# -----------------------------------------

# Navigate to the project directory
cd "$PROJECT_DIR"

# Get the full path to the Python executable inside your ven
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"

# Define the log file path
BLOCKER_LOG="$PROJECT_DIR/blocker.log"
WEBSERVER_LOG="$PROJECT_DIR/webserver.log"

echo "--- Starting FocusGuard Blocker at $(date) ---" >> "$BLOCKER_LOG"
# The '&' runs the process in the background
sudo -E "$VENV_PYTHON" blocker.py >> "$BLOCKER_LOG" 2>&1 &

echo "--- Starting FocusGuard Web Server at $(date) ---" >> "$WEBSERVER_LOG"
sudo -E "$VENV_PYTHON" web_server.py >> "$WEBSERVER_LOG" 2>&1 &