#!/usr/bin/env bash
set -euo pipefail

# One-command setup + run script for Adaptive Study Agent POC
# Run from project root: ./install.sh

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BOOTSTRAP="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BOOTSTRAP="python"
else
  echo "Python was not found in PATH."
  exit 1
fi

"$PYTHON_BOOTSTRAP" -m venv .venv

if [ -x ".venv/bin/python" ]; then
  VENV_PY=".venv/bin/python"
  VENV_PIP=".venv/bin/pip"
  VENV_STREAMLIT=".venv/bin/streamlit"
elif [ -x ".venv/Scripts/python.exe" ]; then
  VENV_PY=".venv/Scripts/python.exe"
  VENV_PIP=".venv/Scripts/pip.exe"
  VENV_STREAMLIT=".venv/Scripts/streamlit.exe"
else
  echo "Virtual environment was created, but Python executable was not found in .venv/bin or .venv/Scripts."
  exit 1
fi

"$VENV_PY" -m pip install --upgrade pip
"$VENV_PIP" install -r requirements.txt

# Optional verification
"$VENV_PY" -c "import streamlit, openai, pydantic, docx, pptx, pypdf, dotenv; print('All required packages imported successfully.')"

echo "Starting Streamlit app on http://localhost:8501 ..."
exec "$VENV_STREAMLIT" run app.py
