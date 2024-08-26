from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
  QApplication, QMainWindow, QLabel,
  QLineEdit,
  QVBoxLayout,
  QHBoxLayout,
  QWidget
)

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow): 
  def __init__(self):
    super().__init__()
    self.setWindowTitle("My App")
    
    self.label = QLabel()
    self.line_edit = QLineEdit()
    self.line_edit.textChanged.connect(self.label.setText)

    layout_vertical = QVBoxLayout()
    layout_vertical.addWidget(self.line_edit)
    layout_vertical.addWidget(self.label)

    container = QWidget()
    container.setLayout(layout_vertical)

    self.setCentralWidget(container)

app = QApplication([])
window = MainWindow()
window.show()

app.exec_()
