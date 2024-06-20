from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QPushButton, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

class ScrollableWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        
        # Crear el QScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Crear el widget contenedor para el QScrollArea
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_widget.setLayout(self.container_layout)
        
        # Añadir el widget contenedor al QScrollArea
        self.scroll_area.setWidget(self.container_widget)
        
        # Añadir el QScrollArea al layout principal
        self.main_layout.addWidget(self.scroll_area)
        
        # Añadir un botón para agregar elementos
        self.add_button = QPushButton("Agregar elemento", self)
        self.add_button.clicked.connect(self.add_element)
        self.main_layout.addWidget(self.add_button)
        
        # Configurar el tamaño mínimo y máximo del QScrollArea
        self.scroll_area.setMinimumSize(100, 100)  # Tamaño mínimo
        #self.scroll_area.setMaximumHeight(200)     # Tamaño máximo en altura
        
    def add_element(self):
        # Crear un nuevo botón y añadirlo al layout del contenedor
        new_button = QPushButton(f"Elemento {self.container_layout.count() + 1}", self.container_widget)
        self.container_layout.addWidget(new_button)
        
        # Ajustar el tamaño del QScrollArea si es necesario
        self.adjust_scroll_area_size()
    
    def adjust_scroll_area_size(self):
        # Ajustar la altura del contenedor según el número de elementos
        num_elements = self.container_layout.count()
        new_height = min(300, 20 + num_elements * 40)  # Ajustar este cálculo según tus necesidades
        self.scroll_area.setFixedHeight(new_height)

if __name__ == "__main__":
    app = QApplication([])
    window = ScrollableWidget()
    window.show()
    app.exec()