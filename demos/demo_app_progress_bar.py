import sys
import time
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QProgressBar

def do_work(progress_changed):
    # Simular un proceso que tarda mucho en ejecutarse
    for i in range(101):
        time.sleep(0.1)
        progress_changed.emit(i)
    # Devolver datos al finalizar el proceso
    return "Resultado 1", "Resultado 2"

class Worker(QObject):  # Creamos una clase Worker para tener un QObject que emita la señal
    progress_changed = Signal(int)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proceso en segundo plano")
        self.setGeometry(100, 100, 300, 250)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.start_button = QPushButton("Iniciar proceso")
        self.start_button.clicked.connect(self.start_process)
        self.layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        self.thread = QThread()
        self.thread.started.connect(self.start_work)
        self.thread.finished.connect(self.process_finished)

    def start_process(self):
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.thread.start()

    def start_work(self):
        # Crear un Worker y conectar la señal del Worker a los métodos de actualización de la interfaz de usuario
        worker = Worker()
        worker.progress_changed.connect(self.update_progress)
        
        # Mover el Worker al hilo secundario y ejecutar el trabajo
        result = do_work(worker.progress_changed)
        # Emitir la señal finished con los datos devueltos
        self.thread.finished.emit(result)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def process_finished(self, result):
        # Este método se llama cuando el proceso en segundo plano ha terminado
        self.start_button.setEnabled(True)
        print("Proceso terminado")
        # Usar los datos devueltos en la interfaz
        print("Datos devueltos:", result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())