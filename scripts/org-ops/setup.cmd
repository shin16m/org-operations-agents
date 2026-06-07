@echo off
setlocal EnableExtensions
call "%~dp0_common.cmd" || exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
exit /b %ERRORLEVEL%
