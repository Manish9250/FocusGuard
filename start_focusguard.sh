#!/bin/bash

# --- IMPORTANT: EDIT THESE TWO VARIABLES ---
# 1. The full, absolute path to your project directory
PROJECT_DIR="/home/manish/shared_space/FocusGuard"

# 2. Your Google API Key
export GENAI_API_KEY_1="AIzaSyCnPOPssH1tLsz8Glt7h-w"
# -----------------------------------------

# Navigate to the project directory
cd "$PROJECT_DIR"

# Get the full path to the Python executable inside your venv
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"

# Define the log file path
LOG_FILE="$PROJECT_DIR/focusguard.log"

# Run the blocker script using the venv's Python.
# - The 'sudo -E' command preserves environment variables (like the API key).
# - '>> "$LOG_FILE" 2>&1' redirects all output and errors to the log file for debugging.
echo "--- Starting FocusGuard at $(date) ---" >> "$LOG_FILE"
#sudo -E "$VENV_PYTHON" blocker.py >> "$LOG_FILE" 2>&1
sudo -E "$VENV_PYTHON" blocker.py 