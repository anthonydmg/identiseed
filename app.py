import sys
from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar, QCheckBox, 
    QPushButton, QDialog, QDialogButtonBox, 
    QVBoxLayout, QMessageBox, QFileDialog,
    QHBoxLayout, QLineEdit, QWidget, QGridLayout, QSpacerItem, QSizePolicy
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
        background_process_view_label = QLabel("Ningua Imagen Importada")
        background_process_view_label.setAlignment(Qt.AlignCenter)
        background_process_view_label.setStyleSheet("color: rgba(0, 0, 0, 0.5);") 
        background_process_view_label.setFont(QFont("Arial", 16))
        process_view_layout.addWidget(background_process_view_label)
        
        main_layout.addWidget(self.process_view_widget)

        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)


    def button_open_rgb_imge(self, line_edit):
        def _button_open_rgb_imge():
            path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", ".","Tiff files (*.tif)","Tiff files (*.tif)")
            
            if not path:
                print("Archivo no seleccionado")
            else:
                print("Archivo seleccionado:", path)
                pixmap = QPixmap("./sample_image/ANC-399-1-RGB.tif")
                self.label_image_selected.setPixmap(pixmap.scaled(200,200, Qt.KeepAspectRatio))
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
        self.process_view_widget.deleteLater()
        self.process_view_widget = QWidget()
        self.process_view_widget.setStyleSheet("background-color: rgba(255, 255, 255, 100);")
        process_view_layout = QVBoxLayout(self.process_view_widget)
        

        ident_seeds_label = QLabel("Semillas Identificadas")
        ident_seeds_label.setAlignment(Qt.AlignLeft)
        ident_seeds_label.setStyleSheet("color: black;")
        ident_seeds_label.setMaximumHeight(20)

        process_view_layout.addWidget(ident_seeds_label)

        seeds_grid_layout = QGridLayout()
        seeds_grid_layout.setSpacing(10) # Espaciado uniforme entre las celdas de la cuadrícula
        row, col = 0, 0
        for i in range(16):
                pixmap = QPixmap(self.line_edits[0].text())
                label = QLabel()
                label.setPixmap(pixmap.scaled(100,100,Qt.KeepAspectRatio))
                col = i % 4
                row = i // 4
                seeds_grid_layout.addWidget(label, row, col, alignment= Qt.AlignCenter)

        process_view_layout.addLayout(seeds_grid_layout)

        layout = self.centralWidget().layout()
        layout.addWidget(self.process_view_widget)

        print("Importar imagen")
    
    def clean_form(self):
        print("Limpiar Formulario")

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()