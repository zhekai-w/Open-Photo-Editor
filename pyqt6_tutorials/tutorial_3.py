'''
This tutorial includes Using QPushButton, QCheckBox, QComboBox, QLabel and QSlider widgets
'''
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDial,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QSlider,
    QSpinBox,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

        # QLabel
        widget = QLabel("Hello")
        font = widget.font()
        font.setPointSize(30)
        widget.setFont(font)
        # widget.setPixmap(QPixmap('skyscraper.jpg'))
        # widget.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # QCheckBox
        widget_checkbox = QCheckBox("check checked")
        widget_checkbox.setCheckState(Qt.CheckState.Checked)
        widget_checkbox.stateChanged.connect(self.show_state)
        self.setCentralWidget(widget_checkbox)

    def show_state(self, s):
        print(s == Qt.CheckState.Checked.value)
        print(s)


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
