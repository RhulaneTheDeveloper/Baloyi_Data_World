@echo off
REM =====================================================================
REM  Hosi Data Analyzer – Run Tests
REM =====================================================================

SET "PROJECT_DIR=%~dp0"
SET "TRUSTED_VENV=C:\Users\Hosi\AppData\Local\hosi_analyzer_venv"
SET "LOCAL_VENV=%PROJECT_DIR%.venv"

echo.
echo  =========================================
echo   HOSI DATA ANALYZER - TEST RUNNER
echo  =========================================
echo.

IF EXIST "%TRUSTED_VENV%\Scripts\python.exe" (
    SET "PYTHON=%TRUSTED_VENV%\Scripts\python.exe"
) ELSE IF EXIST "%LOCAL_VENV%\Scripts\python.exe" (
    SET "PYTHON=%LOCAL_VENV%\Scripts\python.exe"
) ELSE (
    echo [ERROR] No virtual environment found!
    pause & exit /b 1
)

cd /d "%PROJECT_DIR%"

echo  Generating test data...
"%PYTHON%" tests\generate_test_data.py

echo.
echo  Running test suite...
echo.
"%PYTHON%" -m pytest tests\test_analysis.py -v --tb=short

echo.
pause
