import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MplCanvas(FigureCanvas):
    def __init__(self, nombres, estaturas, parent=None):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)

        # Colores para cada punto
        colores = np.arange(len(nombres))

        # Crear el gráfico de dispersión
        scatter = self.ax.scatter(range(1, len(nombres) + 1), estaturas, c=colores, cmap='viridis')

        # Añadir etiquetas a cada punto
        for i, nombre in enumerate(nombres):
            self.ax.text(i + 1, estaturas[i], nombre, fontsize=9, ha='left', va='bottom')

        # Crear la leyenda manualmente
        handles = []
        labels = nombres
        cmap = plt.cm.get_cmap('viridis')
        for i, nombre in enumerate(nombres):
            color = cmap(i / len(nombres))
            handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=nombre))

        self.ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1, 1))

        # Añadir etiquetas y título
        self.ax.set_title('Estaturas de Personas')
        self.ax.set_xlabel('Personas')
        self.ax.set_ylabel('Estatura (cm)')
        self.ax.set_xticks(range(1, len(nombres) + 1))
        self.ax.set_xticklabels(nombres, rotation=45, ha='right')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Datos de ejemplo (nombres y estaturas)
        nombres = ['Persona A', 'Persona B', 'Persona C', 'Persona D', 'Persona E',
                   'Persona F', 'Persona G', 'Persona H', 'Persona I', 'Persona J']
        estaturas = [165, 170, 155, 180, 168, 172, 160, 175, 185, 162]

        # Crear widget de gráfico de dispersión
        self.canvas = MplCanvas(nombres, estaturas)

        # Configurar diseño de la ventana principal
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        # Crear un contenedor central y establecer el diseño
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Configurar la ventana principal
        self.setWindowTitle("Gráfico de Dispersión de Estaturas")
        self.setGeometry(100, 100, 800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())