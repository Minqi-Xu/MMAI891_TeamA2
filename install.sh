#!/usr/bin/env bash
set -euo pipefail

# One-command setup + run script for Adaptive Study Agent POC
# Run from project root: ./install.sh

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# Optional verification
.venv/bin/python -c "import streamlit, openai, pydantic, docx, pptx, pypdf, dotenv; print('All required packages imported successfully.')"

echo "Starting Streamlit app on http://localhost:8501 ..."
exec .venv/bin/streamlit run app.py
