import sys
from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar, QCheckBox, 
    QPushButton, QDialog, QDialogButtonBox, 
    QVBoxLayout, QMessageBox, QFileDialog, QScrollArea,
    QHBoxLayout, QLineEdit, QWidget, QGridLayout, QSpacerItem, QSizePolicy, QTabWidget, QProgressBar, QFrame, QComboBox, QSpinBox, QToolButton
)
from PySide6.QtGui import QAction, QIcon, QPaintEvent, QPixmap, QColor, QPainter, QFont, QImage, QDesktopServices
from PySide6.QtCore import QRunnable, Qt, QThread, Signal, QObject, QThreadPool, QUrl
from utils import extract_one_seed_hsi_features, metadata_hsi_image, metadata_image_tiff, morfo_features_extraction, read_bil_file, seed_detection, seeds_extraction, hyperspectral_images_seeds, extract_one_seed_hsi, resource_path
import cv2
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import time
from enum import Enum
import os
import math
import rasterio
import rasterio.sample
import rasterio.vrt
import rasterio._features

class CustomProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_text = ""
        self.start_time = time.time()
        self.elapsed_time = 0
        self.remaining_time = 0
        self.setTextVisible(False)  # Ocultar el texto predeterminado
        #                 border-radius: 5px;
        # 
        # background-color: #07bd04; 
        # border: 2px solid grey;
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                text-align: center;
                margin-top: 0px;
                padding-top:0px;
                margin-left: 7px;
                margin-right: 7px;           
            }
            QProgressBar::chunk {
                background-color: #52cc50;
                margin: 0px;
                width: 10px;
                border-bottom-right-radius: 10px;
                border-bottom-left-radius: 10px;
            }
        """)

    def reset_progres_bar(self):
        self.custom_text = ""
        self.start_time = time.time()
        self.elapsed_time = 0
        self.remaining_time = 0
        self.setTextVisible(False) 

    def set_custom_text(self, text):
        self.custom_text = text
        self.update()

    def update_time(self, value):
        current_time = time.time()
        self.elapsed_time = current_time - self.start_time
        if value > 0:
            total_time = self.elapsed_time * 100 / value
            self.remaining_time = total_time - self.elapsed_time
        else:
            self.remaining_time = 0

        self.update()

    def format_time(self, seconds):
        if seconds >= 3600:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        elif seconds >= 60:
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes}m {seconds}s"
        else:
            return f"{int(seconds)}s"

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        rect = self.rect()
        pen = painter.pen()
        pen.setColor(Qt.black)
        painter.setPen(pen)
        
        if not self.custom_text:
            self.custom_text = f"{self.value()}%"
        
        remaining_time_text = f" - Tiempo restante: {self.format_time(self.remaining_time)}"
        
        painter.drawText(rect, Qt.AlignCenter, self.custom_text + remaining_time_text)
        painter.end()


class ScatterPlotCanvas(FigureCanvas):
    def __init__(self, xvalues, yvalues, title = "", xlabel = "", ylabel = "", parent=None):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.cmap = plt.cm.tab20
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        colores = self.cmap(np.linspace(0, 1, len(self.xvalues)))

        # Crear el gráfico de dispersión con colores personalizados
        scatter = self.ax.scatter(range(1, len(self.xvalues) + 1), self.yvalues, color=colores)

        # Añadir etiquetas a cada punto
        #for i, nombre in enumerate(self.xvalues):
        #    self.ax.text(i + 1, self.yvalues[i], nombre, fontsize=9, ha='left', va='bottom')

        # Crear la leyenda manualmente
        #handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colores[i], markersize=10, label=nombre) for i, nombre in enumerate(self.xvalues)]
        #self.ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1, 1))

        # Añadir etiquetas y título
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_xticks(range(1, len(self.xvalues) + 1))
        self.ax.set_xticklabels(self.xvalues, rotation=45, ha='right')
        self.draw()

class ScatterPlotWiget(QWidget):
    def __init__(self, title = "", xlabel = "", ylabel = "") -> None:
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #f0f0f0;")
        #self.setMinimumSize(400, 300)

        self.canvas = ScatterPlotCanvas(xvalues = [], yvalues = [], title = title, xlabel = xlabel, ylabel = ylabel)
        layout.addWidget(self.canvas)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.desired_height_in_pixels = int(screen_height * 0.20)

        dpi = screen.physicalDotsPerInch()
        print(f"DPI de la pantalla: {dpi}")

        # Convertir 12 pt a píxeles
        pt = 12
        self.px_12pt = pt * dpi / 72

         # Crear área de scroll para la leyenda
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.legend_widget = QWidget()
        self.legend_layout = QGridLayout(self.legend_widget)
        self.scroll_area.setWidget(self.legend_widget)

        self.scroll_area.setFixedHeight(self.px_12pt + 10)
        #self.scroll_area.setMinimumWidth(screen_width * 0.12)

        layout.addWidget(self.scroll_area)
    
    def update_data(self, xvalues = [], yvalues = []):
            self.xnames = [f"semilla-{seed_id}" for seed_id in xvalues]
            self.canvas.xvalues = xvalues
            self.canvas.yvalues = yvalues
            self.canvas.update_plot()
            self.update_legend()

    def update_legend(self):
        # Limpiar la leyenda actual
        for i in reversed(range(self.legend_layout.count())):
            self.legend_layout.itemAt(i).widget().setParent(None)

        # Colores para cada punto usando un colormap
        cmap = plt.cm.tab20
        colores = cmap(np.linspace(0, 1, len(self.xnames)))

        # Añadir cada elemento de la leyenda al layout de la leyenda
        for i, x_val in enumerate(self.xnames):
            color_patch = QLabel()
            color_patch.setStyleSheet(f'background-color: rgba({colores[i][0] * 255}, {colores[i][1] * 255}, {colores[i][2] * 255}, {colores[i][3] * 255});')
            color_patch.setFixedSize(40, 5)
            self.legend_layout.addWidget(color_patch, i, 0)
            self.legend_layout.addWidget(QLabel(x_val), i, 1)
        
        self.adjust_scroll_area_size()
    
    def adjust_scroll_area_size(self):
        # Ajustar la altura del contenedor según el número de elementos
        num_elements = self.legend_layout.count()
        
        new_height = min(self.desired_height_in_pixels, num_elements * self.px_12pt + 10)  # Ajustar este cálculo según tus necesidades
        self.scroll_area.setFixedHeight(new_height)


class MatplotlibPlotWidget(QWidget):
    def __init__(self, xlabel, ylabel, title = None) -> None:
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #f0f0f0;")
        #self.setMinimumSize(400, 300)
        #self.setContentsMargins(0,0,100,100)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas, alignment=Qt.AlignCenter)
        
         # Obtén el tamaño de la pantalla y la densidad de píxeles
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        dpi = screen.physicalDotsPerInch()
        print(f"DPI de la pantalla: {dpi}")

        # Convertir 12 pt a píxeles
        pt = 12
        self.px_12pt = pt * dpi / 72

        # Establece la proporción deseada de la pantalla que la imagen debe ocupar (por ejemplo, 50%)
        #proportion_of_screen = 0.3

        # Calcula el tamaño deseado en píxeles basado en la proporción de la pantalla
        self.desired_width_in_pixels = int(screen_width * 0.20)
        self.desired_height_in_pixels = int(screen_height * 0.20)

        #self.canvas.setFixedSize(self.desired_width_in_pixels, self.desired_height_in_pixels)

        self.title = title
        
        self.xlabel = xlabel
        self.ylabel = ylabel

        if title:
            self.ax.set_title(title)
        
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.legend_widget = QWidget()
        self.legend_layout = QGridLayout(self.legend_widget)
        self.scroll_area.setWidget(self.legend_widget)

        self.scroll_area.setFixedHeight(self.px_12pt + 10)


        self.height_per_line_legend = screen_height * 0.08
        
        #self.scroll_area.setFixedHeight(screen_height * 0.2)
        
        #self.scroll_area.setMinimumWidth(screen_width * 0.12)
        #self.scroll_area.setStyleSheet("background-color: #ffffff")

        #self.layout_scroll_section = QVBoxLayout()

        #self.layout_scroll_section.addWidget(self.scroll_area)

        layout.addWidget(self.scroll_area)
        #self.scroll_area.setVisible(False)
        #self.canvas.setVisible(False)
    
    
  
    def adjust_scroll_area_size(self):
        # Ajustar la altura del contenedor según el número de elementos
        num_elements = self.legend_layout.count()
        
        new_height = min(self.desired_height_in_pixels, num_elements * self.px_12pt + 10)  # Ajustar este cálculo según tus necesidades
        self.scroll_area.setFixedHeight(new_height)

    
    def update_leyend(self):

        # Limpiar la leyenda actual
        for i in reversed(range(self.legend_layout.count())):
            self.legend_layout.itemAt(i).widget().setParent(None)

        for i, line in enumerate(self.ax.get_lines()):
            label_text = line.get_label()
            color = line.get_color()

            # Crear un widget para cada entrada de la leyenda
            color_patch = QLabel()
            color_patch.setFixedSize(40, 5)
            #  padding: 0px; margin: 0px;
            color_patch.setStyleSheet(f"background-color: {color}; border: none;")
            
            self.legend_layout.addWidget(color_patch, i, 0)
            self.legend_layout.addWidget(QLabel(label_text), i, 1)

        self.adjust_scroll_area_size()
       
           
    def update_plot(self, x_data, y_data, labels):
                    
                    #*y_data_labels):
        # Graficamos los datos
        self.canvas.setVisible(True)
        self.scroll_area.setVisible(True)

        self.ax.clear()
        for y_data, label in zip(y_data, labels):
            self.ax.plot(x_data, y_data, label = label)
        
        
        if self.title is not None:
            self.ax.set_title(self.title)

        #ax.

        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.update_leyend()
        #self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        #self.ax.legend(loc='upper left')
        self.canvas.draw()
        #self.adjustSize()
        
    
    def clear_plot(self):
        self.ax.clear()
        self.canvas.setVisible(False)

class MatplotlibWidget(QWidget):
    def __init__(self, xlabel, ylabel, title = None) -> None:
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #f0f0f0;")
        self.setMinimumSize(400, 300)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self.title = title
        
        self.xlabel = xlabel
        self.ylabel = ylabel

        if title:
            self.ax.set_title(title)
        
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

        self.canvas.setVisible(False)
        #self.ax.text(0.5, 0.5, 'Ningua semilla seleccionada', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)


    
    def update_plot(self, x_data, y_data, labels):
                    
                    #*y_data_labels):
        # Graficamos los datos
        self.canvas.setVisible(True)
        self.ax.clear()
        for y_data, label in zip(y_data, labels):
            self.ax.plot(x_data, y_data, label = label)
        
        
        if self.title is not None:
            self.ax.set_title(self.title)

        #ax.

        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        #self.ax.legend(loc='upper left')
        self.canvas.draw()
        
    
    
    def clear_plot(self):
        self.ax.clear()
        self.canvas.setVisible(False)

    #self.ax.plot(x_data, y1_data)


class WorkerSignals(QObject):
    progress_changed = Signal(int, str)
    images_masks = Signal(list, list)  # Señal para emitir datos al hilo principal
    spectrum_data = Signal(object)
    morfo_features = Signal(object)
    


class Worker(QRunnable):

    def __init__(self, 
                 path_rgb_image, 
                 path_hypespect_image,
                 path_white_reference,
                 path_black_reference,
                 grid_seeds_shape = [5,5],
                 hue_range = None, 
                 saturation_range = None, 
                 value_range = None,
                 wavelength = None) -> None:
        super(Worker, self).__init__()

        self.signals = WorkerSignals()
        self.path_rgb_image = path_rgb_image
        self.path_hypespect_image = path_hypespect_image
        self.hue_range = hue_range
        self.saturation_range = saturation_range
        self.value_range = value_range
        self.grid_seeds_shape = grid_seeds_shape
        self.path_white_reference = path_white_reference
        self.path_black_reference = path_black_reference
        self.wavelength = wavelength

    def run(self):
        num_seeds = self.grid_seeds_shape[0] * self.grid_seeds_shape[1]
        self.signals.progress_changed.emit(0, "Procesanto Imagen RGB")

        image_rgb = cv2.imread(self.path_rgb_image)
        
        print("image_rgb.shape: ", image_rgb.shape)

        mask, centro_x, centro_y, ancho, largo, angulo, counter = seed_detection(image_rgb,
                                                                                 grid_seeds_shape = self.grid_seeds_shape,
                                                                                 plot = False, 
                                                                                 hue_range = self.hue_range,
                                                                                 saturation_range= self.saturation_range,
                                                                                 value_range = self.value_range
                                                                                 )
        
        
        
        #self.mask_seeds = mask
        #self.centers_x = centro_x
        self.signals.progress_changed.emit(5, "Procesanto Imagen RGB")
        
        seeds_rgb, seeds_masks, tras_matrix, rot_matrix, roi_seeds = seeds_extraction(self.grid_seeds_shape, mask, image_rgb, centro_x, centro_y, ancho, largo, angulo)
        morfo_features = {}

        self.signals.progress_changed.emit(8, "Extrayendo carateristicas Morfologicas")

        for i in range(num_seeds):
            morfo_features_seed_i = morfo_features_extraction(seeds_rgb[i], seeds_masks[i])
            morfo_features[str(i)] = morfo_features_seed_i

        
        self.signals.progress_changed.emit(10, "Leyendo datos espectrales")
        
        self.signals.images_masks.emit(seeds_rgb, seeds_masks)

        #self.signals.progress_changed.emit(15, "")

        white_bands = read_bil_file(self.path_white_reference)
        self.signals.progress_changed.emit(15, "Leyendo datos espectrales")
        black_bands = read_bil_file(self.path_black_reference)
        self.signals.progress_changed.emit(20, "Leyendo datos espectrales")
        #white_bands,black_bands = black_white("./sample_image/")
        
        frame_bands_correc = hyperspectral_images_seeds(self.path_hypespect_image, correction=True, white_bands=white_bands,black_bands=black_bands)
        
        self.signals.progress_changed.emit(25, "Leyendo datos espectrales")
        
        print("frame_bands_correc.shape: ", frame_bands_correc.shape)
        seeds_spectrum = {}
        dsize = (image_rgb.shape[1], image_rgb.shape[0])
        for i in range(num_seeds):
            mini_mask = seeds_masks[i]
            traslate_matrix = tras_matrix[i]
            rotate_matrix = rot_matrix[i]
            roi_seed = roi_seeds[i]
            y_mean, y_std = extract_one_seed_hsi_features(frame_bands_correc, dsize, mini_mask, traslate_matrix, rotate_matrix, roi_seed)
            
            extract_one_seed_hsi(self.grid_seeds_shape, mask, image_rgb, frame_bands_correc, centro_x, centro_y, ancho, largo, angulo, i + 1, plot= False)
            seeds_spectrum[str(i)] = {"x_long_waves": self.wavelength , "y_mean":  y_mean, "y_std": y_std} 
            self.signals.progress_changed.emit( 25 + (i * 75) / 25, "Extrayendo Caractersiticas Espectrales")

        
        self.signals.morfo_features.emit(morfo_features)
        self.signals.spectrum_data.emit(seeds_spectrum)
        
        self.signals.progress_changed.emit(100, "Finalizado")


class FontType(Enum):
    MAIN_TITLE = QFont("Roboto", 24, QFont.Bold)
    SECTION_TITLE = QFont("Roboto", 16, QFont.Medium)
    SUBSECTION_TITLE = QFont("Roboto", 14, QFont.Normal)
    NORMAL = QFont("Roboto", 14, QFont.Normal)

    def __call__(self):
        return self.value

class Styles:
    MAIN_TITLE = "color: #333333"
    SECTION_TITLE = "color: #555555"
    SUBSECTION_TITLE = "color: #777777"

class HomeWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40,40,40,40)
        #self.setStyleSheet()
        logo_inictel = QLabel()
        logo_inictel.setPixmap(QPixmap(resource_path("assets/logo_inictel.png")).scaled(100,100, Qt.KeepAspectRatio))
        logo_inictel.setStyleSheet("padding-left: 10px")
        title = QLabel("Bienvenido a IdentiSeed")
        title.setFont(QFont("Roboto", 25,  QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding-top: 10px")
        #description = QLabel("Extrae caracteristicas espectrales y morfologicas de semillas a apartir de una imagen hiperpectral")
        #description = QLabel("Procese una imagen hiperespectral de semillas agricolas y extra")
        description = QLabel("Extrae caracteristicas espectrales y morfologicas de semillas agricolas a apartir de una imagen hiperespectral")
        description.setWordWrap(True)
        description.setFont(QFont("Roboto", 14,  QFont.Medium))
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("padding-top: 25px; padding-bottom: 10px")
        imagen_description = QLabel()
        
        pixmap =  QPixmap(resource_path("assets/image_home_identiseed.png"))
        #pixmap = QPixmap("./icons/logo_inictel.png")

        imagen_description.setPixmap(pixmap.scaled(800,800, Qt.KeepAspectRatio))
        imagen_description.setAlignment(Qt.AlignCenter)
        imagen_description.setStyleSheet("padding-top: 20px; padding-bottom: 30px")
        self.button_start = QPushButton("Comenzar")
        self.button_start.setFont(QFont("Roboto", 14,  QFont.Medium))
        self.button_start.setStyleSheet("""
                        QPushButton {
                            background-color: #005A46; /* Color de fondo de los botones */
                            color: white;              /* Color del texto de los botones */
                        }
                        QPushButton:hover {
                            background-color: #004632; /* Color de fondo de los botones al pasar el ratón */
                        }""")
        #     background-color: #004646; 
        #                                color: white;
        
        #spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addWidget(logo_inictel, alignment= Qt.AlignRight)
        main_layout.addWidget(title)
        main_layout.addWidget(description)
        #main_layout.addItem(spacer)
        main_layout.addWidget(imagen_description)
        main_layout.addWidget(self.button_start)

        self.setLayout(main_layout)
    

class ProcessingForm(QWidget):
    def __init__(self,
                 parent = None,  
                 color_boton = None, 
                 color_texto = QColor(0, 0, 0)):
        super(ProcessingForm, self).__init__(parent)

        self.line_edits = []
        self.initUI(color_boton, color_texto)
    
    def initUI(self, 
                color_boton = None, 
                color_texto = QColor(0, 0, 0)):
        # Layout Principal del Fomulario de Importar Imagen
        color_fondo = QColor(250, 250, 250)
        #import_form_widget = QWidget()
        procesing_form_layout = QVBoxLayout()
        
        procesing_form_layout.setContentsMargins(10,10,10,10)
        procesing_form_layout.setSpacing(10)
        procesing_form_layout.setAlignment(Qt.AlignTop)
        
        self.setLayout(procesing_form_layout)
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        self.setMaximumSize(screen_size)

        # Layout de cada campo del formulario

        # Seccion seleccion de imagen
        settings_header = QLabel("Configuración de Extracción de Caracteristicas")
        settings_header.setStyleSheet(Styles.SECTION_TITLE)
        settings_header.setFont(FontType.SECTION_TITLE())
        
        procesing_form_layout.addWidget(settings_header)
        
        self.label_rgb_image, self.input_rgb_image, _ = self.add_file_input(
                            main_layout = procesing_form_layout, 
                            required = True,
                            label_text="Imagen RGB (.tiff)",
                            fn_load_file = self.load_rgb_image,
                            color_boton = color_boton,
                            color_texto= color_texto,
                            filter_files = "Tiff files (*.tif)")
        
        self.label_image_selected = QLabel(alignment = Qt.AlignCenter)
        self.label_image_selected.setVisible(False)
        procesing_form_layout.addWidget(self.label_image_selected)

        self.label_hsi, self.input_hsi, _ = self.add_file_input(
                            main_layout = procesing_form_layout,
                            required = True, 
                            label_text="Imagen Hiperspectral (.bil)",
                            color_boton = color_boton,
                            color_texto= color_texto,
                            filter_files= "BIL files (*.bil)")
        # Linea separadora

        self.add_separator_line(main_layout = procesing_form_layout)

        # Seccion de calibracion
        calibration_sub_header = QLabel("Calibracion de Reflactancia")
        calibration_sub_header.setStyleSheet(Styles.SECTION_TITLE)
        calibration_sub_header.setFont(FontType.SECTION_TITLE())
        procesing_form_layout.addWidget(calibration_sub_header)
#QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","BIL files (*.bil)","BIL Header files (*.bil.hdr)")
# "Tiff files (*.tif)",
# Tiff files (*.tif)
        self.label_white_hsi, self.input_white_hsi, _ = self.add_file_input(
                            main_layout = procesing_form_layout, 
                            required = True,
                            label_text="Blanco de Referencia (.bil)",
                            color_boton = color_boton,
                            color_texto= color_texto,
                            filter_files = "BIL files (*.bil)")
        

        self.label_black_hsi, self.input_black_hsi, _ = self.add_file_input(
                            main_layout = procesing_form_layout,
                            required = True, 
                            label_text="Negro de Referencia (.bil)",
                            color_boton = color_boton,
                            color_texto= color_texto,
                            filter_files = "BIL files (*.bil)")

        self.add_separator_line(main_layout = procesing_form_layout)
        # Seccion de Opciones de de Procesamiento
        options_process_sub_header = QLabel("Opciones de Procesamiento")
        options_process_sub_header.setStyleSheet(Styles.SECTION_TITLE)
        options_process_sub_header.setFont(FontType.SECTION_TITLE())
        procesing_form_layout.addWidget(options_process_sub_header)
        
        method_layout = QHBoxLayout()

        seg_method_label = QLabel("Metodo de Segmentacion:")

        method_combo_box = QComboBox()
        method_combo_box.addItems(["Filtrado por color"])
        method_combo_box.setEnabled(False)
        method_layout.addWidget(seg_method_label)
        method_layout.addWidget(method_combo_box)

        procesing_form_layout.addLayout(method_layout)

        threshold_layout = QHBoxLayout()

        threshold_label = QLabel("Umbral de color (HSV)")

        threshold_layout.addWidget(threshold_label)
           # Crear un QCheckBox
        self.checkbox_auto = QCheckBox("Automatico")
        self.checkbox_auto.setChecked(True)

        threshold_layout.addWidget(self.checkbox_auto)

        # Conectar la señal toggled del QCheckBox a una función
        self.checkbox_auto.toggled.connect(self.on_checkbox_auto_toggled)

        procesing_form_layout.addLayout(threshold_layout)
        ## entrada de Hue 
        hue_layout = QHBoxLayout()

        hue_label = QLabel("Tono (H):")

        min_hue_layout = QHBoxLayout()

        min_hue_layout.setAlignment(Qt.AlignLeft)

        min_hue_label = QLabel("Min:")
        
        self.min_hue_spin_box = QSpinBox()
        self.min_hue_spin_box.setMinimum(0)
        self.min_hue_spin_box.setMaximum(255)
        self.min_hue_spin_box.setValue(10)

        min_hue_layout.addWidget(min_hue_label)
        min_hue_layout.addWidget(self.min_hue_spin_box)
        
        self.max_hue_layout = QHBoxLayout()
        self.max_hue_layout.setAlignment(Qt.AlignLeft)
        
        max_hue_label = QLabel("Max:")

        self.max_hue_spin_box = QSpinBox()
        self.max_hue_spin_box.setMinimum(0)
        self.max_hue_spin_box.setMaximum(255)
        self.max_hue_spin_box.setValue(10)

        self.max_hue_layout.addWidget(max_hue_label)
        self.max_hue_layout.addWidget(self.max_hue_spin_box)

        hue_layout.addWidget(hue_label)
        hue_layout.addLayout(min_hue_layout)
        hue_layout.addLayout(self.max_hue_layout)
        
        procesing_form_layout.addLayout(hue_layout)

        ## entrada de Saturation 
        saturation_layout = QHBoxLayout()

        saturation_label = QLabel("Saturación (S):")

        min_saturation_layout = QHBoxLayout()
        min_saturation_layout.setAlignment(Qt.AlignLeft)
        
        min_saturation_label = QLabel("Min:")
        
        self.min_saturation_spin_box = QSpinBox()
        self.min_saturation_spin_box.setMinimum(0)
        self.min_saturation_spin_box.setMaximum(255)
        self.min_saturation_spin_box.setValue(10)

        min_saturation_layout.addWidget(min_saturation_label)
        min_saturation_layout.addWidget(self.min_saturation_spin_box)
        
        max_saturation_layout = QHBoxLayout()
        max_saturation_layout.setAlignment(Qt.AlignLeft)
        
        max_saturation_label = QLabel("Max:")

        self.max_saturation_spin_box = QSpinBox()
        self.max_saturation_spin_box.setMinimum(0)
        self.max_saturation_spin_box.setMaximum(255)
        self.max_saturation_spin_box.setValue(10)

        max_saturation_layout.addWidget(max_saturation_label)
        max_saturation_layout.addWidget(self.max_saturation_spin_box)

        saturation_layout.addWidget(saturation_label)
        saturation_layout.addLayout(min_saturation_layout)


        saturation_layout.addLayout(max_saturation_layout)
        
        procesing_form_layout.addLayout(saturation_layout)


        ## entrada de Saturation 
        value_layout = QHBoxLayout()
        value_label = QLabel("Brillo (V):")

        min_value_layout = QHBoxLayout()
        min_value_layout.setAlignment(Qt.AlignLeft)

        min_value_label = QLabel("Min:")
        
        self.min_value_spin_box = QSpinBox()
        self.min_value_spin_box.setMinimum(0)
        self.min_value_spin_box.setMaximum(255)
        self.min_value_spin_box.setValue(10)

        min_value_layout.addWidget(min_value_label)
        min_value_layout.addWidget(self.min_value_spin_box)
        
        max_value_layout = QHBoxLayout()
        max_value_layout.setAlignment(Qt.AlignLeft)
        
        max_value_label = QLabel("Max:")

        self.max_value_spin_box = QSpinBox()
        self.max_value_spin_box.setMinimum(0)
        self.max_value_spin_box.setMaximum(255)
        self.max_value_spin_box.setValue(10)

        max_value_layout.addWidget(max_value_label)
        max_value_layout.addWidget(self.max_value_spin_box)

        value_layout.addWidget(value_label)
        value_layout.addLayout(min_value_layout)

        value_layout.addLayout(max_value_layout)
        
        procesing_form_layout.addLayout(value_layout)
        
        self.disable_widgets_hsv_options()
        self.default_values_hsv_options()

        grid_label = QLabel("Grilla de Semillas")
        grid_label.setFont(FontType.SUBSECTION_TITLE())
        grid_label.setStyleSheet(Styles.SUBSECTION_TITLE)

        procesing_form_layout.addWidget(grid_label)

        num_columns_layout = QHBoxLayout()
        num_columns_layout.setAlignment(Qt.AlignLeft)

        num_columns_label = QLabel("Num. Columnas:")

        self.num_columns_spin_box = QSpinBox()
        self.num_columns_spin_box.setMinimum(0)
        self.num_columns_spin_box.setMaximum(50)
        self.num_columns_spin_box.setValue(5)

        num_columns_layout.addWidget(num_columns_label)
        num_columns_layout.addWidget(self.num_columns_spin_box)

        num_row_layout = QHBoxLayout()
        num_row_layout.setAlignment(Qt.AlignLeft)

        num_row_label = QLabel("Num. Filas:")

        self.num_row_spin_box = QSpinBox()
        self.num_row_spin_box.setMinimum(0)
        self.num_row_spin_box.setMaximum(50)
        self.num_row_spin_box.setValue(5)

        num_row_layout.addWidget(num_row_label)
        num_row_layout.addWidget(self.num_row_spin_box)
        
        procesing_form_layout.addLayout(num_columns_layout)
        procesing_form_layout.addLayout(num_row_layout)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), color_fondo)
        self.setPalette(p)
    
    def disable_widgets_hsv_options(self):
        list_input = [
            self.min_hue_spin_box,
            self.max_hue_spin_box,
            self.min_saturation_spin_box,
            self.max_saturation_spin_box,
            self.min_value_spin_box,
            self.max_value_spin_box
            ]
        disabled_style = "background-color: #f0f0f0; color: #808080;"
        
        for w_input in list_input:
            w_input.setEnabled(False)
            # Establecer estilos para los widgets deshabilitados
            w_input.setStyleSheet(disabled_style)

    def default_values_hsv_options(self):
     
        self.min_hue_spin_box.setValue(0)
        self.max_hue_spin_box.setValue(255)

        self.min_saturation_spin_box.setValue(0)
        self.max_saturation_spin_box.setValue(255)
        
        if self.input_rgb_image.text().strip() != "":
            path_rgb_image = self.input_rgb_image.text()
            image_rgb = cv2.imread(path_rgb_image)
            frame_HSV = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2HSV)
            min_v = int(frame_HSV[:, :, 2].mean())
            self.min_value_spin_box.setValue(min_v)
        else:
            self.min_value_spin_box.setValue(0)
    
        self.max_value_spin_box.setValue(255)

    def enable_widgets_hsv_options(self):
        list_input = [
            self.min_hue_spin_box,
            self.max_hue_spin_box,
            self.min_saturation_spin_box,
            self.max_saturation_spin_box,
            self.min_value_spin_box,
            self.max_value_spin_box
            ]
        for w_input in list_input:
            w_input.setEnabled(True)
            # Establecer estilos para los widgets deshabilitados
            w_input.setStyleSheet("")

    def on_checkbox_auto_toggled(self, checked):
        if checked:
            self.disable_widgets_hsv_options()
            self.default_values_hsv_options()
        else:
            self.enable_widgets_hsv_options()
        return

    def add_separator_line(self, main_layout):
        line = QFrame()

        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
    
    def add_file_input(self,
                        main_layout,
                        label_text,
                        required = False,
                        color_texto = QColor(0, 0, 0),
                        color_boton = None,
                        fn_load_file = None,
                        filter_files = ""):
        
        input_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("color: {};".format(color_texto.name()))
        input = QLineEdit()
        selection_button = QPushButton("Seleccionar")
        selection_button.clicked.connect(self.button_open_file(input, filter_files, fn_load_file))
        
        if color_boton is not None:
            selection_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        
        input_layout.addWidget(label)
        
        if required:
            asterisk_label = QLabel("*")
            asterisk_label.setStyleSheet("color: red;")
            asterisk_label.setFont(QFont("Arial", 12, QFont.Bold))
            input_layout.addWidget(asterisk_label)
        
        input_layout.addWidget(input)
        input_layout.addWidget(selection_button)

        main_layout.addLayout(input_layout)

        self.line_edits.append({"input": input, "required": required})
        
        return label, input, selection_button
    

    
    def button_open_file(self, input, filter_files = "", fn_load_file = None):
        def _button_open_file():
            path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".", filter_files,filter_files)
            
            if not path:
                print("Archivo no seleccionado")
            else:
                print("Archivo seleccionado:", path)
                input.setText(path)
                ## Cargar y mostrar image
                
                if fn_load_file is not None:
                    fn_load_file(path)

        return _button_open_file

    def load_rgb_image(self, path):
       
        pixmap = QPixmap(path)
        self.label_image_selected.setPixmap(pixmap.scaled(150,150, Qt.KeepAspectRatio))
        self.label_image_selected.setVisible(True)
        self.default_values_hsv_options()
    

    def validate_filled_form(self):
        for line_edit in self.line_edits:
            if line_edit["input"].text().strip() == "" and line_edit["required"]:
                QMessageBox.warning(self, "Campos Vacios","Por favor, llene todos los campos requeridos.")
                return False
        return True


class ImageGridWidget(QWidget):
    def __init__(self, 
                 background_text = "NINGUNA IMAGEN",
                 image_clickable = True,
                 include_select_all = False,
                 margin_top = 0,
                 margin_bottom = 0,
                 margin_left = 0,
                 margin_right = 0,
                 grid_shape = [5,5]):
        super().__init__()
        self.include_select_all = include_select_all
        self.image_labels = {}
        self.image_clickable = image_clickable
        self.on_image_clicked = None

         # Obtén el tamaño de la pantalla y la densidad de píxeles
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Establece la proporción deseada de la pantalla que la imagen debe ocupar (por ejemplo, 50%)
        proportion_of_screen = 0.095

        # Calcula el tamaño deseado en píxeles basado en la proporción de la pantalla
        self.desired_width_in_pixels = int(screen_width * proportion_of_screen)
        self.desired_height_in_pixels = int(screen_height * proportion_of_screen)

        self.initUI(background_text, margin_top, margin_bottom, margin_left, margin_right)

    
    def update_scroll_size(self):
        print("self.grid_layout.rowCount():", self.grid_layout.rowCount())
        self.scroll_area.setFixedSize(self.desired_height_in_pixels * 5)

    def initUI(self, background_text, margin_top, margin_bottom, margin_left, margin_right):
        #self.setStyleSheet("background-color: rgba(255, 255, 255, 150);")
        
        #self.scroll_area = QScrollArea()
        #self.scroll_area.setFixedSize(self.desired_width_in_pixels * 5, self.desired_height_in_pixels * 5)
        #self.scroll_area.setWidgetResizable(True)
        #self.legend_widget = QWidget()
        #self.legend_layout = QGridLayout(self.legend_widget)
        ##
        #self.grid_layout = QGridLayout(self.legend_widget)
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(margin_left, margin_top, margin_right, margin_bottom)
        self.grid_layout.setSpacing(2)
        ##
        #self.scroll_area.setWidget(self.legend_widget)

        #self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
       
        
        if self.include_select_all:
            self.main_layout = QVBoxLayout()
            self.select_all_checkbox = QCheckBox("Seleccionar todo")
            # Conectar la señal toggled del QCheckBox a una función
            self.select_all_checkbox.toggled.connect(self.on_checkbox_select_all)

            self.main_layout.addWidget(self.select_all_checkbox, alignment = Qt.AlignLeft)
            #self.main_layout.addWidget(self.scroll_area)
            self.main_layout.addLayout(self.grid_layout)
            self.setLayout(self.main_layout)
        else:
         self.setLayout(self.grid_layout)
        
        self.setMaximumHeight(600)
        # Mostrar text in backgroud
        self.no_image_label = QLabel(background_text)
        self.no_image_label.setAlignment(Qt.AlignCenter)
        self.no_image_label.setStyleSheet("font-size: 18px; background-color: rgba(50, 50, 50, 100); color: white;")
        self.no_image_label.setVisible(True)
        self.grid_layout.addWidget(self.no_image_label,0,0,1,1)

    def add_image(self, image_array, row, column, id_label):
        h, w, channels  = image_array.shape
        image_qimage =  QImage(image_array.data, w, h, w * channels, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image_qimage)

        # Creamos un QLabel y establecemos la imagen como su pixmap
        image_label = QLabel()
        image_label.setPixmap(pixmap.scaled(self.desired_width_in_pixels, self.desired_height_in_pixels, Qt.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignCenter)

        # Permitimos que el QLabel sea seleccionable
        if self.image_clickable:
            image_label.setCursor(Qt.PointingHandCursor)
            image_label.mousePressEvent = lambda event: self.image_clicked(
                event, image_label, id_label)
            image_label.setEnabled(False)


        image_label.setToolTip(f'Semilla-{id_label}')

        # Agregamos el QLabel con fondo negro y la imagen al layout
        #self.seeds_grid_layout.addWidget(background_label, row, column, alignment= Qt.AlignCenter)
        self.grid_layout.addWidget(image_label, row, column, alignment= Qt.AlignCenter)
        self.image_labels[id_label] = False

        self.no_image_label.setVisible(False)
        #self.update_scroll_size()

    def on_checkbox_select_all(self, checked):
        if checked:
            self.select_all()
        else:
            self.unselect_all()
        

    def unselect_all(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            widget.setStyleSheet("")
        
        for key in self.image_labels.keys():
            self.image_labels[key] = False

        if self.on_image_clicked:
            self.on_image_clicked(0, self.image_labels)

    def select_all(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            widget.setEnabled(True)
            widget.setStyleSheet("border: 3px solid green;")

        for key in self.image_labels.keys():
            self.image_labels[key] = True

        if self.on_image_clicked:
            self.on_image_clicked(0, self.image_labels)

    def enable_images_clicked(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            widget.setEnabled(True)


    def disable_images_clicked(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            widget.setEnabled(False)

    def clear_images(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.no_image_label.setVisible(True)
    
    def image_clicked(self, event, image_label, id_image):
        self.image_labels[id_image] = not self.image_labels[id_image]

        # Cambiamos el estilo del QLabel cuando se hace clic en él
        if self.image_labels[id_image]:
            image_label.setStyleSheet("border: 3px solid green;")
        else:
            image_label.setStyleSheet("")
            #image_label.setStyleSheet("border: 3px solid black;")
        
        if self.include_select_all and self.select_all_checkbox.isChecked():
            self.select_all_checkbox.setChecked(False)
           
        if self.on_image_clicked:
            self.on_image_clicked(id_image, self.image_labels)
    
    def get_images_clicked_status(self):
        return self.image_labels

    def onImageClicked(self, func):
        self.on_image_clicked = func
    
class PanelFullImage(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        
        
        self.setObjectName("panel-full-image")  # Establecemos un nombre de objeto para el widget

        style = """
            #panel-full-image {
                border: 2px solid #e6e6e6;
                padding: 0px;
                margin: 0px
            }
        """
        
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Establece la proporción deseada de la pantalla que la imagen debe ocupar (por ejemplo, 50%)
        proportion_of_screen = 0.50

        # Calcula el tamaño deseado en píxeles basado en la proporción de la pantalla
        desired_width_in_pixels = int(screen_width * 0.35)
        desired_height_in_pixels = int(screen_height * 0.40)
                                       
        self.setMinimumSize(desired_width_in_pixels, desired_height_in_pixels)

        self.setStyleSheet(style)
      
        self.image_label = QLabel("")
        #self.image_label.setStyleSheet("""background: #e6e6e6""")
        #self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.image_label.setAlignment(Qt.AlignCenter)
        
        self.image_filename_label = QLabel()

        #self.image_label.setMinimumSize(400,400)
        self.image_label.setScaledContents(True)
        main_layout.addWidget(self.image_label, alignment= Qt.AlignHCenter)
        main_layout.addWidget(self.image_filename_label, alignment= Qt.AlignHCenter)
        self.pixmap = None
        self.setLayout(main_layout)
   
    def paintEvent(self, event):
        super().paintEvent(event)
 
    
    def resizeEvent(self, event):
        # Redimensiona el pixmap para que se ajuste al tamaño de la ventana
        if self.pixmap:
            scaled_pixmap = self.pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)
            self.adjustSize()
            super().resizeEvent(event)

    def set_image(self, image_path):
        file_name = os.path.basename(image_path)
        self.image_filename_label.setText(file_name)
        self.pixmap = QPixmap(image_path)


        label_width = self.width()
        print("label_width:", label_width)
        pixmap_ratio = self.pixmap.width() / self.pixmap.height()
        label_height = int(label_width / pixmap_ratio)
        print("label_height:", label_height)
        #self.image_label.setFixedSize(label_width, label_height)
        self.image_label.setPixmap(self.pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio))

        
        self.image_label.setVisible(True)
        self.adjustSize()

    def clean_image(self):
        self.image_filename_label.setText("")


