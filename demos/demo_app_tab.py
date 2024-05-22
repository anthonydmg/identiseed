import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTabWidget, QLabel

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ejemplo de Tabs")
        self.setGeometry(100, 100, 400, 300)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # Tab 1
        tab1 = QWidget()
        tab_widget.addTab(tab1, "Tab 1")
        tab1_layout = QVBoxLayout()
        tab1.setLayout(tab1_layout)
        tab1_label = QLabel("Contenido del Tab 1")
        tab1_layout.addWidget(tab1_label)

        # Tab 2
        tab2 = QWidget()
        tab_widget.addTab(tab2, "Tab 2")
        tab2_layout = QVBoxLayout()
        tab2.setLayout(tab2_layout)
        tab2_label = QLabel("Contenido del Tab 2")
        tab2_layout.addWidget(tab2_label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())