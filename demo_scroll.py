import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QScrollArea

class ScrollAreaExample(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Crear el contenido del scroll area (en este caso un QTextEdit)
        self.textEdit = QTextEdit(self)
        self.textEdit.setText("Contenido del QTextEdit")
        
        # Crear el QScrollArea y configurar su contenido
        scrollArea = QScrollArea(self)
        scrollArea.setWidget(self.textEdit)
        
        # Configurar el tamaño mínimo del QScrollArea
        scrollArea.setMinimumSize(self.textEdit.sizeHint())
        
        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(scrollArea)
        
        self.setLayout(layout)
        self.setWindowTitle('Ejemplo QScrollArea con tamaño mínimo')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScrollAreaExample()
    sys.exit(app.exec())