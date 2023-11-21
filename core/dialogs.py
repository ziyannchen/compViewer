from ui import Ui_Dialog

import sys
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QPushButton, QDialog, QVBoxLayout

class Dialog(QDialog, Ui_Dialog):
    def __init__(self, label, title='Dialog', edit='line'):
        '''
        Args:
            label: str, label of the input box
            title: str, title of the dialog
            edit: str, type of the input box, 'line' or 'text' for 'lineEdit' or 'textEdit'
        '''
        super(Dialog, self).__init__()
        assert edit in ['line', 'text'], f'edit type {edit} not implemented'
        self.edit = edit
        self.setupUi(self, title=title, label=label, edit=edit)

    # 获取输入框的值的方法
    def get_input_text(self):
        if self.edit == 'text':
            return self.editor.toPlainText()
        return self.editor.text()