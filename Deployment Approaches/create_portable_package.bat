@echo off
echo ===== Creating Portable Partner Dashboard Package =====
echo.

cd ..

REM Create directories
mkdir portable_dashboard 2>nul
mkdir portable_dashboard\app 2>nul

REM Copy application files
echo Copying application files...
xcopy /Y *.py portable_dashboard\app\
xcopy /Y *.txt portable_dashboard\app\
xcopy /Y run_dashboard.bat portable_dashboard\app\
if exist lib xcopy /Y lib portable_dashboard\app\lib\ /E /I

REM Create portable Python environment
echo Creating portable Python environment...
python -m venv portable_dashboard\python

REM Install requirements
echo Installing required packages...
call portable_dashboard\python\Scripts\activate
cd portable_dashboard\app
pip install -r requirements.txt
cd ..\..

REM Create startup script
echo Creating startup script...
(
echo @echo off
echo echo Starting Partner Dashboard...
echo call %%~dp0python\Scripts\activate
echo cd %%~dp0app
echo python -m streamlit run app.py
echo pause
) > portable_dashboard\start_dashboard.bat

echo.
echo Portable package created in the 'portable_dashboard' folder.
echo.
echo To share:
echo 1. Zip the 'portable_dashboard' folder
echo 2. Share the zip file
echo 3. Recipients just need to extract and run 'start_dashboard.bat'
echo.
pause
