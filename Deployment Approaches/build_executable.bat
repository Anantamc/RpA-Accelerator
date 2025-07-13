@echo off
echo ===== Building Partner Dashboard Executable =====
echo.

cd ..

REM Create venv if not exists
IF NOT EXIST .build_venv (
    echo Creating build virtual environment...
    python -m venv .build_venv
)

REM Activate venv
call .build_venv\Scripts\activate

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building executable...
python "Deployment Approaches\build_exe.py"

echo.
echo Done! The executable is in the 'dist' folder.
echo You can share the 'PartnerDashboard.exe' file with others.
pause
