#!/bin/bash
# OpenMunicipality: launcher for Linux (run ./iniciar_linux.sh).
# The first run creates a private Python environment (.venv) and installs the
# libraries; later runs start the app straight away in the browser.
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 no está instalado. Descárgalo de https://www.python.org/downloads/"
    read -r -p "Pulsa Intro para salir." _
    exit 1
fi
if [ ! -x .venv/bin/python ]; then
    echo "Preparando OpenMunicipality por primera vez (unos minutos)..."
    python3 -m venv .venv && .venv/bin/python -m pip install -q -r requirements.txt || {
        rm -rf .venv
        read -r -p "No se pudieron instalar las bibliotecas. Pulsa Intro para salir." _
        exit 1
    }
fi
rm -rf modules/__pycache__
exec .venv/bin/python -m streamlit run app.py
