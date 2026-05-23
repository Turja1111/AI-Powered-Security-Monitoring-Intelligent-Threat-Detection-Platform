#!/bin/bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo 'Virtual environment ready. Run: source backend/venv/bin/activate'
