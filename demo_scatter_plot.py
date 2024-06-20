import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QHBoxLayout, QLabel, QScrollArea, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class ScatterPlotCanvas(FigureCanvas):
    def __init__(self, nombres, estaturas, parent=None):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.nombres = nombres
        self.estaturas = estaturas
        self.cmap = plt.cm.tab20
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        colores = self.cmap(np.linspace(0, 1, len(self.nombres)))

        # Crear el gráfico de dispersión con colores personalizados
        scatter = self.ax.scatter(range(1, len(self.nombres) + 1), self.estaturas, color=colores)

        # Añadir etiquetas a cada punto
        for i, nombre in enumerate(self.nombres):
            self.ax.text(i + 1, self.estaturas[i], nombre, fontsize=9, ha='left', va='bottom')

        # Crear la leyenda manualmente
        #handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colores[i], markersize=10, label=nombre) for i, nombre in enumerate(self.nombres)]
        #self.ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1, 1))

        # Añadir etiquetas y título
        self.ax.set_title('Estaturas de Personas')
        self.ax.set_xlabel('Personas')
        self.ax.set_ylabel('Estatura (cm)')
        self.ax.set_xticks(range(1, len(self.nombres) + 1))
        self.ax.set_xticklabels(self.nombres, rotation=45, ha='right')
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Datos de ejemplo (nombres y estaturas)
        self.nombres = ['Persona A', 'Persona B', 'Persona C', 'Persona D', 'Persona E',
                        'Persona F', 'Persona G', 'Persona H', 'Persona I', 'Persona J']
        self.estaturas = [165, 170, 155, 180, 168, 172, 160, 175, 185, 162]

        # Crear widget de gráfico de dispersión
        self.canvas = ScatterPlotCanvas(self.nombres, self.estaturas)

        # Configurar diseño de la ventana principal
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        # Controles para actualizar datos
        self.name_input = QLineEdit()
        self.height_input = QLineEdit()
        update_button = QPushButton("Actualizar Gráfico")
        update_button.clicked.connect(self.update_data)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Nombre:"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("Estatura:"))
        input_layout.addWidget(self.height_input)
        input_layout.addWidget(update_button)

        layout.addLayout(input_layout)

        # Crear área de scroll para la leyenda
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.legend_widget = QWidget()
        self.legend_layout = QGridLayout(self.legend_widget)
        self.scroll_area.setWidget(self.legend_widget)
        layout.addWidget(self.scroll_area)

        # Crear un contenedor central y establecer el diseño
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Configurar la ventana principal
        self.setWindowTitle("Gráfico de Dispersión de Estaturas")
        self.setGeometry(100, 100, 800, 600)

        # Inicializar la leyenda
        self.update_legend()

    def update_data(self):
        nombre = self.name_input.text()
        try:
            estatura = float(self.height_input.text())
        except ValueError:
            print("Por favor, introduce una estatura válida.")
            return

        if nombre and estatura > 0:
            self.nombres.append(nombre)
            self.estaturas.append(estatura)
            self.canvas.nombres = self.nombres
            self.canvas.estaturas = self.estaturas
            self.canvas.update_plot()
            self.update_legend()

    def update_legend(self):
        # Limpiar la leyenda actual
        for i in reversed(range(self.legend_layout.count())):
            self.legend_layout.itemAt(i).widget().setParent(None)

        # Colores para cada punto usando un colormap
        cmap = plt.cm.tab20
        colores = cmap(np.linspace(0, 1, len(self.nombres)))

        # Añadir cada elemento de la leyenda al layout de la leyenda
        for i, nombre in enumerate(self.nombres):
            color_patch = QLabel()
            color_patch.setStyleSheet(f'background-color: rgba({colores[i][0] * 255}, {colores[i][1] * 255}, {colores[i][2] * 255}, {colores[i][3] * 255});')
            color_patch.setFixedSize(20, 20)
            self.legend_layout.addWidget(color_patch, i, 0)
            self.legend_layout.addWidget(QLabel(nombre), i, 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())