import sys
from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar, QCheckBox, QPushButton, QDialog, QDialogButtonBox, QVBoxLayout, QMessageBox
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("My Awesome App")

        button = QPushButton("Press me for a dialog!")
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)

    def button_clicked(self, s):

        button = QMessageBox.question(self, "Question dialog", "The longer message")

        if button == QMessageBox.Yes:
            print("Yes!")
        else:
            print("No!")


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()