import sys
from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar, QCheckBox, 
    QPushButton, QDialog, QDialogButtonBox, 
    QVBoxLayout, QMessageBox, QFileDialog,
    QHBoxLayout, QLineEdit, QWidget, QGridLayout, QSpacerItem, QSizePolicy, QTabWidget, QProgressBar, QFrame, QComboBox, QSpinBox, QToolButton
)
from PySide6.QtGui import QAction, QIcon, QPaintEvent, QPixmap, QColor, QPainter, QFont, QImage
from PySide6.QtCore import QRunnable, Qt, QThread, Signal, QObject, QThreadPool
from utils import black_white, extract_one_seed_hsi_features, seed_detection, seeds_extraction, one_seed, hyperspectral_images_seeds, long_onda, extract_one_seed_hsi
import cv2
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import pandas as pd
import time
from enum import Enum

class CustomProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_text = ""
        self.start_time = time.time()
        self.elapsed_time = 0
        self.remaining_time = 0
        self.setTextVisible(False)  # Ocultar el texto predeterminado
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00FF00;  # Color verde
                width: 20px;
            }
        """)

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


class MatplotlibWidget(QWidget):
    def __init__(self, xlabel, ylabel, title = None) -> None:
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #f0f0f0;")
        self.setMinimumSize(600, 300)

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
    
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.legend(loc='upper left')
        self.canvas.draw()
        
    
    
    def clear_plot(self):
        self.ax.clear()
        self.canvas.setVisible(False)

    #self.ax.plot(x_data, y1_data)


class WorkerSignals(QObject):
    progress_changed = Signal(int)
    images_masks = Signal(list, list)  # Señal para emitir datos al hilo principal
    spectrum_data = Signal(object)
    


class Worker(QRunnable):

    def __init__(self, path_rgb_image, path_hypespect_image) -> None:
        super(Worker, self).__init__()

        self.signals = WorkerSignals()
        self.path_rgb_image = path_rgb_image
        self.path_hypespect_image = path_hypespect_image

    def run(self):
        white_bands,black_bands = black_white("./sample_image/")

        
        image_rgb = cv2.imread(self.path_rgb_image)
        print("image_rgb.shape: ", image_rgb.shape)
        mask, centro_x, centro_y, ancho, largo, angulo, counter = seed_detection(image_rgb,plot=False)
        
        #self.mask_seeds = mask
        #self.centers_x = centro_x
        seeds_rgb, seeds_masks, tras_matrix, rot_matrix, roi_seeds = seeds_extraction([5,5], mask, image_rgb, centro_x, centro_y, ancho, largo, angulo)
        
        
        self.signals.images_masks.emit(seeds_rgb, seeds_masks)

        white_bands,black_bands = black_white("./sample_image/")
        
        frame_bands_correc = hyperspectral_images_seeds(self.path_hypespect_image, correction=True, white_bands=white_bands,black_bands=black_bands)
        print("frame_bands_correc.shape: ", frame_bands_correc.shape)
        seeds_spectrum = {}
        dsize = (image_rgb.shape[1], image_rgb.shape[0])
        for i in range(25):
            mini_mask = seeds_masks[i]
            traslate_matrix = tras_matrix[i]
            rotate_matrix = rot_matrix[i]
            roi_seed = roi_seeds[i]
            y_mean, y_std = extract_one_seed_hsi_features(frame_bands_correc, dsize, mini_mask, traslate_matrix, rotate_matrix, roi_seed)
            
            extract_one_seed_hsi([5,5], mask, image_rgb, frame_bands_correc, centro_x, centro_y, ancho, largo, angulo, i + 1, plot= False)
            seeds_spectrum[str(i)] = {"x_long_waves": long_onda , "y_mean":  y_mean, "y_std": y_std} 
            self.signals.progress_changed.emit(i * 100 / 25)

        self.signals.spectrum_data.emit(seeds_spectrum)

        self.signals.progress_changed.emit(100)

class FileInput(QWidget):
    def __init__(self, 
                 label_input,
                 color_texto = QColor(0, 0, 0),
                 color_boton = QColor(0,0,0)
                 ):
        super().__init__()

    
    def initUI(self, label_input, color_texto, color_boton):
        label_input = QLabel(label_input)
        label_input.setStyleSheet("color: {};".format(color_texto.name()))
        path_input = QLineEdit()
        selection_button = QPushButton("Seleccionar")
        selection_button.clicked.connect(self.button_open_file(path_input))
        selection_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
    
        return

class FontType(Enum):
    MAIN_TITLE = QFont("Roboto", 24, QFont.Bold)
    SECTION_TITLE = QFont("Roboto", 16, QFont.Medium)
    SUBSECTION_TITLE = QFont("Roboto", 14, QFont.Normal)

    def __call__(self):
        return self.value

class Styles:
    MAIN_TITLE = "color: #333333"
    SECTION_TITLE = "color: #555555"
    SUBSECTION_TITLE = "color: #777777"

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

        self.setMaximumSize(800, 16777215)

        
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
                            color_texto= color_texto)
        
        self.label_image_selected = QLabel(alignment = Qt.AlignCenter)
        self.label_image_selected.setVisible(False)
        procesing_form_layout.addWidget(self.label_image_selected)

        self.label_hsi, self.input_hsi, _ = self.add_file_input(
                            main_layout = procesing_form_layout,
                            required = True, 
                            label_text="Imagen Hiperspectral (.bil)",
                            color_boton = color_boton,
                            color_texto= color_texto)
        # Linea separadora

        self.add_separator_line(main_layout = procesing_form_layout)

        # Seccion de calibracion
        calibration_sub_header = QLabel("Calibracion de Reflactancia")
        calibration_sub_header.setStyleSheet(Styles.SECTION_TITLE)
        calibration_sub_header.setFont(FontType.SECTION_TITLE())
        procesing_form_layout.addWidget(calibration_sub_header)

        self.label_white_hsi, self.input_white_hsi, _ = self.add_file_input(
                            main_layout = procesing_form_layout, 
                            required = True,
                            label_text="Blanco de Referencia (.bil)",
                            color_boton = color_boton,
                            color_texto= color_texto)
        

        self.label_black_hsi, self.input_black_hsi, _ = self.add_file_input(
                            main_layout = procesing_form_layout,
                            required = True, 
                            label_text="Negro de Referencia (.bil)",
                            color_boton = color_boton,
                            color_texto= color_texto)

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

        threshold_label = QLabel("Umbral de color (HSV)")

        procesing_form_layout.addWidget(threshold_label)
        ## entrada de Hue 
        hue_layout = QHBoxLayout()

        hue_label = QLabel("Tono (H):")

        min_hue_layout = QHBoxLayout()

        min_hue_layout.setAlignment(Qt.AlignLeft)

        min_hue_label = QLabel("Min:")
        
        min_hue_spin_box = QSpinBox()
        min_hue_spin_box.setMinimum(0)
        min_hue_spin_box.setMaximum(255)
        min_hue_spin_box.setValue(10)

        min_hue_layout.addWidget(min_hue_label)
        min_hue_layout.addWidget(min_hue_spin_box)
        
        max_hue_layout = QHBoxLayout()
        max_hue_layout.setAlignment(Qt.AlignLeft)
        
        max_hue_label = QLabel("Max:")

        max_hue_spin_box = QSpinBox()
        max_hue_spin_box.setMinimum(0)
        max_hue_spin_box.setMaximum(255)
        max_hue_spin_box.setValue(10)

        max_hue_layout.addWidget(max_hue_label)
        max_hue_layout.addWidget(max_hue_spin_box)

        hue_layout.addWidget(hue_label)
        hue_layout.addLayout(min_hue_layout)
        hue_layout.addLayout(max_hue_layout)
        
        procesing_form_layout.addLayout(hue_layout)

        ## entrada de Saturation 
        saturation_layout = QHBoxLayout()

        saturation_label = QLabel("Saturación (S):")

        min_saturation_layout = QHBoxLayout()
        min_saturation_layout.setAlignment(Qt.AlignLeft)
        
        min_saturation_label = QLabel("Min:")
        
        min_saturation_spin_box = QSpinBox()
        min_saturation_spin_box.setMinimum(0)
        min_saturation_spin_box.setMaximum(255)
        min_saturation_spin_box.setValue(10)

        min_saturation_layout.addWidget(min_saturation_label)
        min_saturation_layout.addWidget(min_saturation_spin_box)
        
        max_saturation_layout = QHBoxLayout()
        max_saturation_layout.setAlignment(Qt.AlignLeft)
        
        max_saturation_label = QLabel("Max:")

        max_saturation_spin_box = QSpinBox()
        max_saturation_spin_box.setMinimum(0)
        max_saturation_spin_box.setMaximum(255)
        max_saturation_spin_box.setValue(10)

        max_saturation_layout.addWidget(max_saturation_label)
        max_saturation_layout.addWidget(max_saturation_spin_box)

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
        
        min_value_spin_box = QSpinBox()
        min_value_spin_box.setMinimum(0)
        min_value_spin_box.setMaximum(255)
        min_value_spin_box.setValue(10)

        min_value_layout.addWidget(min_value_label)
        min_value_layout.addWidget(min_value_spin_box)
        
        max_value_layout = QHBoxLayout()
        max_value_layout.setAlignment(Qt.AlignLeft)
        
        max_value_label = QLabel("Max:")

        max_value_spin_box = QSpinBox()
        max_value_spin_box.setMinimum(0)
        max_value_spin_box.setMaximum(255)
        max_value_spin_box.setValue(10)

        max_value_layout.addWidget(max_value_label)
        max_value_layout.addWidget(max_value_spin_box)

        value_layout.addWidget(value_label)
        value_layout.addLayout(min_value_layout)

        value_layout.addLayout(max_value_layout)
        
        procesing_form_layout.addLayout(value_layout)

        grid_label = QLabel("Grilla de Semillas")
        grid_label.setFont(FontType.SUBSECTION_TITLE())
        grid_label.setStyleSheet(Styles.SUBSECTION_TITLE)

        procesing_form_layout.addWidget(grid_label)

        num_columns_layout = QHBoxLayout()
        num_columns_layout.setAlignment(Qt.AlignLeft)

        num_columns_label = QLabel("Num. Columnas:")

        num_columns_spin_box = QSpinBox()
        num_columns_spin_box.setMinimum(0)
        num_columns_spin_box.setMaximum(50)
        num_columns_spin_box.setValue(5)

        num_columns_layout.addWidget(num_columns_label)
        num_columns_layout.addWidget(num_columns_spin_box)

        num_row_layout = QHBoxLayout()
        num_row_layout.setAlignment(Qt.AlignLeft)

        num_row_label = QLabel("Num. Filas:")

        num_row_spin_box = QSpinBox()
        num_row_spin_box.setMinimum(0)
        num_row_spin_box.setMaximum(50)
        num_row_spin_box.setValue(5)

        num_row_layout.addWidget(num_row_label)
        num_row_layout.addWidget(num_row_spin_box)
        
        procesing_form_layout.addLayout(num_columns_layout)
        procesing_form_layout.addLayout(num_row_layout)

        #buttons_form_layout = QHBoxLayout()
        # Botton importar imagen
        #self.clean_button = QPushButton("Cancelar")

        #self.clean_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        #buttons_form_layout.addWidget(self.clean_button)
        
        
        #Boton de Aplicar formulario
        #self.processing_button = QPushButton("Aplicar")
        #self.processing_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        #buttons_form_layout.addWidget(self.processing_button)

        #self.import_button.clicked.connect(self.process_image)

        #procesing_form_layout.addLayout(buttons_form_layout)

        # Establecer fondo para el formulario
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), color_fondo)
        self.setPalette(p)
    
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
                        fn_load_file = None):
        
        input_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("color: {};".format(color_texto.name()))
        input = QLineEdit()
        selection_button = QPushButton("Seleccionar")
        selection_button.clicked.connect(self.button_open_file(input, fn_load_file))
        
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
    

    def button_open_file(self, input, fn_load_file = None):
        def _button_open_file():
            path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","Tiff files (*.tif)","Tiff files (*.tif)")
            
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
        self.label_image_selected.setPixmap(pixmap.scaled(200,200, Qt.KeepAspectRatio))
        self.label_image_selected.setVisible(True)
    

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
                 grid_shape = [5,5]) -> None:
        super().__init__()
        self.initUI(background_text)
        self.image_labels = {}
        self.image_clickable = image_clickable
    
    def initUI(self, background_text):
        #self.setStyleSheet("background-color: rgba(255, 255, 255, 150);")
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.setMinimumSize(600, 400)
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
        image_label.setPixmap(pixmap.scaled(100,100,Qt.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignCenter)

        # Permitimos que el QLabel sea seleccionable
        if self.image_clickable:
            image_label.setCursor(Qt.PointingHandCursor)
            image_label.mousePressEvent = lambda event: self.image_clicked(
                event, image_label, id_label)

        image_label.setToolTip(f'Semilla-{id_label}')

        # Agregamos el QLabel con fondo negro y la imagen al layout
        #self.seeds_grid_layout.addWidget(background_label, row, column, alignment= Qt.AlignCenter)
        self.grid_layout.addWidget(image_label, row, column, alignment= Qt.AlignCenter)
        self.image_labels[id_label] = False

        self.no_image_label.setVisible(False)

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
            image_label.setStyleSheet("border: 3px solid black;")
    
    def get_images_clicked_status(self):
        return self.image_labels

class PanelFileInformation(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        
        self.setObjectName("custom-widget")  # Establecemos un nombre de objeto para el widget

        style = """
            QLabel {
                    color: #000000;            /* Color del texto de las etiquetas */
                    font: normal 14px;           /* Fuente del texto de las etiquetas */
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
            
            #custom-widget {
                border: 1px solid #e6e6e6;
                padding: 0px;
                margin: 0px
            }
        """
        self.setStyleSheet(style)
        # "font-size: 20px; color: #333; background-color: #f0f0f0; padding: 5px;"
        title_panel = QLabel("Panel de Informacion")
        title_panel.setFont(FontType.MAIN_TITLE())
        title_panel.setStyleSheet("""
                background-color: #f0f0f0;
                padding: 5px;                  
               """)
        main_layout.addWidget(title_panel)
        
        info_file_image_label = QLabel("Informacion del Archivo de Image")
        info_file_image_label.setFont(FontType.SECTION_TITLE())
        info_file_image_label.setStyleSheet(Styles.SECTION_TITLE)

        resolution_field_label = QLabel("Resolucion:")
        type_file_field_label = QLabel("Tipo de archivo:")

       
        main_layout.addWidget(info_file_image_label)
        main_layout.addWidget(resolution_field_label)
        main_layout.addWidget(type_file_field_label)

        info_file_hsi_label = QLabel("Informacion del Archivo de Image")
        info_file_hsi_label.setFont(FontType.SUBSECTION_TITLE())
        spectral_range_label = QLabel("Rango Espectral:")
        
        num_bands_label = QLabel("Numero de Bandas:")
        type_file_hsi_field_label = QLabel("Tipo de archivo:")

        main_layout.addWidget(info_file_hsi_label)
        main_layout.addWidget(spectral_range_label)
        main_layout.addWidget(num_bands_label)
        main_layout.addWidget(type_file_hsi_field_label)

        self.setLayout(main_layout)
        #pass

    def paintEvent(self, event):
        super().paintEvent(event)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.setWindowTitle("IDENTISEED")
        self.setGeometry(100, 100, 500, 200)
        # Colores
        color_fondo = QColor(240, 240, 240)
        color_boton = QColor(0, 70, 70)
        color_texto = QColor(0, 0, 0)

        # Main Layout Principal
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20,20,20,20)

        ## Menu
        menu = self.menuBar()
        file_menu = menu.addMenu("Archivo")
        button_action_file1 = QAction("Guardar datos espectrales", self)
        button_action_file1.setStatusTip("Guardar Datos Espectrales")
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
        
        
       
        
           # Vista de las semillas identificadas
        self.image_information_seccion_widget = QWidget()
      
        self.image_information_seccion_widget.setStyleSheet("background-color: rgba(255, 255, 255, 100);")

        image_information_layout = QVBoxLayout(self.image_information_seccion_widget)


        panel_file_info_widget = PanelFileInformation()

        panel_file_info_widget_2 = PanelFileInformation()
        image_information_layout.addWidget(panel_file_info_widget)
        image_information_layout.addWidget(panel_file_info_widget_2)

        # Crear acciones

        # Layout Principal del Fomulario de Importar Imagen
        #import_form_widget = QWidget()
        #import_form_layout = QVBoxLayout(import_form_widget)
        #import_form_widget.setMaximumSize(800, 16777215)
        # Layout de cada campo del formulario
        #input_rgb_image_layout = QHBoxLayout()
        #input_cabecera_layout = QHBoxLayout()
        #input_hsi_layout  = QHBoxLayout()
        #input_white_hsi_layout  = QHBoxLayout()
        #input_black_hsi_layout  = QHBoxLayout()
        #columna_layout  = QHBoxLayout()
        #input_grid_config_layout  = QHBoxLayout()
        #input_grid_row_column_layout  = QHBoxLayout()
        
        #row_colum_layout = QHBoxLayout()
        #buttons_form_layout = QHBoxLayout()
        
        # Establecer fondo para el formulario
        #import_form_widget.setAutoFillBackground(True)
        #p = import_form_widget.palette()
        #p.setColor(import_form_widget.backgroundRole(), color_fondo)
        #import_form_widget.setPalette(p)
        
        #label_dist_grid_image = QLabel("Distribucion de grilla de semillas")
        #label_dist_grid_image.setStyleSheet("color: {};".format(color_texto.name()))
        
        #input_grid_config_layout.addWidget(label_dist_grid_image)

        #label_row_grid = QLabel("Numero de Filas:")
        #label_row_grid.setStyleSheet("color: {};".format(color_texto.name()))
        #input_row_grid = QLineEdit()
        
        #row_colum_widget = QWidget()
        #row_colum_layout = QHBoxLayout(row_colum_widget)
        #row_colum_widget.setMaximumHeight(100)

        #label_colum_grid = QLabel("Numero de Columnas:")
        #label_colum_grid.setStyleSheet("color: {};".format(color_texto.name()))
        #input_colum_grid = QLineEdit()

        #row_colum_layout.addWidget(label_row_grid)
        #row_colum_layout.addWidget(input_row_grid)
        #row_colum_layout.addWidget(label_colum_grid)
        #row_colum_layout.addWidget(input_colum_grid)

        
      
        #input_grid_row_column_layout.addWidget(row_colum_widget)
        #input_grid_config_layout.addWidget(row_colum_widget)

        #label_rgb_image = QLabel("Imagen RGB (.tiff)")
        #label_rgb_image.setStyleSheet("color: {};".format(color_texto.name()))
        #input_rgb_image = QLineEdit()
        #button_rgb_image = QPushButton("Seleccionar")
        #button_rgb_image.clicked.connect(self.button_open_rgb_imge(input_rgb_image))
        #button_rgb_image.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))

        #asterisk_label_rbg = QLabel("*")
        #asterisk_label_rbg.setStyleSheet("color: red;")
        #asterisk_label_rbg.setFont(QFont("Arial", 12, QFont.Bold))

        #label_hsi = QLabel("Imagen Hiperspectral (.bil)")
        #input_hsi = QLineEdit()
        #button_hsi = QPushButton("Seleccionar")
        #button_hsi.clicked.connect(self.button_open_hsi(input_hsi))
        #button_hsi.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        #asterisk_label_hsi = QLabel("*")
        #asterisk_label_hsi.setStyleSheet("color: red;")
        #asterisk_label_hsi.setFont(QFont("Arial", 12, QFont.Bold))


        #label_white_hsi = QLabel("Blanco de Referencia (.bil)")
        #input_white_hsi = QLineEdit()
        #button_white_hsi = QPushButton("Seleccionar")
        #button_white_hsi.clicked.connect(self.button_open_white_hsi(input_white_hsi))
        #button_white_hsi.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        #asterisk_label_white_hsi = QLabel("*")
        #asterisk_label_white_hsi.setStyleSheet("color: red;")
        #asterisk_label_white_hsi.setFont(QFont("Arial", 12, QFont.Bold))


        #label_black_hsi = QLabel("Negro de Referencia (.bil)")
        #input_black_hsi = QLineEdit()
        #button_black_hsi = QPushButton("Seleccionar")
        #button_black_hsi.clicked.connect(self.button_open_black_hsi(input_black_hsi))
        #button_black_hsi.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        #asterisk_label_black_hsi = QLabel("*")
        #asterisk_label_black_hsi.setStyleSheet("color: red;")
        #asterisk_label_black_hsi.setFont(QFont("Arial", 12, QFont.Bold))
        
        #label_columna = QLabel("Numero de Filas")
        #input_columna = QLineEdit()
        #input_columna.setFixedWidth(30)
        #asterisk_label_columna = QLabel("*")
        #asterisk_label_columna.setFixedWidth(20)
        #asterisk_label_columna.setStyleSheet("color: red;")
        #asterisk_label_columna.setFont(QFont("Arial", 12, QFont.Bold))

        #label_row = QLabel("Numero de Columnas")


        #self.label_image_selected = QLabel(alignment = Qt.AlignCenter)

        #input_rgb_image_layout.addWidget(label_rgb_image)
        #input_rgb_image_layout.addWidget(asterisk_label_rbg)
        #input_rgb_image_layout.addWidget(input_rgb_image)
        #input_rgb_image_layout.addWidget(button_rgb_image)

        #input_hsi_layout.addWidget(label_hsi)
        #input_hsi_layout.addWidget(asterisk_label_hsi)
        #input_hsi_layout.addWidget(input_hsi)
        #input_hsi_layout.addWidget(button_hsi)
        
        #input_white_hsi_layout.addWidget(label_white_hsi)
        #input_white_hsi_layout.addWidget(asterisk_label_white_hsi)
        #input_white_hsi_layout.addWidget(input_white_hsi)
        #input_white_hsi_layout.addWidget(button_white_hsi)


        #input_black_hsi_layout.addWidget(label_black_hsi)
        #input_black_hsi_layout.addWidget(asterisk_label_black_hsi)
        #input_black_hsi_layout.addWidget(input_black_hsi)
        #input_black_hsi_layout.addWidget(button_black_hsi)


        #columna_layout.addWidget(label_columna)
        #columna_layout.addWidget(asterisk_label_columna)
        #columna_layout.addWidget(input_columna)
        #columna_layout.addChildWidget(label_row)
        #self.line_edits = [input_rgb_image, input_hsi, input_white_hsi, input_black_hsi]
    
        #import_form_layout.addLayout(input_rgb_image_layout)
        #import_form_layout.addLayout(input_cabecera_layout)
        #import_form_layout.addLayout(input_hsi_layout)
        #import_form_layout.addLayout(input_white_hsi_layout)
        #import_form_layout.addLayout(input_black_hsi_layout)
        #import_form_layout.addLayout(columna_layout)

        #import_form_layout.addLayout(input_black_hsi_layout)
        #import_form_layout.addWidget(input_grid_config_layout)
        #import_form_layout.addLayout(input_grid_row_column_layout)
        #import_form_layout.addWidget(self.label_image_selected)


        # Botton importar imagen
        #self.clean_button = QPushButton("Limpiar")
        #self.clean_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        #buttons_form_layout.addWidget(self.clean_button)
        #self.clean_button.clicked.connect(self.clean_form)
        
        #Boton de Limpiar formulario
        #self.import_button = QPushButton("Procesar")
        #self.import_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        #buttons_form_layout.addWidget(self.import_button)
        #self.import_button.clicked.connect(self.import_image)

        #import_form_layout.addLayout(buttons_form_layout)
        
        #self.progress_bar = CustomProgressBar(self)
        #self.progress_bar.setRange(0, 100)
        #self.progress_bar.setValue(0)
        
        #import_form_layout.addWidget(self.progress_bar)

        main_layout.addWidget(self.image_information_seccion_widget)

        #processing_form_widget =  ProcessingForm()
        #main_layout.addWidget(processing_form_widget)
        
        #main_layout.addWidget(self.progress_bar)
        #main_layout.addItem(QSpacerItem(20,20, QSizePolicy.Fixed, QSizePolicy.Minimum))
        
        # Vista de las semillas identificadas
        self.process_view_widget = QWidget()
      
        self.process_view_widget.setStyleSheet("background-color: rgba(255, 255, 255, 100);")
        process_view_layout = QVBoxLayout(self.process_view_widget)
        

        main_layout.addWidget(self.process_view_widget)

        tab_widget = QTabWidget()
        process_view_layout.addWidget(tab_widget)

        self.seeds_tab = ImageGridWidget(background_text="Ninguna Semilla Identificada")
        self.masks_tab = ImageGridWidget(background_text="Ninguna Semilla Identificada", image_clickable = False)

        tab_widget.addTab(self.seeds_tab, "Semillas")
        tab_widget.addTab(self.masks_tab, "Mascaras")

        ## Boton de ver grafico de bandas espectradles

        spectrum_button = QPushButton("Mostrar Informacion Espectral")
        spectrum_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        spectrum_button.clicked.connect(self.button_show_spectrum)
        
        process_view_layout.addWidget(spectrum_button)

        ## Header se seccion de descarga de informacion hypespectral
        spectrum_header = QWidget()
        spectrum_header.setStyleSheet("font-size: 20px; color: #333; background-color: #f0f0f0; padding: 5px;")
        spectrum_header_layout = QHBoxLayout(spectrum_header)
       
        spectrum_label = QLabel("<b>Información Hiperespectral</b>")
        spectrum_label.setAlignment(Qt.AlignLeft)
        spectrum_label.setStyleSheet("font-size: 20px; color: #333; background-color: #f0f0f0; padding: 5px;")

        self.download_spectrum = QPushButton()
        
        icon_download = QIcon("./icons/icons8-descargar-48.png")  # Ruta al archivo de icono
        self.download_spectrum.setIcon(icon_download)

        self.download_spectrum.clicked.connect(self.download_csv_spectrum)


        spectrum_header_layout.addWidget(spectrum_label)
        spectrum_header_layout.addStretch(1)
        spectrum_header_layout.addWidget(self.download_spectrum)
        
        process_view_layout.addWidget(spectrum_header)

        tab_hci_data = QTabWidget()
        process_view_layout.addWidget(tab_hci_data)
        
        ## Tab de grafico de avg 
        self.spectrum_avg_plot = MatplotlibWidget(xlabel="wave length", ylabel="radiance")

        #self.spectrum_avg_graph =  QWidget()
        #self.spectrum_avg_graph.setStyleSheet("background-color: #f0f0f0;")
        #self.spectrum_avg_graph.setMinimumSize(600, 300)
        
        #self.graph_layout_avg = QHBoxLayout(self.spectrum_avg_graph)
        #self.fig_avg, self.ax_avg = plt.subplots()
        #self.canvas_avg_graph = FigureCanvas(self.fig_avg)
        #self.graph_layout_avg.addWidget(self.canvas_avg_graph)

        #self.canvas_avg_graph.setVisible(False)

        tab_hci_data.addTab(self.spectrum_avg_plot, "Espectro (Promedio)")
        ## Tab de grafico de desviacion estandar 
        self.spectrum_std_plot = MatplotlibWidget(xlabel="wave length", ylabel="radiance")

        #self.spectrum_sd_graph =  QWidget()
        #self.spectrum_sd_graph.setStyleSheet("background-color: #f0f0f0;")
        #self.spectrum_sd_graph.setMinimumSize(600, 300)
        
        #self.graph_layout_sd = QHBoxLayout(self.spectrum_sd_graph)
        #self.fig_sd, self.ax_sd = plt.subplots()
        #self.canvas_sd_graph = FigureCanvas(self.fig_sd)
        #self.graph_layout_sd.addWidget(self.canvas_sd_graph)

        #self.canvas_sd_graph.setVisible(False)

        tab_hci_data.addTab(self.spectrum_std_plot, "Espectro (Des. Estandar)")

        
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
    
    def on_dowload_manual(self):
        return ""
    def on_extract_spectral_feactures(self):
        self.dialog =  QDialog(self)
        self.dialog.setWindowTitle(" ")
        #self.dialog.setWindowFlags(Qt.FramelessWindowHint) 
        #self.dialog.setFixedSize(500, 600)  # Fijar tamaño del diálogo
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

        #dialog_layout.addWidget(self.process_form_dialog)
        dialog_layout.addLayout(button_dialog_layout)

        self.dialog.setLayout(dialog_layout)
        self.dialog.exec_()

        return ""

    def process_extract_features(self):
        return ""
    def on_save_data_spectral(self):
        return ""
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

            columns = ["seed_id"] +  [f"avg_band_{lw}" for lw in x_long_waves] + [ f"sd_band_{lw}" for lw in x_long_waves]
            
            print("\nself.spectrum_data:", self.spectrum_data)
            data = [ [id_seed] + seed_data["y_mean"].tolist() + seed_data["y_std"].tolist() for id_seed , seed_data in self.spectrum_data.items()]
            print()
            print("\ndata[0]:", data[0]) 
            df = pd.DataFrame(data, columns = columns)
            print(df)
            df.to_csv(fileName, index= False)
            
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

    def update_progress(self, value):
        text = f"Progreso: {value}% completado"
        self.progress_bar.setValue(value)
        self.progress_bar.set_custom_text(text)
        self.progress_bar.update_time(value)


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

    def button_open_rgb_imge(self, line_edit):
        def _button_open_rgb_imge():
            path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","Tiff files (*.tif)","Tiff files (*.tif)")
            
            if not path:
                print("Archivo no seleccionado")
            else:
                print("Archivo seleccionado:", path)
                pixmap = QPixmap(path)
                self.label_image_selected.setPixmap(pixmap.scaled(600,600, Qt.KeepAspectRatio))
                line_edit.setText(path)
        return _button_open_rgb_imge
            #self.path = path


    def button_open_cabecera(self, line_edit):
        def _button_open_cabecera():
            path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","BIL Header files (*.bil.hdr)","BIL Header files (*.bil.hdr)")
            if not path:
                print("Archivo no seleccionado")
            else:
                print("Archivo seleccionado:", path)
                line_edit.setText(path)
        return _button_open_cabecera
    

    def button_open_hsi(self, line_edit):
        def _button_open_hsi():
            path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","BIL files (*.bil)","BIL files (*.bil)")
            if not path:
                print("Archivo no seleccionado")
            else:
                print("Archivo seleccionado:", path)
                line_edit.setText(path)
        return _button_open_hsi

    def button_open_white_hsi(self, line_edit):
        def _button_open_white_hsi():
            path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","BIL files (*.bil)","BIL files (*.bil)")
            if not path:
                print("Archivo no seleccionado")
            else:
                print("Archivo seleccionado:", path)
                line_edit.setText(path)
        return _button_open_white_hsi
    
    def button_open_black_hsi(self, line_edit):
        def _button_open_black_hsi():
            path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","BIL files (*.bil)","BIL files (*.bil)")
            if not path:
                print("Archivo no seleccionado")
            else:
                print("Archivo seleccionado:", path)
                line_edit.setText(path)
        return _button_open_black_hsi

    def validate_filled_form(self):
        for line_edit in self.line_edits:
            if line_edit.text().strip() == "":
                QMessageBox.warning(self, "Campos Vacios","Por favor, llene todos los campos.")
                return False
        return True
    
    def import_image(self):
        self.import_button.setEnabled(False)
        self.progress_bar.setValue(0)

        success_validate = self.validate_filled_form()
        print("success_validate:", success_validate)
        if not success_validate:
            return
        
        path_rgb_image = self.line_edits[0].text()
        path_hypespect_image = self.line_edits[2].text()

        #self.thread_process = QThread()
        worker = Worker(path_rgb_image, path_hypespect_image)
        worker.signals.progress_changed.connect(self.update_progress)
        worker.signals.images_masks.connect(self.show_images_masks)
        worker.signals.spectrum_data.connect(self.recive_spectrum_data)
        
        self.threadpool.start(worker)

    def process_image(self):
        #self.import_button.setEnabled(False)
        #self.progress_bar.setValue(0)

        #success_validate = self.validate_filled_form()
        #print("success_validate:", success_validate)
        #if not success_validate:
        #    return
        
        #path_rgb_image = self.line_edits[0].text()
        #path_hypespect_image = self.line_edits[2].text()

        #self.thread_process = QThread()
        """ worker = Worker(path_rgb_image, path_hypespect_image)
        worker.signals.progress_changed.connect(self.update_progress)
        worker.signals.images_masks.connect(self.show_images_masks)
        worker.signals.spectrum_data.connect(self.recive_spectrum_data)
        
        self.threadpool.start(worker) """

    def recive_spectrum_data(self, spectrum_data):
        self.spectrum_data = spectrum_data


    def process_finished(self, result):
        # Este método se llama cuando el proceso en segundo plano ha terminado
        self.import_button.setEnabled(True)
        print("Proceso terminado")
      
        
    def clean_form(self):
        print("Limpiar Formulario")

    def image_clicked(self, event, background_label, id_image):
        self.image_labels[id_image] = not self.image_labels[id_image]

        # Cambiamos el estilo del QLabel cuando se hace clic en él
        if self.image_labels[id_image]:
            background_label.setStyleSheet("border: 3px solid green;")
        else:
            background_label.setStyleSheet("")
            background_label.setStyleSheet("border: 3px solid black;")

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()