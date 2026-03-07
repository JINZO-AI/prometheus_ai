#!/bin/bash
# Quick start — activate venv and run app
if [ -d ".venv" ]; then
  source .venv/bin/activate
elif [ -d "venv" ]; then
  source venv/bin/activate
fi
python app.py
