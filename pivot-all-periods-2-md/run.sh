#!/usr/bin/env bash
set -e

# Change directory to script location
cd "$(dirname "$0")"

# Ensure virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running setup.sh first..."
    ./setup.sh
fi

.venv/bin/python3 pivot_cli.py "$@"
