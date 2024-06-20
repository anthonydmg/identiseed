import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()

        # Establece el título de la ventana
        self.setWindowTitle('Título alineado a la izquierda')
        self.setGeometry(100, 100, 400, 300)  # Establece la geometría de la ventana

        # Crear un widget central para la ventana
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout vertical para colocar un QLabel
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Sin márgenes

        # Crear un QLabel con el texto del título
        label = QLabel('Título alineado a la izquierda')
        layout.addWidget(label)

        # Alinear el texto del QLabel a la izquierda
        label.setAlignment(Qt.AlignLeft)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec())