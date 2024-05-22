import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QListWidget, QListWidgetItem
from PySide6.QtGui import QPixmap, QIcon

class ImageListModel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Creamos un layout vertical para este widget
        self.layout = QVBoxLayout(self)

        # Creamos un QListWidget para mostrar las imágenes
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        # Agregamos algunas imágenes a la lista
        self.add_image("./sample_image/AMAZ-46-02-RGB.tif")
        self.add_image("./sample_image/AMAZ-46-02-RGB.tif")
        self.add_image("./sample_image/AMAZ-46-02-RGB.tif")

    def add_image(self, image_path):
        # Cargamos la imagen desde el archivo
        pixmap = QPixmap(image_path)

        # Creamos un QListWidgetItem y establecemos la imagen como su icono
        item = QListWidgetItem()
        item.setIcon(QIcon(pixmap))

        # Añadimos el item a la lista
        self.list_widget.addItem(item)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lista de Imágenes")
        self.setGeometry(100, 100, 400, 300)

        # Creamos el widget principal y el layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Creamos el modelo de imágenes y lo agregamos al layout
        self.image_list = ImageListModel()
        self.layout.addWidget(self.image_list)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())