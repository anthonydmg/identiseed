import sys
from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar, QCheckBox, 
    QPushButton, QDialog, QDialogButtonBox, 
    QVBoxLayout, QMessageBox, QFileDialog,
    QHBoxLayout, QLineEdit, QWidget, QGridLayout, QSpacerItem, QSizePolicy, QTabWidget
)
from PySide6.QtGui import QAction, QIcon, QPaintEvent, QPixmap, QColor, QPainter, QFont, QImage
from PySide6.QtCore import Qt, QThread, Signal, QObject
from utils import black_white, seed_detection, seeds_extraction, one_seed, hyperspectral_images_seeds, long_onda
import cv2
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


def process_image_hsi(process_changed, path_image_rgb, path_hsi_bil):
    white_bands,black_bands = black_white("./sample_image/")
    
    frame_bands_correc = hyperspectral_images_seeds(path_hsi_bil, correction=True, white_bands=white_bands,black_bands=black_bands)
    
    image_rgb = cv2.imread(path_image_rgb)
    mask, centro_x, centro_y, ancho, largo, angulo, counter = seed_detection(image_rgb,plot=False)
    
    #self.mask_seeds = mask
    #self.centers_x = centro_x
    seeds_rgb, seeds_masks = seeds_extraction([5,5], mask, image_rgb, centro_x, centro_y, ancho, largo, angulo)
    
    white_bands,black_bands = black_white("./sample_image/")
    
    frame_bands_correc = hyperspectral_images_seeds(path_hsi_bil, correction=True, white_bands=white_bands,black_bands=black_bands)

    seeds_spectrum = {}
    for i in range(25):
        y_mean, y_std = one_seed([5,5], mask, image_rgb, frame_bands_correc, centro_x, centro_y, ancho, largo, angulo, i + 1)
        seeds_spectrum[str(i)] = {"x_long_waves": long_onda , "y_mean":  y_mean, "y_std": y_std} 
    
    return seeds_rgb, seeds_masks 

