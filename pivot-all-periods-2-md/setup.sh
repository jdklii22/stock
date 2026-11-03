#!/usr/bin/env bash
set -e

# Change directory to script folder
cd "$(dirname "$0")"

echo "=== Stock Pivot CLI Setup ==="

# Check Python installation
PYTHON_CMD=""
if command -v python3.11 &>/dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
else
    echo "Error: Python 3 is not installed or not in PATH."
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in PythonScript/.venv..."
    $PYTHON_CMD -m venv .venv
else
    echo "Virtual environment .venv already exists."
fi

# Upgrade pip and install requirements
echo "Installing dependencies from requirements.txt..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo "To run the script, execute:"
echo "  ./run.sh"
echo "or manually:"
echo "  source .venv/bin/activate && python3 pivot_cli.py"
