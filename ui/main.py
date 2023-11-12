from .base_ui import BaseUI

class Ui_MainWindow(BaseUI):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
    
    def setWindow(self, MainWindow):
        self.MainWindow = MainWindow
    
    def keyPressEvent(self, event):
        self.MainWindow.keyPressEvent(event)