# =====================================================================
#  Hosi Data Analyzer – PowerShell Launch Script
#  Usage: .\start_app.ps1
# =====================================================================

$ProjectDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$TrustedVenv = "C:\Users\Hosi\AppData\Local\hosi_analyzer_venv"
$LocalVenv   = Join-Path $ProjectDir ".venv"

Write-Host ""
Write-Host " ==========================================" -ForegroundColor Cyan
Write-Host "  HOSI DATA ANALYZER  v1.0" -ForegroundColor Cyan
Write-Host "  Hosi Technologies - Plan 1 Analysis" -ForegroundColor Cyan
Write-Host " ==========================================" -ForegroundColor Cyan
Write-Host ""

# Select venv
if (Test-Path "$TrustedVenv\Scripts\python.exe") {
    $Python     = "$TrustedVenv\Scripts\python.exe"
    $Streamlit  = "$TrustedVenv\Scripts\streamlit.exe"
    Write-Host " [OK] Using trusted venv: $TrustedVenv" -ForegroundColor Green
} elseif (Test-Path "$LocalVenv\Scripts\python.exe") {
    $Python     = "$LocalVenv\Scripts\python.exe"
    $Streamlit  = "$LocalVenv\Scripts\streamlit.exe"
    Write-Host " [OK] Using project venv: $LocalVenv" -ForegroundColor Green
} else {
    Write-Host " [ERROR] No virtual environment found!" -ForegroundColor Red
    Write-Host ""
    Write-Host " Create one with:"
    Write-Host "   python -m venv .venv"
    Write-Host "   .venv\Scripts\pip install -r requirements.txt"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host " [OK] Python: $Python" -ForegroundColor Green
Write-Host ""
Write-Host " Starting at http://localhost:8501 — press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

Set-Location $ProjectDir
& $Streamlit run app.py --server.port 8501 --server.headless false
