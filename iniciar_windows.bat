@echo off
rem OpenMunicipality: launcher for Windows (double-click).
rem The first run creates a private Python environment (.venv) and installs the
rem libraries; later runs start the app straight away in the browser.
cd /d "%~dp0"
if exist .venv\Scripts\python.exe goto run
echo Preparando OpenMunicipality por primera vez (unos minutos)...
py -3 -m venv .venv 2>nul || python -m venv .venv || goto fail
.venv\Scripts\python -m pip install -q -r requirements.txt || goto fail
:run
if exist modules\__pycache__ rmdir /s /q modules\__pycache__
.venv\Scripts\python -m streamlit run app.py
goto end
:fail
if exist .venv rmdir /s /q .venv
echo No se pudo preparar OpenMunicipality. Instala Python 3 desde https://www.python.org/downloads/
pause
:end
