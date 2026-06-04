@echo off
call "%~dp0_common.cmd" || exit /b 1
"%PY%" tools\asana_webhook_handler.py --port 8766 %*
exit /b %ERRORLEVEL%