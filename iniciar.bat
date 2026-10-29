@echo off
chcp 65001 >nul
cd /d "%~dp0"
title ProgLucia

where python >nul 2>nul
if errorlevel 1 (
    echo No encuentro Python. Instala Python 3.10 o superior desde python.org
    echo y marca "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Primera vez: preparando el entorno, tarda un par de minutos...
    python -m venv .venv
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)
rem si vienes de una version anterior, esto actualiza lo que haga falta (es rapido si ya esta todo)
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt

echo Abriendo ProgLucia en el navegador... (cierra esta ventana para apagarla)
start "" /min cmd /c "timeout /t 6 /nobreak >nul & start http://localhost:8501"
".venv\Scripts\python.exe" -m streamlit run app.py
pause
