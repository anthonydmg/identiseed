from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QMainWindow, QApplication

import sys
import time

from PySide6.QtCore import QRunnable, Slot, QThreadPool
from PySide6.QtCore import QTimer
import rasterio

class Worker(QRunnable):

    @Slot() # QtCore.Slot
    def run(self) -> None:
        print("Thread start")

        dataset = rasterio.open("./sample_image/AMAZ-46-02.bil")
        frame_bands = dataset.read()
        dataset.close()
        #time.sleep(5)

        print('Thread complete')
    

class MainWindow(QMainWindow):


    def __init__(self):
        super(MainWindow, self).__init__()

        self.counter = 0

        layout = QVBoxLayout()

        self.l = QLabel("Start")
        b = QPushButton("DANGER!")

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        b.pressed.connect(self.oh_no)

        layout.addWidget(self.l)
        layout.addWidget(b)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()

    def oh_no(self):
        worker = Worker()
        self.threadpool.start(worker)

    def recurring_timer(self):
        self.counter +=1
        self.l.setText("Counter: %d" % self.counter)


app = QApplication(sys.argv)
window = MainWindow()
app.exec()
