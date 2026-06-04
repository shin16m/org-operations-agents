@echo off
call "%~dp0_common.cmd" || exit /b 1
set "ORG_OPS_AUTO_KICK=1"
"%PY%" tools\asana_ops_runner.py --watch --interval 20 -y --human %*
exit /b %ERRORLEVEL%