import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QFrame

class ExampleApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ejemplo de QFrame")
        self.setGeometry(100, 100, 400, 300)

        # Creamos un layout principal y un widget central
        self.main_layout = QVBoxLayout()
        self.central_widget = QFrame()  # Usamos un QFrame como widget central
        self.central_widget.setStyleSheet("background-color: white; border: 2px solid blue;")  # Estilo del QFrame
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        # Creamos widgets para mostrar en el QFrame
        self.title_label = QLabel("Resumen:")
        self.main_layout.addWidget(self.title_label)

        self.summary_label = QLabel("Aquí va el resumen de la información.")
        self.main_layout.addWidget(self.summary_label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    sys.exit(app.exec())