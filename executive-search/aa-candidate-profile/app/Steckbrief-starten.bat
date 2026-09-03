@echo off
setlocal EnableExtensions
title A/A Steckbrief-Arbeitsplatz

rem Wechsel in den Ordner dieser Datei. pushd kommt auch mit Netz- und
rem OneDrive-Pfaden zurecht, cd /d nicht immer.
pushd "%~dp0" 2>nul
if errorlevel 1 (
  echo FEHLER: Konnte nicht in den Programmordner wechseln.
  echo Pfad: %~dp0
  echo.
  echo Bitte den Ordner aus der ZIP-Datei nach Dokumente entpacken
  echo und die Datei dort starten, nicht direkt in der ZIP-Ansicht.
  echo.
  pause
  exit /b 1
)

echo Arbeitsordner: %CD%

if not exist "steckbrief_app.py" (
  echo FEHLER: steckbrief_app.py liegt nicht in diesem Ordner.
  echo Die Datei Steckbrief-starten.bat muss im Ordner "app" liegen,
  echo und daneben muss der Ordner "scripts" stehen.
  echo.
  pause
  popd
  exit /b 1
)

set "PYEXE="
set "PYARG="

rem %ProgramFiles(x86)% enthaelt selbst Klammern. Direkt in einer
rem for/in-Klammerliste verwendet, verwechselt der Batch-Parser die
rem erste schliessende Klammer aus "(x86)" mit dem Ende der Liste.
rem Deshalb vorher in eine klammerfreie Variable kopieren.
set "PF86=%ProgramFiles(x86)%"

rem Schritt 1: der Python-Launcher py, der Normalfall bei einer Installation von python.org
call :pruefe "py" "-3"
if not defined PYEXE call :pruefe "python" ""
if not defined PYEXE call :pruefe "python3" ""

rem Schritt 2: uebliche Installationsorte direkt absuchen, falls PATH nicht gesetzt wurde
if not defined PYEXE for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
  if not defined PYEXE call :pruefe "%%~D\python.exe" ""
)
if not defined PYEXE for /d %%D in ("%ProgramFiles%\Python3*") do (
  if not defined PYEXE call :pruefe "%%~D\python.exe" ""
)
if not defined PYEXE for /d %%D in ("%PF86%\Python3*") do (
  if not defined PYEXE call :pruefe "%%~D\python.exe" ""
)
if not defined PYEXE for /d %%D in ("C:\Python3*") do (
  if not defined PYEXE call :pruefe "%%~D\python.exe" ""
)
if not defined PYEXE call :pruefe "%LOCALAPPDATA%\Programs\Python\Launcher\py.exe" "-3"

if not defined PYEXE goto :keinpython

echo Python gefunden: %PYEXE% %PYARG%
echo Starte A/A Steckbrief-Arbeitsplatz ...
echo Dieses Fenster bitte offen lassen. Beenden mit Strg+C.
echo.
"%PYEXE%" %PYARG% steckbrief_app.py %*
set "CODE=%ERRORLEVEL%"
echo.
if not "%CODE%"=="0" echo Die Anwendung endete mit Fehlercode %CODE%.
echo Anwendung beendet.
popd
pause
exit /b %CODE%

rem ---------------------------------------------------------------
:pruefe
rem %~1 = Programm, %~2 = zusaetzliches Argument. Setzt PYEXE, wenn
rem sich damit ein Python ab Version 3.8 wirklich starten laesst.
rem Der Microsoft-Store-Platzhalter faellt hier durch, weil er kein
rem Programm ausfuehrt und einen Fehlercode liefert.
"%~1" %~2 -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if errorlevel 1 goto :eof
set "PYEXE=%~1"
set "PYARG=%~2"
goto :eof

rem ---------------------------------------------------------------
:keinpython
echo.
echo ============================================================
echo  Python 3.8 oder neuer wurde auf diesem Rechner nicht gefunden.
echo ============================================================
echo.
echo So beheben Sie das:
echo.
echo  1. https://www.python.org/downloads/windows/ oeffnen
echo  2. "Download Python 3.x" anklicken und den Installer starten
echo  3. WICHTIG: unten im Installer den Haken bei
echo     "Add python.exe to PATH" setzen, bevor Sie auf Install klicken
echo  4. Danach diese Datei erneut per Doppelklick starten
echo.
echo Falls Python schon installiert ist: den Installer erneut starten,
echo "Modify" waehlen und sicherstellen, dass "py launcher" aktiv ist.
echo.
echo ------------------------- Diagnose -------------------------
echo Arbeitsordner: %CD%
echo.
echo Suche nach py:
where py 2>&1
echo.
echo Suche nach python:
where python 2>&1
echo.
echo Installationsordner:
if exist "%LOCALAPPDATA%\Programs\Python" (dir /b "%LOCALAPPDATA%\Programs\Python" 2>&1) else (echo   nicht vorhanden: %LOCALAPPDATA%\Programs\Python)
echo.
echo Wenn es danach immer noch klemmt, bitte dieses ganze Fenster
echo abfotografieren und an Claude schicken.
echo ------------------------------------------------------------
echo.
popd
pause
exit /b 1
