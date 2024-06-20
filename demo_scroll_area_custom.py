import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton, QScrollArea

class ScrollAreaExample(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Crear un widget de contenedor para los elementos
        container = QWidget(self)
        containerLayout = QVBoxLayout(container)
        
        # Agregar widgets al contenedor
        containerLayout.addWidget(QLabel("Etiqueta 1"))
        containerLayout.addWidget(QLabel("Etiqueta 2"))
        containerLayout.addWidget(QLabel("Etiqueta 3"))
        containerLayout.addWidget(QPushButton("Botón 1"))
        containerLayout.addWidget(QPushButton("Botón 2"))
        
        # Crear el QScrollArea y configurar su contenido como el contenedor
        scrollArea = QScrollArea(self)
        scrollArea.setWidgetResizable(True)  # Ajustar el tamaño automáticamente
        scrollArea.setWidget(container)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.addWidget(scrollArea)
        
        self.setLayout(layout)
        self.setWindowTitle('Ejemplo QScrollArea con múltiples widgets')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScrollAreaExample()
    sys.exit(app.exec())