class Worker(QObject):
    progress_changed = Signal(int)
    data_ready = Signal(object)  # Señal para emitir datos al hilo principal


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
        self.no_image_label.setStyleSheet("background-color: rgba(50, 50, 50, 100); color: white;")
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
        
        
        # Layout Principal del Fomulario de Importar Imagen
        import_form_widget = QWidget()
        import_form_layout = QVBoxLayout(import_form_widget)
        import_form_widget.setMaximumSize(600, 16777215)
        # Layout de cada campo del formulario
        input_rgb_image_layout = QHBoxLayout()
        input_cabecera_layout = QHBoxLayout()
        input_hsi_layout  = QHBoxLayout()
        buttons_form_layout = QHBoxLayout()
        
        # Establecer fondo para el formulario
        import_form_widget.setAutoFillBackground(True)
        p = import_form_widget.palette()
        p.setColor(import_form_widget.backgroundRole(), color_fondo)
        import_form_widget.setPalette(p)
        
        label_rgb_image = QLabel("Importar Imagen RGB (.tiff)")
        label_rgb_image.setStyleSheet("color: {};".format(color_texto.name()))
        input_rgb_image = QLineEdit()
        button_rgb_image = QPushButton("Seleccionar")
        button_rgb_image.clicked.connect(self.button_open_rgb_imge(input_rgb_image))
        button_rgb_image.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))

        asterisk_label_rbg = QLabel("*")
        asterisk_label_rbg.setStyleSheet("color: red;")
        asterisk_label_rbg.setFont(QFont("Arial", 12, QFont.Bold))

        label_cabecera = QLabel("Importar Cebecera (.bil.hdr)")
        input_cabecera = QLineEdit()
        button_cabecera = QPushButton("Seleccionar")
        button_cabecera.clicked.connect(self.button_open_cabecera(input_cabecera))
        button_cabecera.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))

        asterisk_label_cabecera = QLabel("*")
        asterisk_label_cabecera.setStyleSheet("color: red;")
        asterisk_label_cabecera.setFont(QFont("Arial", 12, QFont.Bold))

        label_hsi = QLabel("Importar Imagen Hiperspectral (.bil)")
        input_hsi = QLineEdit()
        button_hsi = QPushButton("Seleccionar")
        button_hsi.clicked.connect(self.button_open_hsi(input_hsi))
        button_hsi.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        asterisk_label_hsi = QLabel("*")
        asterisk_label_hsi.setStyleSheet("color: red;")
        asterisk_label_hsi.setFont(QFont("Arial", 12, QFont.Bold))

        self.label_image_selected = QLabel(alignment = Qt.AlignCenter)

        input_rgb_image_layout.addWidget(label_rgb_image)
        input_rgb_image_layout.addWidget(asterisk_label_rbg)
        input_rgb_image_layout.addWidget(input_rgb_image)
        input_rgb_image_layout.addWidget(button_rgb_image)

        input_cabecera_layout.addWidget(label_cabecera)
        input_cabecera_layout.addWidget(asterisk_label_cabecera)
        input_cabecera_layout.addWidget(input_cabecera)
        input_cabecera_layout.addWidget(button_cabecera)
     
        input_hsi_layout.addWidget(label_hsi)
        input_hsi_layout.addWidget(asterisk_label_hsi)
        input_hsi_layout.addWidget(input_hsi)
        input_hsi_layout.addWidget(button_hsi)
        
        self.line_edits = [input_rgb_image, input_cabecera, input_hsi]
    
        import_form_layout.addLayout(input_rgb_image_layout)
        import_form_layout.addLayout(input_cabecera_layout)
        import_form_layout.addLayout(input_hsi_layout)
        import_form_layout.addWidget(self.label_image_selected)

        # Botton importar imagen
        self.clean_button = QPushButton("Limpiar")
        self.clean_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        buttons_form_layout.addWidget(self.clean_button)
        self.clean_button.clicked.connect(self.clean_form)
        
        #Boton de Limpiar formulario
        self.import_button = QPushButton("Importar")
        self.import_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        buttons_form_layout.addWidget(self.import_button)
        self.import_button.clicked.connect(self.import_image)

        import_form_layout.addLayout(buttons_form_layout)
        
        main_layout.addWidget(import_form_widget)
        main_layout.addItem(QSpacerItem(20,20, QSizePolicy.Fixed, QSizePolicy.Minimum))
        
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

        spectrum_button = QPushButton("Mostrar Firma Espectral")
        spectrum_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))

        spectrum_label = QLabel("<b>Spectrum</b>")
        spectrum_label.setAlignment(Qt.AlignLeft)
        spectrum_label.setStyleSheet("font-size: 20px; color: #333; background-color: #f0f0f0; padding: 5px;")

        process_view_layout.addWidget(spectrum_button)
        process_view_layout.addWidget(spectrum_label)


        # Crear y agregar la sección del gráfico
        self.graph_section = QWidget()
        self.graph_section.setStyleSheet("background-color: #f0f0f0;")
        self.graph_section.setMinimumSize(600, 300)

        # Layout para la sección del gráfico
        self.graph_layout = QHBoxLayout(self.graph_section)

        # Crear y agregar el gráfico dentro de la sección del gráfico
        #self.fig, self.ax = plt.subplots()
        #self.canvas = FigureCanvas(self.fig)
        #self.graph_layout.addWidget(self.canvas)

        process_view_layout.addWidget(self.graph_section)

        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        # Plot

        self.thread = QThread()
        self.thread.started.connect(self.start_work)
        self.thread.finished.connect(self.process_finished)
        

    def button_show_spectrum(self):
        #Crear y agregar el gráfico dentro de la sección del gráfico
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.graph_layout.addWidget(self.canvas)

        # Actualizar el gráfico de barras
        self.ax.clear()
        images_clicked_status = self.seeds_tab.get_images_clicked_status()
        images_clicked_ids = [ key for key, value in images_clicked_status.items() if value]
        if len(images_clicked_ids) > 0:
            #self.ax.hist(file_sizes, bins=20, alpha=0.7, color='blue')
            for image_id in images_clicked_ids:
                x = self.seeds_spectrum[image_id]["x_long_waves"]
                y_mean = self.seeds_spectrum[image_id]["y_mean"]
                self.ax.plot(x, y_mean)
            self.ax.set_title('Distribución de tamaños de archivo')
            self.ax.set_xlabel('Tamaño del archivo (bytes)')
            self.ax.set_ylabel('Frecuencia')
        else:
            self.ax.text(0.5, 0.5, 'No hay archivos en esta carpeta', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
        self.canvas.draw()

        return 

    def button_open_rgb_imge(self, line_edit):
        def _button_open_rgb_imge():
            path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","Tiff files (*.tif)","Tiff files (*.tif)")
            
            if not path:
                print("Archivo no seleccionado")
            else:
                print("Archivo seleccionado:", path)
                pixmap = QPixmap(path)
                self.label_image_selected.setPixmap(pixmap.scaled(400,400, Qt.KeepAspectRatio))
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

    def validate_filled_form(self):
        for line_edit in self.line_edits:
            if line_edit.text().strip() == "":
                QMessageBox.warning(self, "Campos Vacios","Por favor, llene todos los campos.")
                return False
        return True
    
    def import_image(self):
        success_validate = self.validate_filled_form()
        print("success_validate:", success_validate)
        if not success_validate:
            return

        self.seeds_spectrum = {}
        path_rgb_image = self.line_edits[0].text()
        image_rgb = cv2.imread(path_rgb_image)
        mask, centro_x, centro_y, ancho, largo, angulo, counter = seed_detection(image_rgb,plot=False)
        
        #self.mask_seeds = mask
        #self.centers_x = centro_x
        seeds_rgb, seeds_masks = seeds_extraction([5,5], mask, image_rgb, centro_x, centro_y, ancho, largo, angulo)
        
        path_hypespect_image = self.line_edits[2].text()
        white_bands,black_bands = black_white("./sample_image/")
        
        frame_bands_correc = hyperspectral_images_seeds(path_hypespect_image, correction=True, white_bands=white_bands,black_bands=black_bands)

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

            #y_mean, y_std = one_seed([5,5], mask, image_rgb, frame_bands_correc, centro_x, centro_y, ancho, largo, angulo, i + 1)

            #self.seeds_spectrum[str(i)] = {"x_long_waves": long_onda , "y_mean":  y_mean, "y_std": y_std} 

            #self.image_labels[i] = False
        
        spectral_label = QLabel("Firmas Espectrales")
        spectral_label.setAlignment(Qt.AlignLeft)
        spectral_label.setStyleSheet("color: black;")
        spectral_label.setMaximumHeight(20)

        print("Importar imagen")
    
        
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