@echo off
setlocal EnableExtensions EnableDelayedExpansion
title org-ops launcher
call "%~dp0_common.cmd" || exit /b 1
:menu
cls
echo ========================================
echo  org-ops batch launcher
echo  repo: %ORG_OPS_ROOT%
echo ========================================
echo.
echo  1. once dry-run
echo  2. watch hints only
echo  3. watch production (-y)
echo  4. watch auto kick
echo  5. webhook
echo  6. dispatch list
echo  0. exit
echo.
set /p CHOICE=Select [0-6]: 
if "%CHOICE%"=="1" (call "%~dp0org-ops-once-dryrun.cmd" & pause & goto menu)
if "%CHOICE%"=="2" (call "%~dp0org-ops-watch.cmd" & goto menu)
if "%CHOICE%"=="3" (call "%~dp0org-ops-watch-yes.cmd" & goto menu)
if "%CHOICE%"=="4" (call "%~dp0org-ops-watch-auto.cmd" & goto menu)
if "%CHOICE%"=="5" (call "%~dp0org-ops-webhook.cmd" & goto menu)
if "%CHOICE%"=="6" (
    set /p EPIC=Epic GID: 
    if not "!EPIC!"=="" call "%~dp0org-ops-dispatch.cmd" !EPIC! list
    pause
    goto menu
)
if "%CHOICE%"=="0" exit /b 0
echo Invalid choice.
pause
goto menu