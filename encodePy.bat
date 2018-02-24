@echo off
setlocal

set python=
set encpy=
set py_func=

:enc
%python% %encpy% "%~1"

shift
if "%~1" == "" (
  endlocal
  pause
  goto :EOF
)
goto enc
