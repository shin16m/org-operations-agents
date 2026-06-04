@echo off
call "%~dp0_common.cmd" || exit /b 1
if "%~1"=="" (
    echo Usage: %~nx0 EPIC_GID list^|dryrun^|kick
    exit /b 1
)
set "PARENT=%~1"
set "MODE=%~2"
if "%MODE%"=="list" (
    "%PY%" tools\task_dispatcher.py --parent %PARENT% --list
    exit /b %ERRORLEVEL%
)
if "%MODE%"=="dryrun" (
    "%PY%" tools\task_dispatcher.py --parent %PARENT% --dry-run
    exit /b %ERRORLEVEL%
)
if "%MODE%"=="kick" (
    if defined CURSOR_API_KEY set "ORG_OPS_AUTO_KICK=1"
    "%PY%" tools\task_dispatcher.py --parent %PARENT% --kick -y
    exit /b %ERRORLEVEL%
)
echo Unknown mode: %MODE%
exit /b 1