@echo off
echo ===== Partner Revenue & Activity Dashboard =====
echo.

REM Create venv if not exists
IF NOT EXIST .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt

echo.
echo Starting Partner Revenue & Activity Dashboard...
echo Press Ctrl+C in the terminal to exit when finished

REM Run Streamlit app
python -m streamlit run app.py

pause
