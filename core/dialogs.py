from ui import Ui_Dialog

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout

class Dialog(QDialog, Ui_Dialog):
    def __init__(self, text, title='Dialog'):
        super(Dialog, self).__init__()
        self.setupUi(self, title=title, text=text)

    # 获取输入框的值的方法
    def get_input_text(self):
        return self.lineEdit.text()