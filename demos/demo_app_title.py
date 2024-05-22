import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTreeView, QWidget, QFileSystemModel, QLabel
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ejemplo de QTreeView y gráfico")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Crear y agregar el título de la sección
        section_title = QLabel("Explorador de archivos y gráfico de tamaño")
        section_title.setAlignment(Qt.AlignCenter)
        section_title.setStyleSheet("font-size: 20px; color: #333; background-color: #f0f0f0; padding: 5px;")
        self.layout.addWidget(section_title)

        # Crear y agregar la vista de árbol
        self.tree_view = QTreeView()
        self.layout.addWidget(self.tree_view)

        # Configurar modelo de sistema de archivos
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.tree_view.setModel(self.model)

        # Crear y agregar la sección del gráfico
        self.graph_section = QWidget()
        self.layout.addWidget(self.graph_section)

        # Layout para la sección del gráfico
        self.graph_layout = QVBoxLayout(self.graph_section)

        # Crear y agregar el gráfico dentro de la sección del gráfico
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.graph_layout.addWidget(self.canvas)

        # Conectar selección de árbol con actualización del gráfico
        self.tree_view.selectionModel().selectionChanged.connect(self.update_graph)

    def update_graph(self):
        # Obtener la ruta del archivo seleccionado en el árbol
        selected_index = self.tree_view.currentIndex()
        file_path = self.model.filePath(selected_index)

        # Calcular el tamaño de los archivos en la carpeta seleccionada
        file_sizes = []
        if os.path.isdir(file_path):
            for dirpath, _, filenames in os.walk(file_path):
                for filename in filenames:
                    file_sizes.append(os.path.getsize(os.path.join(dirpath, filename)))

        # Actualizar el gráfico de barras
        self.ax.clear()
        if file_sizes:
            self.ax.hist(file_sizes, bins=20, alpha=0.7, color='blue')
            self.ax.set_title('Distribución de tamaños de archivo')
            self.ax.set_xlabel('Tamaño del archivo (bytes)')
            self.ax.set_ylabel('Frecuencia')
        else:
            self.ax.text(0.5, 0.5, 'No hay archivos en esta carpeta', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())