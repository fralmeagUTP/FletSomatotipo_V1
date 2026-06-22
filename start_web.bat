@echo off
cd /d "%~dp0"
setlocal

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
  echo No se encontro %PYTHON_EXE%
  echo Crea el entorno con: python -m venv .venv
  exit /b 1
)

set "APP_RUNTIME=web"
"%PYTHON_EXE%" web_main.py
