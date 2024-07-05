@echo off
REM Activar el entorno virtual
call .\env\Scripts\activate

REM Ejecutar PyInstaller
pyinstaller --windowed --console --add-data "assets/inictel.ico;assets" --add-data "assets/image_home_identiseed.png;assets" --add-data "assets/logo_inictel.png;assets" --add-data "assets/Manual_de_usuario_Software_Identiseed_2024.pdf;assets" -n "identiSeed" app.py

REM Desactivar el entorno virtual
deactivate

echo Ejecutable actualizado.
pause