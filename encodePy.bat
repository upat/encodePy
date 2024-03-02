@echo off
setlocal

:enc
cd /d %~dp0
py encodePy.py "%~1"

shift
if "%~1" == "" (
  endlocal
  pause
  goto :EOF
)
goto enc
