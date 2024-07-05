#!/bin/bash

# Nombre del archivo Python
PYTHON_FILE="app.py"
# Nombre del ejecutable
EXECUTABLE_NAME="identiseed"

# Crear un entorno virtual (opcional pero recomendado)
#python3 -m venv env

# Activar el entorno virtual
source ./venv/bin/activate

# Instalar pyinstaller si no está instalado
#pip install pyinstaller

# Generar el ejecutable con pyinstaller
pyinstaller --windowed --add-data="assets/inictel.ico:assets" --add-data="assets/image_home_identiseed.png:assets" --add-data="assets/logo_inictel.png:assets" --add-data="assets/Manual_de_usuario_Software_Identiseed_2024.pdf:assets" -n "identiSeed" $PYTHON_FILE

# Mover el ejecutable generado a la ubicación deseada
#mv dist/$EXECUTABLE_NAME ./

# Limpiar archivos temporales generados por pyinstaller
#rm -rf build dist __pycache__ $PYTHON_FILE.spec

# Desactivar el entorno virtual
deactivate