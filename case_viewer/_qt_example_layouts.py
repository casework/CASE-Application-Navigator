from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow 

from _qt_layout_color_widget import Color


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow): 
  def __init__(self):
    super().__init__()
    self.setWindowTitle("My App")
    widget = Color("red")
    self.setCentralWidget(widget)  

app = QApplication([])
window = MainWindow()
window.show()

app.exec_()
