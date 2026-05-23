@echo off
echo Setting up Python virtual environment...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Virtual environment setup complete!
echo Run: cd backend && venv\Scripts\activate
