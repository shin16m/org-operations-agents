@echo off
call "%~dp0_common.cmd" || exit /b 1
"%PY%" tools\asana_ops_runner.py --once --dry-run --human %*
exit /b %ERRORLEVEL%