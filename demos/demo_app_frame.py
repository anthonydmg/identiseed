import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QListWidget, QTextEdit, QLabel, QFrame

class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mi Aplicación de Notas")
        self.setGeometry(100, 100, 600, 400)

        # Creamos un widget principal y un layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Creamos la barra lateral izquierda para las categorías
        self.category_frame = QFrame()
        self.category_frame.setFrameShape(QFrame.StyledPanel)
        self.category_layout = QVBoxLayout(self.category_frame)

        self.category_label = QLabel("Categorías")
        self.category_layout.addWidget(self.category_label)

        self.category_list = QListWidget()
        self.category_list.addItems(["Personal", "Trabajo", "Escuela"])
        self.category_layout.addWidget(self.category_list)

        self.main_layout.addWidget(self.category_frame)

        # Creamos el área principal derecha para mostrar las notas
        self.notes_frame = QFrame()
        self.notes_frame.setFrameShape(QFrame.StyledPanel)
        self.notes_layout = QVBoxLayout(self.notes_frame)

        self.notes_label = QLabel("Notas")
        self.notes_layout.addWidget(self.notes_label)

        self.notes_edit = QTextEdit()
        self.notes_layout.addWidget(self.notes_edit)

        self.save_button = QPushButton("Guardar")
        self.notes_layout.addWidget(self.save_button)

        self.main_layout.addWidget(self.notes_frame)

        # Conectamos la señal de cambio de selección en la lista de categorías
        self.category_list.currentItemChanged.connect(self.display_notes)

    def display_notes(self):
        # Aquí agregarías lógica para mostrar las notas correspondientes a la categoría seleccionada
        pass
QGroupBox
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()
    window.show()
    sys.exit(app.exec())