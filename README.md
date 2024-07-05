# IDENTISEED
## Descripción
Identiseed es un software creado para la identificacion y extraccion de informacion espectral de semillas agricolados, a partir de imagenes hiperespectrales tomadas por la camara Pika II.

## Descripción general de los archivos
El codigo fuente del proyecto esta estructurado de las siguiente manera.

`app.py` - Script de python que contiene el codigo fuente para la creacion de la interfaz de usuario

`utils.py` - Script de python que contiene las funciones principales para el procesamiento del software asi como funciones utilitarias.

`assets` - Carpeta donde se encuentran los iconos usados para la creacion de la interfaz de usuario.


## Instalación Local - Codigo Fuente

Para ejecutar el codigo, clone el repositorio o descomprima el archivo zip, luego ejecute los siguiente comando para instalar las dependencias

```
pip3 install -r requirements.txt
python app.py
```
## Generación de Ejecutable
En Window:
* Abrir CMD
* Mover a la ruta del Proyecto
* Ejecutar el archivo build.bat, escribiendo el nombre en la consolo y presionado enter.

En Linux:
* Abrir Terminal
* Mover a la ruta del Proyecto, con el comando CD.
* Agregar permisos de ejecucion
```
chmod +x build.sh
```
* Ejecutar el build.sh
```
build.sh
```

## Uso del Software
Para usar el software descargue y descomprima el archivo zip, [identiseed.zip](https://drive.google.com/file/d/1V7Zu9COu5CqKmV4Zaac4jvERatSyo_k_/view?usp=sharing)
Luego Ejecute el archivo EXE