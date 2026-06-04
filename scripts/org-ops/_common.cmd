@echo off
set "ORG_OPS_SCRIPT_DIR=%~dp0"
for %%I in ("%ORG_OPS_SCRIPT_DIR%..\..") do set "ORG_OPS_ROOT=%%~fI"
set "PY=%ORG_OPS_ROOT%\.venv\Scripts\python.exe"
if not exist "%PY%" (
    echo ERROR: venv not found: %PY%
    echo Run setup_venv.ps1 under skills\platform\asana-buddy\optional
    exit /b 1
)
set "PYTHONIOENCODING=utf-8"
cd /d "%ORG_OPS_ROOT%"
exit /b 0