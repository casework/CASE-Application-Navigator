from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QListWidget

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow): 
  def __init__(self):
    super().__init__()
    self.setWindowTitle("My App")
    widget = QListWidget()
    self.list_values = ["One", "Two", "Three"]
    widget.addItems(self.list_values)
    widget.currentItemChanged.connect(self.index_changed)
    self.setCentralWidget(widget)

  def index_changed(self, i): # i is an int
    print(i.text())
    #print(self.list_values[i])
  

app = QApplication([])
window = MainWindow()
window.show()

app.exec_()
