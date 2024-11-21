@echo off
echo Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo Failed to create virtual environment.
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies.
    exit /b 1
)

echo Building the app...
python -m compileall main.py
if %ERRORLEVEL% neq 0 (
    echo Failed to build the app.
    exit /b 1
)

echo Starting the app...
python main.py
if %ERRORLEVEL% neq 0 (
    echo Failed to start the app.
    exit /b 1
)

pause
