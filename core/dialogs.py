from ui import Ui_Dialog

import sys
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QPushButton, QDialog, QVBoxLayout, QListWidget, QDialogButtonBox

class EditDialog(QDialog, Ui_Dialog):
    def __init__(self, label, title='Dialog', edit='line'):
        '''
        Args:
            label: str, label of the input box
            title: str, title of the dialog
            edit: str, type of the input box, 'line' or 'text' for 'lineEdit' or 'textEdit'
        '''
        super(EditDialog, self).__init__()
        assert edit in ['line', 'text'], f'edit type {edit} not implemented'
        self.edit = edit
        self.setupUi(self, title=title, label=label, edit=edit)

    # 获取输入框的值的方法
    def get_input_text(self):
        if self.edit == 'text':
            return self.editor.toPlainText()
        return self.editor.text()
    
class ListDialog(QDialog):
    def __init__(self, items, title="Select from list", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        # 创建布局
        layout = QVBoxLayout(self)

        # 创建列表控件
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(items)
        layout.addWidget(self.list_widget)

        # 创建确认按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_selected_item(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None