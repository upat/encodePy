@echo off
setlocal

cd /d %~dp0
:enc
py encodePy.py "%~1"

shift
if "%~1" == "" (
  endlocal
  pause
  goto :EOF
)
goto enc
