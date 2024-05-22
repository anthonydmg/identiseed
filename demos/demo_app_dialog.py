import sys
from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar, QCheckBox, QPushButton, QDialog, QDialogButtonBox, QVBoxLayout
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Something happened, is that OK?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("My Awesome App")

        button = QPushButton("Press me for a dialog!")
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)

        self.setStatusBar(QStatusBar(self))
    def button_clicked(self, s):
        print("click", s)
        dlg = CustomDialog()
        dlg.setWindowTitle("HELLO!")
        if dlg.exec():
            print("Success!")
        else:
            print("Cancel!")

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()