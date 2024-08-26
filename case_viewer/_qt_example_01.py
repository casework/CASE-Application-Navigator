from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow): 
  def __init__(self):
    super().__init__()
    self.setWindowTitle("My App")
    self.setFixedSize(QSize(400, 300))
    self.button = QPushButton("Press Me!")
    self.button.setCheckable(True)
    self.button.clicked.connect(self.the_button_was_clicked)
    # Set the central widget of the Window.
    self.setCentralWidget(self.button)

  def the_button_was_clicked(self):
    self.button.setText("You already clicked me.") 
    self.button.setEnabled(False)

    # Also change the window title.
    self.setWindowTitle("My Oneshot App")

app = QApplication([])
window = MainWindow()
window.show()

app.exec_()
