
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QScrollArea, QLabel, QFrame, QHBoxLayout, QSizePolicy
import sys
import numpy as np
from PySide6.QtGui import QFont
from PySide6.QtCore import QRunnable, Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
class ScrollAreaExample(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Crear un widget de contenedor para los elementos
        container = QWidget(self)
        containerLayout = QVBoxLayout(container)
        
        # Agregar widgets al contenedor
        #containerLayout.addWidget(QLabel("Etiqueta 1"))
        #containerLayout.addWidget(QLabel("Etiqueta 2"))
        #containerLayout.addWidget(QLabel("Etiqueta 3"))
        #containerLayout.addWidget(QPushButton("Botón 1"))
        #containerLayout.addWidget(QPushButton("Botón 2"))
        
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
    

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gráfico con Leyenda Desplazable")

        # Crear el gráfico
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        x = np.linspace(400, 900, 100)
        y = [np.sin(x / 100 + i) * 20 + 40 + i for i in range(5)]

        for i, y_val in enumerate(y):
            sc.axes.plot(x, y_val, label=f'semilla-{i}')

        sc.axes.set_xlabel('Wavelength')
        sc.axes.set_ylabel('Radiance')

        # Crear el widget de desplazamiento para la leyenda
        scroll = QScrollArea()
        #scroll.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        scroll.setWidgetResizable(True)
        
        self.legend_container = QWidget()
        scroll.setWidget(self.legend_container)
        
        #self.legend_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        legend_layout = QVBoxLayout(self.legend_container)
        legend_layout.setSpacing(0)
        #legend_layout.setAlignment(Qt.AlignTop)
        # Agregar la leyenda
        for line in sc.axes.get_lines():
            label_text = line.get_label()
            color = line.get_color()

            # Crear un widget para cada entrada de la leyenda
            legend_entry = QWidget()
            entry_layout = QHBoxLayout()
            entry_layout.setAlignment(Qt.AlignCenter)
            color_patch = QLabel()
            color_patch.setFixedSize(40, 5)
            color_patch.setStyleSheet(f"background-color: {color}; border: none;")
            text_label = QLabel(label_text)
            text_label.setFont(QFont("Roboto", 11, QFont.Normal))
            entry_layout.addWidget(color_patch)
            entry_layout.addWidget(text_label)
            entry_layout.addStretch()
            legend_entry.setLayout(entry_layout)

            legend_layout.addWidget(legend_entry)
        
        # Crear un layout principal
        layout = QHBoxLayout()  # Usar QHBoxLayout para colocar la leyenda al costado
        layout.addWidget(sc)
        
        layout_scroll_section = QVBoxLayout()
        
        self.pad_widget_top = QWidget()
        self.pad_widget_top.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout_scroll_section.addWidget(self.pad_widget_top)
        layout_scroll_section.addWidget(scroll)
        self.pad_widget_button = QWidget()
        self.pad_widget_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout_scroll_section.addWidget(self.pad_widget_button)


        layout.addLayout(layout_scroll_section)
        
        container = QWidget()
        container.setLayout(layout)
        
        #self.legend_container.adjustSize()
        #scroll.adjustSize()
        self.setCentralWidget(container)

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()