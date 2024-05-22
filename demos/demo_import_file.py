import sys
from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar, QCheckBox, 
    QPushButton, QDialog, QDialogButtonBox, 
    QVBoxLayout, QMessageBox, QFileDialog,
    QHBoxLayout, QLineEdit, QWidget, QGridLayout
)
from PySide6.QtGui import QAction, QIcon, QPaintEvent, QPixmap, QColor, QPainter, QFont
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("IDENTISEED")
        self.setGeometry(100, 100, 500, 200)
        # Colores
        color_fondo = QColor(240, 240, 240)
        color_boton = QColor(0, 70, 70)
        color_texto = QColor(0, 0, 0)

        # Grid Layout Principal
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(20,20,20,20)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        # Layout Principal del Fomulario de Importar Imagen
        import_form_layout = QVBoxLayout()
        #import_form_layout.setContentsMargins(20,20,20,20)
        
        # Layout de cada campo del formulario
        input_rgb_image_layout = QHBoxLayout()
        input_cabecera_layout = QHBoxLayout()
        input_hsi_layout  = QHBoxLayout()
        buttons_form_layout = QHBoxLayout()

        # Establecer fondo para el formulario
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), color_fondo)
        self.setPalette(p)
        
        label_rgb_image = QLabel("Importar Imagen RGB (.tiff)")
        label_rgb_image.setStyleSheet("color: {};".format(color_texto.name()))
        input_rgb_image = QLineEdit()
        button_rgb_image = QPushButton("Seleccionar")
        button_rgb_image.clicked.connect(self.button_open_rgb_imge)
        button_rgb_image.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))

        label_cabecera = QLabel("Importar Cebecera (.bil.hdr)")
        input_cabecera = QLineEdit()
        button_cabecera = QPushButton("Seleccionar")
        button_cabecera.clicked.connect(self.button_open_cabecera)
        button_cabecera.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))

        label_hsi = QLabel("Importar Imagen Hiperspectral (.bil)")
        input_hsi = QLineEdit()
        button_hsi = QPushButton("Seleccionar")
        button_hsi.clicked.connect(self.button_open_hsi)
        button_hsi.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))

        self.label_image_selected = QLabel(alignment = Qt.AlignCenter)

        input_rgb_image_layout.addWidget(label_rgb_image)
        input_rgb_image_layout.addWidget(input_rgb_image)
        input_rgb_image_layout.addWidget(button_rgb_image)

        input_cabecera_layout.addWidget(label_cabecera)
        input_cabecera_layout.addWidget(input_cabecera)
        input_cabecera_layout.addWidget(button_cabecera)
     
        input_hsi_layout.addWidget(label_hsi)
        input_hsi_layout.addWidget(input_hsi)
        input_hsi_layout.addWidget(button_hsi)
     
        import_form_layout.addLayout(input_rgb_image_layout)
        import_form_layout.addLayout(input_cabecera_layout)
        import_form_layout.addLayout(input_hsi_layout)
        import_form_layout.addWidget(self.label_image_selected)

        # Botton importar imagen
        self.clean_button = QPushButton("Limpiar")
        self.clean_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        buttons_form_layout.addWidget(self.clean_button)
        self.clean_button.clicked.connect(self.clean_form)
        
        self.import_button = QPushButton("Importar")
        self.import_button.setStyleSheet("background-color: {}; color: white;".format(color_boton.name()))
        buttons_form_layout.addWidget(self.import_button)
        self.import_button.clicked.connect(self.import_image)

        import_form_layout.addLayout(buttons_form_layout)
        
        grid_layout.addLayout(import_form_layout, 0, 0)

        self.image_process_view = ImageProcessView()
        grid_layout.addWidget(self.image_process_view, 0, 1)
        
        widget = QWidget()
        widget.setLayout(grid_layout)
        self.setCentralWidget(widget)

    def button_open_rgb_imge(self, s):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","Tiff files (*.tif)","Tiff files (*.tif)")
        
        if not path:
            print("Archivo no seleccionado")
        else:
            print("Archivo seleccionado:", path)
            pixmap = QPixmap("./sample_image/ANC-399-1-RGB.tif")
            self.label_image_selected.setPixmap(pixmap.scaled(200,200, Qt.KeepAspectRatio))

    def button_open_cabecera(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","BIL Header files (*.bil.hdr)","BIL Header files (*.bil.hdr)")
        if not path:
            print("Archivo no seleccionado")
        else:
            print("Archivo seleccionado:", path)

    def button_open_hsi(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","BIL files (*.bil)","BIL files (*.bil)")
        if not path:
            print("Archivo no seleccionado")
        else:
            print("Archivo seleccionado:", path)

    def import_image(self):
        print("Importar imagen")
    
    def clean_form(self):
        print("Limpiar Formulario")

class ImageProcessView(QWidget):
    def __init__(self):
        super().__init__()
        self.text = "Nunguna Imagen Importada"
        self.setStyleSheet("background-color: rgba(255, 255, 255, 100);")
        self.setMinimumSize(300, 200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.transparent)
        painter.fillRect(self.rect(), QColor(255, 255, 255, 100))
        
        painter.setPen(QColor(100, 100, 100, 150))
        painter.setFont(QFont('Arial', 14))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text)
app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()