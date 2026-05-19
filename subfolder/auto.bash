#!/bin/bash
VENV_DIR=".venv"

#activate if exists
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/Scripts/activate"
    pip freeze >> requirements.txt
    echo "requirements generated from virtual env: $VENV_DIR"
else
    echo "error: virtual env : $VENV_DIR not found"
    exit 1
fi