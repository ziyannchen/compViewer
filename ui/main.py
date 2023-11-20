from .base import Ui_Base

# from PyQt5.QtWidgets import QDesktopWidget

class MainWindowUI(Ui_Base):
    def __init__(self):
        super(MainWindowUI, self).__init__()
    
    def setWindow(self, MainWindow):
        self.MainWindow = MainWindow
    
    def keyPressEvent(self, event):
        self.MainWindow.keyPressEvent(event)