import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt

class ImageGrid(QWidget):
    def __init__(self):
        super().__init__()

        # Creamos un layout de cuadrícula para este widget
        self.layout = QGridLayout(self)

        # Agregamos algunas imágenes a la cuadrícula
        self.add_image("./sample_image/AMAZ-46-02-RGB.tif", 0, 0)
        self.add_image("./sample_image/AMAZ-46-02-RGB.tif", 0, 1)
        self.add_image("./sample_image/AMAZ-46-02-RGB.tif", 1, 0)
        self.add_image("./sample_image/AMAZ-46-02-RGB.tif", 1, 1)

    def add_image(self, image_path, row, column):
        # Cargamos la imagen desde el archivo
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        # Creamos un QLabel y establecemos la imagen como su pixmap
        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)

        # Permitimos que el QLabel sea seleccionable
        label.setScaledContents(True)
        label.setCursor(Qt.PointingHandCursor)
        label.mousePressEvent = lambda event: self.image_clicked(event, label)

        # Agregamos el QLabel a la cuadrícula
        self.layout.addWidget(label, row, column)

    def image_clicked(self, event, label):
        # Cambiamos el estilo del QLabel cuando se hace clic en él
        if label.styleSheet() == "":
            label.setStyleSheet("border: 2px solid blue;")
        else:
            label.setStyleSheet("")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cuadrícula de Imágenes")
        self.setGeometry(100, 100, 400, 300)

        # Creamos el widget principal y el layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        # Creamos la cuadrícula de imágenes y la agregamos al layout
        self.image_grid = ImageGrid()
        self.layout.addWidget(self.image_grid)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())