#!/usr/bin/env bash
# Builds for production into the 'docs/' folder, with BASEPATH pointing to GitHub Pages repo name

REPO_NAME="YOUR_REPO_NAME"
chmod +x src/main.py
python3 src/main.py "/${REPO_NAME}/"
