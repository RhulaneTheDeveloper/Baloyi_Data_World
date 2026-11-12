@echo off
REM =====================================================================
REM  Hosi Data Analyzer – Launch Script
REM  Tries trusted AppData venv first, falls back to project .venv
REM =====================================================================

SET "PROJECT_DIR=%~dp0"
SET "TRUSTED_VENV=C:\Users\Hosi\AppData\Local\hosi_analyzer_venv"
SET "LOCAL_VENV=%PROJECT_DIR%.venv"

echo.
echo  =========================================
echo   HOSI DATA ANALYZER  v1.0
echo   Hosi Technologies - Plan 1 Analysis
echo  =========================================
echo.

REM -- Choose venv -------------------------------------------------------
IF EXIST "%TRUSTED_VENV%\Scripts\python.exe" (
    SET "PYTHON=%TRUSTED_VENV%\Scripts\python.exe"
    SET "STREAMLIT=%TRUSTED_VENV%\Scripts\streamlit.exe"
    echo  [OK] Using trusted venv: %TRUSTED_VENV%
) ELSE IF EXIST "%LOCAL_VENV%\Scripts\python.exe" (
    SET "PYTHON=%LOCAL_VENV%\Scripts\python.exe"
    SET "STREAMLIT=%LOCAL_VENV%\Scripts\streamlit.exe"
    echo  [OK] Using project venv: %LOCAL_VENV%
) ELSE (
    echo  [ERROR] No virtual environment found!
    echo.
    echo  Please create one first:
    echo    python -m venv .venv
    echo    .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo  [OK] Python: %PYTHON%
echo.
echo  Starting application at http://localhost:8501
echo  Press Ctrl+C to stop.
echo.

cd /d "%PROJECT_DIR%"
"%STREAMLIT%" run app.py --server.port 8501 --server.headless false

pause
