from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configura el widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Configura el layout del widget central
        layout = QVBoxLayout(central_widget)
        
        # Carga la imagen
        original_pixmap = QPixmap("./icons/Image_home_identiseed.png")

        # Obtén la densidad de píxeles de la pantalla
        screen = QApplication.primaryScreen()
        logical_dpi = screen.logicalDotsPerInch()
        
        # Establece el tamaño deseado en unidades físicas (por ejemplo, 2.5 pulgadas de ancho)
        desired_physical_width_in_inches = 2.5
        
        # Calcula el tamaño en píxeles basado en la densidad de píxeles
        desired_width_in_pixels = int(desired_physical_width_in_inches * logical_dpi)
        
        # Escala la imagen para que tenga el ancho deseado en píxeles y mantiene la proporción
        scaled_pixmap = original_pixmap.scaled(desired_width_in_pixels, desired_width_in_pixels, Qt.KeepAspectRatio)
        
        # Crea una etiqueta y establece la imagen escalada
        label = QLabel()
        label.setPixmap(scaled_pixmap)
        layout.addWidget(label)

        # Configura el tamaño inicial de la ventana (opcional)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Ejemplo de imagen escalada con proporción mantenida")

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()