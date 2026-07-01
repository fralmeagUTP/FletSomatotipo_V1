@echo off
cd /d "%~dp0"
setlocal

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
set "API_URL=http://127.0.0.1:8085"

if not exist "%PYTHON_EXE%" (
  echo No se encontro %PYTHON_EXE%
  echo Crea el entorno con: python -m venv .venv
  exit /b 1
)

powershell -NoProfile -Command ^
  "$listener = Get-NetTCPConnection -LocalPort 8085 -State Listen -ErrorAction SilentlyContinue;" ^
  "if (-not $listener) {" ^
  "  Start-Process -FilePath '%PYTHON_EXE%' -ArgumentList '-m','uvicorn','src.backend.main:app','--host','127.0.0.1','--port','8085' -WorkingDirectory '%~dp0' -WindowStyle Hidden" ^
  "}"

timeout /t 2 /nobreak >nul
set "APP_RUNTIME=web"
"%PYTHON_EXE%" web_main.py