class PanelFileInformation(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        
        self.setObjectName("panel-info-widget")  # Establecemos un nombre de objeto para el widget
        #       /*QLabel {
                   # color: #000000;            /* Color del texto de las etiquetas */
                    #font: normal 14px;           /* Fuente del texto de las etiquetas */
                #}*/
        
        style = """
      
                QPushButton {
                    background-color: #005A46; /* Color de fondo de los botones */
                    color: white;              /* Color del texto de los botones */
                    border: none;
                    padding: 8px 16px;         /* Relleno de los botones */
                    font: bold 12px;           /* Fuente del texto de los botones */
                    border-radius: 8px;        /* Bordes redondeados de los botones */
                }
                QPushButton:hover {
                    background-color: #004632; /* Color de fondo de los botones al pasar el ratón */
                }
                QLineEdit {
                    border: 1px solid; /* Borde de los campos de entrada */
                    padding: 4px;              /* Relleno de los campos de entrada */
                    border-radius: 4px;        /* Bordes redondeados de los campos de entrada */
                }
                                    
            QLineEdit:focus {
                    border: 2px solid #005A46; /* Borde de los campos de entrada */
                }
            
            #panel-info-widget {
                border: 1px solid #e6e6e6;
                padding: 0px;
                margin: 0px
            }
        """
        self.setStyleSheet(style)
        # "font-size: 20px; color: #333; background-color: #f0f0f0; padding: 5px;"
        #title_panel = QLabel("Panel de Informacion")
        #title_panel.setFont(QFont("Roboto", 14, QFont.Bold))
        #title_panel.setFont(FontType.MAIN_TITLE())
        #  font: bold 16px;
        #title_panel.setStyleSheet("""
        #        color: #000000;
        #        background-color: #f0f0f0;
        #        padding: 5px;
        #        margin: 0px                  
        #       """)
        #main_layout.addWidget(title_panel)
        ## Imagen RGB FILE
        info_file_image_label = QLabel("Informacion del Archivo de Image")
        info_file_image_label.setFont(QFont("Roboto", 11, QFont.Bold))
 
        info_file_image_label.setStyleSheet("""color: #333333;""")
        
        resolution_field_label = QLabel("Resolucion:")

        resolution_field_label.setFont(QFont("Roboto", 11, QFont.Normal))
        
        layout_resolution = QHBoxLayout()
        layout_resolution.setAlignment(Qt.AlignLeft)

        layout_resolution.addWidget(resolution_field_label)
       
        self.resolution_value_label = QLabel("")
        self.resolution_value_label.setFont(QFont("Roboto", 11, QFont.Normal))
        layout_resolution.addWidget(self.resolution_value_label)
        
        type_file_field_label = QLabel("Tipo de archivo:")
        type_file_field_label.setFont(QFont("Roboto", 11, QFont.Normal))

        layout_type_file_rgb = QHBoxLayout()
        layout_type_file_rgb.addWidget(type_file_field_label)

        self.type_file_rgb_value = QLabel("")
        self.type_file_rgb_value.setFont(QFont("Roboto", 11, QFont.Normal))
        layout_type_file_rgb.setAlignment(Qt.AlignLeft)
        layout_type_file_rgb.addWidget(self.type_file_rgb_value)

        main_layout.addWidget(info_file_image_label)
        main_layout.addLayout(layout_resolution)
        main_layout.addLayout(layout_type_file_rgb)

        info_file_hsi_label = QLabel("Informacion del Archivo de Imagen Hiperespectral")
        info_file_hsi_label.setFont(QFont("Roboto", 11, QFont.Bold))
        info_file_hsi_label.setStyleSheet("""color: #333333;""")
        
        layout_spectral_range = QHBoxLayout()
        layout_spectral_range.setAlignment(Qt.AlignLeft)
        
        spectral_range_label = QLabel("Rango Espectral:")
        spectral_range_label.setFont(QFont("Roboto", 11, QFont.Normal))
        self.spectral_range_value = QLabel("")
        self.spectral_range_value.setFont(QFont("Roboto", 11, QFont.Normal))
        layout_spectral_range.addWidget(spectral_range_label)
        layout_spectral_range.addWidget( self.spectral_range_value)

        layout_num_bands = QHBoxLayout()
        layout_num_bands.setAlignment(Qt.AlignLeft)

        num_bands_label = QLabel("Numero de Bandas:")
        num_bands_label.setFont(QFont("Roboto", 11, QFont.Normal))
        
        layout_num_bands.addWidget(num_bands_label)
        self.num_bands_value = QLabel("")
        self.num_bands_value.setFont(QFont("Roboto", 11, QFont.Normal))
        layout_num_bands.addWidget(self.num_bands_value)

        layout_type_file_hsi = QHBoxLayout()
        layout_type_file_hsi.setAlignment(Qt.AlignLeft)

        type_file_hsi_field_label = QLabel("Tipo de archivo:")
        type_file_hsi_field_label.setFont(QFont("Roboto", 11, QFont.Normal))
        self.type_file_hsi_value_label = QLabel("")
        self.type_file_hsi_value_label.setFont(QFont("Roboto", 11, QFont.Normal))

        layout_type_file_hsi.addWidget(type_file_hsi_field_label)
        layout_type_file_hsi.addWidget(self.type_file_hsi_value_label)

        main_layout.addWidget(info_file_hsi_label)
        main_layout.addLayout(layout_spectral_range)
        main_layout.addLayout(layout_num_bands)
        main_layout.addLayout(layout_type_file_hsi)

        self.setLayout(main_layout)
        #pass

    def setInfoFileRGB(self, image_shape, format):
        self.resolution_value_label.setText(f"{image_shape[0]}x{image_shape[1]}")
        self.type_file_rgb_value.setText(format.upper())

    def setInfoFileHSI(self, hsi_shape, spec_range, format):
        self.num_bands_value.setText(f"{hsi_shape[2]}")
        min_range = spec_range[0]
        max_range = spec_range[1]
        self.spectral_range_value.setText(f"{min_range}nm - {max_range}nm")
        self.type_file_hsi_value_label.setText(format.upper())

    def paintEvent(self, event):
        super().paintEvent(event)

class FeatureExtractionWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.spectrum_data = None
        self.wavelength = None
        self.initUI()
    
    def initUI(self):
        
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()
        #screen_size = screen.size()
        #self.setMaximumSize(available_geometry.width(), available_geometry.height())

        main_layout = QVBoxLayout()
        main_content_layout = QHBoxLayout()
        
        main_layout.setContentsMargins(0,0,0,10)
        
        self.image_information_seccion_widget = QWidget()
      
        self.image_information_seccion_widget.setStyleSheet("background-color: rgba(255, 255, 255, 100);")

        image_information_layout = QVBoxLayout(self.image_information_seccion_widget)

        panel_image_title = QLabel("Imagen RGB")
        panel_image_title.setFont(QFont("Roboto", 14, QFont.Bold))
        panel_image_title.setStyleSheet("""
                color: #000000;
                background-color: #f0f0f0;
                padding: 5px;
                margin: 0px                  
               """)
        
        self.panel_image_info_widget = PanelFullImage()

        panel_file_info_title = QLabel("Panel de Informacion")
        panel_file_info_title.setFont(QFont("Roboto", 14, QFont.Bold))
        panel_file_info_title.setStyleSheet("""
                color: #000000;
                background-color: #f0f0f0;
                padding: 5px;
                margin: 0px                  
               """)
        
        self.panel_file_info_widget = PanelFileInformation()
        self.panel_file_info_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        image_information_layout.addWidget(panel_image_title)

        image_information_layout.addWidget(self.panel_image_info_widget, alignment= Qt.AlignCenter)
        image_information_layout.addWidget(panel_file_info_title)
        image_information_layout.addWidget(self.panel_file_info_widget)

        main_content_layout.addWidget(self.image_information_seccion_widget)

        #processing_form_widget =  ProcessingForm()
        #main_layout.addWidget(processing_form_widget)
        
        #main_layout.addWidget(self.progress_bar)
        #main_layout.addItem(QSpacerItem(20,20, QSizePolicy.Fixed, QSizePolicy.Minimum))
        
        # Vista de las semillas identificadas
        self.process_view_widget = QWidget()
      
        self.process_view_widget.setStyleSheet("background-color: rgba(255, 255, 255, 100);")
        process_view_layout = QVBoxLayout(self.process_view_widget)
        

        main_content_layout.addWidget(self.process_view_widget)

        tab_widget = QTabWidget()
        process_view_layout.addWidget(tab_widget)

        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Establece la proporción deseada de la pantalla que la imagen debe ocupar (por ejemplo, 50%)
        proportion_of_screen = 0.40

        # Calcula el tamaño deseado en píxeles basado en la proporción de la pantalla
        desired_width_in_pixels = int(screen_width * proportion_of_screen)
        desired_height_in_pixels = int(screen_height * proportion_of_screen)

        #scroll_seeds = QScrollArea()
        #scroll.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        #scroll_seeds.setWidgetResizable(True)

        tab_widget.setMinimumHeight(screen_height * 0.38)
        #tab_widget.setFixedSize(desired_width_in_pixels, desired_height_in_pixels)

        self.seeds_tab = ImageGridWidget(background_text="Ninguna Semilla Identificada", include_select_all= True)
        
        #scroll_seeds.setWidget(self.seeds_tab)

        self.seeds_tab.onImageClicked(lambda id_image, images_checked: self.show_features(images_checked))
        
        self.masks_tab = ImageGridWidget(background_text="Ninguna Semilla Identificada", image_clickable = False, margin_right=10,  margin_left=10, margin_bottom = 10, margin_top=25)

        tab_widget.addTab(self.seeds_tab, "Semillas")
        tab_widget.addTab(self.masks_tab, "Mascaras")

        tab_widget.setStyleSheet("""QTabWidget QTabBar::tab {
            font-family: Arial;
            font-size: 13pt;
            font-weight: bold;
            color: #000000;                     
        }""")
   
        tab_features_data = QTabWidget()

        tab_features_data.setObjectName("outerTabWidget")

        
        tab_hci_data = QTabWidget()
        tab_hci_data.setStyleSheet("""
        QTabBar::tab {
            font-family: Arial;
            font-size: 11pt;
            font-weight: normal;
            color: #000000;
        }
    """)
        #tab_hci_data.setSizePolicy(QSizePolicy.Spanding, QSizePolicy.Minimum)
        #tab_hci_data.setStyleSheet()
        tab_hci_data.setMinimumSize(screen_width * 0.57, screen_height * 0.43)
        #tab_features_data.setMinimumSize(screen_width * 0.55, screen_height * 0.40)
        tab_features_data.addTab(tab_hci_data, "Caracteristicas Espectrales")

        #desired_width_in_pixels = int(screen_width * proportion_of_screen)
        #desired_height_in_pixels = int(screen_height * 0.35)

        #tab_hci_data.setFixedSize(desired_width_in_pixels, desired_height_in_pixels)
        tab_hci_data.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        process_view_layout.addWidget(tab_features_data)
        
        ## Tab de grafico de avg 
        self.spectrum_avg_plot = MatplotlibPlotWidget(xlabel="Longitud de onda", ylabel="Radiancia")

        tab_hci_data.addTab(self.spectrum_avg_plot, "Espectro (Promedio)")
        ## Tab de grafico de desviacion estandar 
        self.spectrum_std_plot = MatplotlibPlotWidget(xlabel="Longitud de onda", ylabel="Radiancia")

        tab_hci_data.addTab(self.spectrum_std_plot, "Espectro (Des. Estandar)")

        tab_morfo_features = QTabWidget()
        
        tab_morfo_features.setStyleSheet("""
        QTabBar::tab {
            font-family: Arial;
            font-size: 11pt;
            font-weight: normal;
            color: #000000;
        }
    """)
        
        self.morfo_area = ScatterPlotWiget(xlabel="ID Semilla", ylabel= "Área (pixels)")
        self.morfo_perimeter = ScatterPlotWiget(xlabel="ID Semilla", ylabel= "Perímetro (pixels)")
        self.morfo_ratio = ScatterPlotWiget(xlabel="ID Semilla", ylabel= "Relación de aspecto (pixels)")
        
        #self.morfo_area.update_data(xvalues=["1", "2"], yvalues = [32, 42])

        tab_morfo_features.addTab(self.morfo_area, "Área (pixeles)")
        tab_morfo_features.addTab(self.morfo_perimeter, "Perímetro (pixeles)")
        tab_morfo_features.addTab(self.morfo_ratio, "Relación de aspecto (pixeles)")
        
        tab_features_data.addTab(tab_morfo_features, "Caracteristicas Morfologias")

        
        self.progress_bar = CustomProgressBar(self)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addLayout(main_content_layout)
        main_layout.addWidget(self.progress_bar, alignment= Qt.AlignTop)
        
        self.setStyleSheet("""
        #outerTabWidget QTabBar::tab {
            font-family: Arial;
            font-size: 13pt;
            font-weight: bold;
            color: #000000;
        }
    """)
        
        self.setLayout(main_layout)

    def setSpectrumData(self, data):
        self.spectrum_data = data
    
    def setMorfoFeatures(self, data):
        print("\nmorfo_features:", data)
        self.morfo_features = data

    def setWavelength(self, wavelength):
        self.wavelength = wavelength

    def desableSelectAll(self):
        self.seeds_tab.select_all_checkbox.setEnabled(False)
    
    def enableSelectAll(self):
        self.seeds_tab.select_all_checkbox.setEnabled(True)

    def show_morfo_features(self, image_ids):
        y_area = []
        y_perimeter = []
        y_ratio = []
        for id_image in image_ids:
            seed_features = self.morfo_features[str(id_image)]
            y_area.append(seed_features["area"])
            y_perimeter.append(seed_features["perimetro"])
            y_ratio.append(seed_features["relacion_aspecto"])
        
        xvalues = [str(im_id) for im_id in image_ids ]
        
        self.morfo_area.update_data(xvalues = xvalues, yvalues = y_area)
        self.morfo_perimeter.update_data(xvalues = xvalues, yvalues = y_perimeter)
        self.morfo_ratio.update_data(xvalues = xvalues, yvalues = y_ratio)

    def show_features(self, images_checked):
        images_clicked_ids = [ key for key, value in images_checked.items() if value]
      
        if self.wavelength:
            x = self.wavelength
        elif self.spectrum_data:
            x = self.spectrum_data['0']["x_long_waves"]
        else:
            return

        y_mean_data = []
        y_std_data = []
        seed_labels = []


        for image_id in images_clicked_ids:
            y_mean = self.spectrum_data[str(image_id)]["y_mean"]
            y_std = self.spectrum_data[str(image_id)]["y_std"]
            seed_label = f"semilla-{image_id}"

            y_mean_data.append(y_mean)
            y_std_data.append(y_std)
            seed_labels.append(seed_label)
        
        self.spectrum_avg_plot.update_plot(x_data=x, y_data = y_mean_data, labels=seed_labels)
        self.spectrum_std_plot.update_plot(x_data=x, y_data = y_std_data, labels=seed_labels)

        self.show_morfo_features(images_clicked_ids)


    def button_show_spectrum(self):
        #Crear y agregar el gráfico dentro de la sección del gráfico
    
        # Actualizar el gráfico de barras
        #self.canvas_avg_graph.setVisible(True)
        #self.ax_avg.clear()
        images_clicked_status = self.seeds_tab.get_images_clicked_status()
        images_clicked_ids = [ key for key, value in images_clicked_status.items() if value]
        if len(images_clicked_ids) > 0:
            #self.ax.hist(file_sizes, bins=20, alpha=0.7, color='blue')
            x = self.spectrum_data[str(images_clicked_ids[0])]["x_long_waves"]
            y_mean_data = []
            y_std_data = []
            seed_labels = []
                    
            for image_id in images_clicked_ids:
                y_mean = self.spectrum_data[str(image_id)]["y_mean"]
                y_std = self.spectrum_data[str(image_id)]["y_std"]
                seed_label = f"semilla-{image_id}"

                y_mean_data.append(y_mean)
                y_std_data.append(y_std)
                seed_labels.append(seed_label)
            
            self.spectrum_avg_plot.update_plot(x_data=x, y_data = y_mean_data, labels=seed_labels)
            self.spectrum_std_plot.update_plot(x_data=x, y_data = y_std_data, labels=seed_labels)
            #self.ax_avg.set_title('Spectrum (avg)')
            #self.ax_avg.set_xlabel('Longitudes de Onda Luz')
            #self.ax_avg.set_ylabel('Reflectance Mean')
            
        #else:
            #self.ax_avg.text(0.5, 0.5, 'Ningua semilla seleccionada', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
            #self.canvas_avg_graph.draw()
        return
    
    def download_csv_spectrum(self):
        #options = QFileDialog.Options()
        #ptions |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Seleccionar archivo o carpeta", "", "CSV Files (*.csv);;All Files (*)")
        if fileName:
            # Verificar si el nombre del archivo tiene la extensión .csv
            if not fileName.endswith(".csv"):
                # Agregar la extensión .csv si no está presente
                fileName += ".csv"
            print("Archivo seleccionado:", fileName)

            ## Guardar archivo
            x_long_waves = self.spectrum_data['0']['x_long_waves']

            columns = ["seed_id"] +  [f"media_band_{lw}" for lw in x_long_waves] + [ f"desv_estandar_band_{lw}" for lw in x_long_waves]
            
            print("\nself.spectrum_data:", self.spectrum_data)
            data = [ [id_seed] + seed_data["y_mean"].tolist() + seed_data["y_std"].tolist() for id_seed , seed_data in self.spectrum_data.items()]
            print()
            print("\ndata[0]:", data[0]) 
            df = pd.DataFrame(data, columns = columns)
            print(df)
            df.to_csv(fileName, index= False)

    
    def setImageSeeds(self, seeds_rgb, seeds_masks):
        self.seeds_rgb = seeds_rgb
        self.seeds_masks = seeds_masks
        self.show_images_masks(seeds_rgb, seeds_masks)
    
    def show_images_masks(self, seeds_rgb, seeds_masks):
        # Crear un Worker y conectar la señal del Worker a los métodos de actualización de la interfaz de usuario
        
        for i in range(len(seeds_rgb)):
            seed_image = seeds_rgb[i]
            # completar fondo negro
            h_seed, w_seed, _ = seed_image.shape
            # Calcular la dimension maxima para hacer el fondo cuadrado
            max_dimension = max(h_seed, w_seed)
            # Crear una imagen negra cuadrada
            black_frame = np.zeros((max_dimension, max_dimension, 3), dtype=np.uint8)
            # Calcular las coordenadas para colocar la imagen original
            inicio_y = (max_dimension - h_seed) // 2
            inicio_x = (max_dimension - w_seed) // 2
            # superponer imagen a frame negro
            black_frame[inicio_y: inicio_y + h_seed, inicio_x: inicio_x + w_seed] = seed_image
    
            black_frame = cv2.cvtColor(black_frame, cv2.COLOR_BGR2RGB)
            column = i % 5
            row = i // 5
            self.seeds_tab.add_image(black_frame, row, column, i)

            seed_mask = seeds_masks[i]

            mask_black_frame = np.zeros((max_dimension, max_dimension, 3), dtype=np.uint8)
            mask_black_frame[inicio_y: inicio_y + h_seed, inicio_x: inicio_x + w_seed, :] = seed_mask[..., np.newaxis]
            self.masks_tab.add_image(mask_black_frame, row, column, i)
        
        self.seeds_tab.adjustSize()
    
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()
        #screen_size = screen.size()
        self.setMaximumSize(available_geometry.width(), available_geometry.height())
        
        self.setWindowTitle("IdentiSeed")
        #self.setStyleSheet("""background-color: #ffffff;""")
        self.setStyleSheet("""
        QMenuBar::item:selected { /* Cuando el cursor pasa sobre la acción */
                background-color: #2e8b57; /* Verde oscuro */
                color: #ffffff;
            }
        QMenu::item:selected { /* Cuando el cursor pasa sobre la acción */
                background-color: #2e8b57;
                color: #ffffff;
            }""")
        
        # Cargar la imagen del icono
        icon = QIcon(resource_path("assets/inictel.ico"))

        self.setWindowIcon(icon)
        self.setGeometry(0, 0, 500, 200)
        #self.setGeometry(100, 100, 500, 200)
        
        # Main Layout Principal
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignTop)

        main_content_layout = QHBoxLayout()
       
        #main_layout.setContentsMargins(20,20,20,20)
        ## Menu
        menu = self.menuBar()
        file_menu = menu.addMenu("Archivo")
        button_action_file1 = QAction("Exportar Caracteristicas Extraidas", self)
        button_action_file1.setStatusTip("Exportar Caracteristicas Extraidas")
        button_action_file1.triggered.connect(self.on_save_data_spectral)
        file_menu.addAction(button_action_file1)

        process_menu = menu.addMenu("Procesamiento")
        button_action_process1 = QAction("Extraccion de Caracteristicas", self)
        button_action_process1.setStatusTip("Extraccion de Caracteristicas")
        button_action_process1.triggered.connect(self.on_extract_spectral_feactures)
        process_menu.addAction(button_action_process1)

        help_menu = menu.addMenu("Ayuda")
        button_action_help1 = QAction("Manual", self)
        button_action_help1.setStatusTip("Manual")
        button_action_help1.triggered.connect(self.on_dowload_manual)
        help_menu.addAction(button_action_help1)
                
      
        self.home_window = HomeWindow()
        self.home_window.button_start.clicked.connect(self.on_extract_spectral_feactures)

        self.feature_extraction_window = FeatureExtractionWindow()
        self.feature_extraction_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.home_window)
        
        
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("""background-color: #ffffff;""")
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
    
    def show_feature_extraction_window(self):
        self.setGeometry(20, 20, 500, 200)
        # Reemplazar el widget actual por widget1
        self.main_layout.removeWidget(self.home_window)
        self.home_window.setParent(None)
        self.main_layout.addWidget( self.feature_extraction_window)

    def on_dowload_manual(self):
        # Ruta al archivo PDF del manual de usuario
        pdf_path = resource_path("assets/Manual_de_usuario_Software_Identiseed_2024.pdf")

        # Abre el PDF en el visor predeterminado del sistema
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path)):
            QMessageBox.critical(self, "Error", "No se pudo abrir el manual de usuario.")

        #self.download_csv_spectrum()
        return ""
    
    def on_extract_spectral_feactures(self):
        self.dialog =  QDialog(self)
        
        self.dialog.setWindowTitle(" ")
        self.dialog.setWindowIcon(QIcon())

        self.dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;  /* Color de fondo del diálogo */
                /*border: 2px solid #0078d7;*/  /* Borde del diálogo */
                border-radius: 10px;        /* Bordes redondeados */
            }
            QLabel {
                color: #000000;            /* Color del texto de las etiquetas */
                font: bold 14px;           /* Fuente del texto de las etiquetas */
            }
            QPushButton {
                background-color: #005A46; /* Color de fondo de los botones */
                color: white;              /* Color del texto de los botones */
                border: none;
                padding: 8px 16px;         /* Relleno de los botones */
                font: bold 12px;           /* Fuente del texto de los botones */
                border-radius: 8px;        /* Bordes redondeados de los botones */
            }
            QPushButton:hover {
                background-color: #004632; /* Color de fondo de los botones al pasar el ratón */
            }
            QLineEdit {
                border: 1px solid; /* Borde de los campos de entrada */
                padding: 4px;              /* Relleno de los campos de entrada */
                border-radius: 4px;        /* Bordes redondeados de los campos de entrada */
            }
                                  
           QLineEdit:focus {
                border: 2px solid #005A46; /* Borde de los campos de entrada */
            }
        """)
        
        ## Dialog layout
        dialog_layout = QVBoxLayout()
        
        dialog_layout.setAlignment(Qt.AlignTop)

        self.process_form_dialog = ProcessingForm(color_boton = None)
        dialog_layout.addWidget(self.process_form_dialog)

        button_dialog_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancelar")
        apply_button = QPushButton("Aplicar")

        cancel_button.clicked.connect(self.dialog.reject)
        apply_button.clicked.connect(self.process_extract_features)
        
        button_dialog_layout.addWidget(cancel_button)
        button_dialog_layout.addWidget(apply_button)

        dialog_layout.addLayout(button_dialog_layout)

        self.dialog.setLayout(dialog_layout)
        self.dialog.exec()

        return ""

    def process_extract_features(self):
        if self.process_form_dialog.validate_filled_form():
            
            self.show_feature_extraction_window()
            self.feature_extraction_window.progress_bar.reset_progres_bar()
            self.feature_extraction_window.desableSelectAll()

            path_rgb_image = self.process_form_dialog.input_rgb_image.text()
            self.feature_extraction_window.panel_image_info_widget.set_image(path_rgb_image)
            image_shape, type_file = metadata_image_tiff(path_rgb_image)
            self.feature_extraction_window.panel_file_info_widget.setInfoFileRGB(image_shape, type_file)
            
            path_hypespect_image = self.process_form_dialog.input_hsi.text()
            hsi_shape, type_file_hsi, wavelength = metadata_hsi_image(path_hypespect_image)
            print("wavelength:", wavelength)
            wavelength = [float(v) for v in wavelength]
            spectral_range = [math.ceil( wavelength[0] / 10)*10,  math.ceil(wavelength[-1] / 10)*10]

            self.feature_extraction_window.panel_file_info_widget.setInfoFileHSI(hsi_shape, spectral_range, type_file_hsi)
            
            self.feature_extraction_window.setWavelength(wavelength)

            ## AQUI GET METADA 
            auto_filter_hsv = self.process_form_dialog.checkbox_auto.isChecked()
            
            num_row = self.process_form_dialog.num_row_spin_box.value()
            num_colum = self.process_form_dialog.num_columns_spin_box.value()

            grid_seeds_shape = (num_row, num_colum)

            path_white_reference = self.process_form_dialog.input_white_hsi.text()
            path_black_reference = self.process_form_dialog.input_black_hsi.text()

            print("grid_seeds_shape:", grid_seeds_shape)

            #self.wavelength = wavelength

            if auto_filter_hsv:
                worker = Worker(path_rgb_image, 
                                path_hypespect_image, 
                                grid_seeds_shape = grid_seeds_shape, 
                                path_white_reference = path_white_reference,
                                path_black_reference = path_black_reference,
                                wavelength = wavelength)
            else:

                hue_range = (self.process_form_dialog.min_hue_spin_box.value(), 
                             self.process_form_dialog.max_hue_spin_box.value())
                
                saturation_range = (self.process_form_dialog.min_saturation_spin_box.value(), 
                             self.process_form_dialog.max_saturation_spin_box.value())
                
                value_range = (self.process_form_dialog.min_value_spin_box.value(), 
                             self.process_form_dialog.max_value_spin_box.value())
                
                worker = Worker(path_rgb_image, 
                                path_hypespect_image, 
                                hue_range, 
                                saturation_range, 
                                value_range, 
                                grid_seeds_shape = grid_seeds_shape,
                                path_white_reference = path_white_reference,
                                path_black_reference = path_black_reference,
                                wavelength = wavelength)
            
            worker.signals.progress_changed.connect(self.update_progress)
            worker.signals.images_masks.connect(self.feature_extraction_window.setImageSeeds)
            worker.signals.spectrum_data.connect(self.recive_spectrum_data)
            worker.signals.morfo_features.connect(self.recive_morfo_features)
            
            self.threadpool.start(worker)

            self.dialog.accept()
        return ""
    
    def on_save_data_spectral(self):
        self.download_csv_spectrum()
        return ""
    
    def download_csv_spectrum(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Seleccionar archivo o carpeta", "", "CSV Files (*.csv);;All Files (*)")
        if fileName:
            # Verificar si el nombre del archivo tiene la extensión .csv
            if not fileName.endswith(".csv"):
                # Agregar la extensión .csv si no está presente
                fileName += ".csv"
            print("Archivo seleccionado:", fileName)

            ## Guardar archivo
            x_long_waves = self.spectrum_data['0']['x_long_waves']

            columns = ["seed_id"] +  [f"media_band_{lw}" for lw in x_long_waves] + [ f"desv_estandar_band_{lw}" for lw in x_long_waves]
    
            morfo_features_name = ["área", "perímetro ","relación_de_aspecto"]
            columns = columns + morfo_features_name

            #print("\nself.spectrum_data:", self.spectrum_data)
            data = []
            for id_seed , seed_data in self.spectrum_data.items():
                row_values =  [id_seed] + seed_data["y_mean"].tolist() + seed_data["y_std"].tolist()
                seed_morfo_features =  self.morfo_features[id_seed]
                row_values = row_values + [seed_morfo_features["area"], seed_morfo_features["perimetro"], seed_morfo_features["relacion_aspecto"]]
                data.append(row_values)

                        
            print()
            print("\ndata[0]:", data[0]) 
            df = pd.DataFrame(data, columns = columns)
            print(df)
            df.to_csv(fileName, index= False)
            
    
    def update_progress(self, value, status):
        text = f"{status}: {value}% completado"
        self.feature_extraction_window.progress_bar.setValue(value)
        self.feature_extraction_window.progress_bar.set_custom_text(text)
        self.feature_extraction_window.progress_bar.update_time(value)

    def button_show_spectrum(self):
        #Crear y agregar el gráfico dentro de la sección del gráfico
     
        # Actualizar el gráfico de barras
        #self.canvas_avg_graph.setVisible(True)
        #self.ax_avg.clear()
        images_clicked_status = self.seeds_tab.get_images_clicked_status()
        images_clicked_ids = [ key for key, value in images_clicked_status.items() if value]
        if len(images_clicked_ids) > 0:
            #self.ax.hist(file_sizes, bins=20, alpha=0.7, color='blue')
            x = self.spectrum_data[str(images_clicked_ids[0])]["x_long_waves"]
            y_mean_data = []
            y_std_data = []
            seed_labels = []
                      
            for image_id in images_clicked_ids:
                y_mean = self.spectrum_data[str(image_id)]["y_mean"]
                y_std = self.spectrum_data[str(image_id)]["y_std"]
                seed_label = f"semilla-{image_id}"

                y_mean_data.append(y_mean)
                y_std_data.append(y_std)
                seed_labels.append(seed_label)
            
            self.spectrum_avg_plot.update_plot(x_data=x, y_data = y_mean_data, labels=seed_labels)
            self.spectrum_std_plot.update_plot(x_data=x, y_data = y_std_data, labels=seed_labels)
            #self.ax_avg.set_title('Spectrum (avg)')
            #self.ax_avg.set_xlabel('Longitudes de Onda Luz')
            #self.ax_avg.set_ylabel('Reflectance Mean')
            
        #else:
            #self.ax_avg.text(0.5, 0.5, 'Ningua semilla seleccionada', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
            #self.canvas_avg_graph.draw()

        return 

    def recive_spectrum_data(self, spectrum_data):
        
        self.spectrum_data = spectrum_data
        self.feature_extraction_window.setSpectrumData(self.spectrum_data)
        
        self.feature_extraction_window.seeds_tab.enable_images_clicked()
        self.feature_extraction_window.seeds_tab.select_all()
        
        images_checked = self.feature_extraction_window.seeds_tab.get_images_clicked_status()
        self.feature_extraction_window.show_features(images_checked)

        self.feature_extraction_window.enableSelectAll()

    def recive_morfo_features(self, morfo_features):
        self.morfo_features = morfo_features
        self.feature_extraction_window.setMorfoFeatures(self.morfo_features)


    def process_finished(self, result):
        # Este método se llama cuando el proceso en segundo plano ha terminado
        self.import_button.setEnabled(True)
        print("Proceso terminado")
      

app = QApplication(sys.argv)
app.setStyle("Fusion")
window = MainWindow()
#window.resize(300, 200)

screen_geometry = app.primaryScreen().geometry()
screen_width = screen_geometry.width()
screen_height = screen_geometry.height()

# Obtiene el tamaño de la ventana
window_width = window.width()
window_height = window.height()

# Calcula las coordenadas x y y para centrar la ventana
x = (screen_width - window_width) // 4 + 10
y = (screen_height - window_height) // 8

print("x:", x)
print("screen_width:", screen_width)
print("window_width:", window_width)
# Mueve la ventana al centro de la pantalla
window.move(x, y)

window.show()
app.exec()