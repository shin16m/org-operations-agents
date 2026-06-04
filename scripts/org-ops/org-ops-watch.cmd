@echo off
call "%~dp0_common.cmd" || exit /b 1
"%PY%" tools\asana_ops_runner.py --watch --interval 60 --human %*
exit /b %ERRORLEVEL%