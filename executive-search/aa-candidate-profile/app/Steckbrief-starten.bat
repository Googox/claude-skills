@echo off
REM A/A Steckbrief-Arbeitsplatz, lokaler Start unter Windows.
REM Startet die Anwendung auf 127.0.0.1 und oeffnet den Browser.
setlocal
cd /d "%~dp0"

set PY=
where py >/dev/null 2>&1 && set PY=py -3
if "%PY%"=="" (where python >/dev/null 2>&1 && set PY=python)
if "%PY%"=="" (
  echo Python 3 wurde nicht gefunden.
  echo Bitte Python 3.8 oder neuer installieren: https://www.python.org/downloads/windows/
  echo Beim Installieren die Option "Add python.exe to PATH" anhaken.
  pause
  exit /b 1
)

echo Starte A/A Steckbrief-Arbeitsplatz ...
%PY% steckbrief_app.py %*
echo.
echo Anwendung beendet.
pause
