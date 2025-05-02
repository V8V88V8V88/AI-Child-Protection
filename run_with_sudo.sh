#!/bin/bash
# Wrapper script to run the application with sudo while using the virtual environment

# Get the absolute path to the Python interpreter in the virtual environment
VENV_PYTHON="$(pwd)/.venv/bin/python"

# Run the application with sudo using the virtual environment's Python
sudo -E "$VENV_PYTHON" run_main_app.py "$@" 