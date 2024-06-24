import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PySide6.QtGui import QDesktopServices, QAction 
from PySide6.QtCore import QUrl
#from PySide6 QAction, QFileDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aplicación de Escritorio con PySide6")

        # Crea la barra de menú
        menubar = self.menuBar()

        # Crea el menú "Ayuda"
        ayuda_menu = menubar.addMenu("Ayuda")

        # Crea la acción "Manual de Usuario"
        manual_usuario_action = QAction("Manual de Usuario", self)
        manual_usuario_action.triggered.connect(self.mostrar_manual_usuario)
        ayuda_menu.addAction(manual_usuario_action)

    def mostrar_manual_usuario(self):
        # Ruta al archivo PDF del manual de usuario
        pdf_path = "./Manual-Usuario-IdentiTree.pdf"

        # Abre el PDF en el visor predeterminado del sistema
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path)):
            QMessageBox.critical(self, "Error", "No se pudo abrir el manual de usuario.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())