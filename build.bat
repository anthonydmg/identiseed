@echo off
REM Activar el entorno virtual
call .\env\Scripts\activate

REM Ejecutar PyInstaller
pyinstaller --onefile --console --add-data "assets/inictel.ico;assets" --add-data "assets/image_home_identiseed.png;assets" --add-data "assets/logo_inictel.png;assets" --add-data "assets/Manual-Usuario-IdentiTree.pdf;assets" --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets app.py

REM Desactivar el entorno virtual
deactivate

echo Ejecutable actualizado.
pause