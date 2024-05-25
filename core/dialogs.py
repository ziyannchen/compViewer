from ui import Ui_Dialog

import sys
# from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QVBoxLayout, QListWidgetItem, QPushButton, QDialog, QVBoxLayout, QListWidget, \
                             QMessageBox, QLabel, QWidget, QLineEdit, QDialogButtonBox, QHBoxLayout)

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
    

class EditableListDialog(QDialog):
    def __init__(self, dict):
        super().__init__()
        self.dict = dict

        self.setWindowTitle("Editable List Dialog")
        self.resize(400, 400)

        self.list_widget = QListWidget()
        # self.list_widget.setSpacing(0)

        # self.add_button = QPushButton("Add Item")
        # self.add_button.clicked.connect(self.add_item)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.confirm_save)

        button_layout = QHBoxLayout()
        # button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.save_button)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.edited_values = {}
    
        self.populate_list()

    def populate_list(self):
        for attr, value in vars(self.dict).items():
            # 创建一个包含标签和编辑框的自定义小部件
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            
            label = QLabel(f"{attr}:")
            # label.setFixedWidth(100)  # 固定标签宽度
            # label.setFixedHeight(10)  # 固定标签高度
            line_edit = QLineEdit(str(value))
            line_edit.setObjectName(attr)  # 使用属性名称作为对象名称
            
            item_layout.addWidget(label)
            item_layout.addWidget(line_edit)
            # item_layout.addStretch()
            item_widget.setLayout(item_layout)

            # 将自定义小部件添加到列表项中
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.setItemWidget(list_item, item_widget)

    def confirm_save(self):
        # confirm dialog
        reply = QMessageBox.question(self, 'Confirm Save', 'Are you sure you want to save the changes?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.save_items()
            self.accept()  # close dialog

    def save_items(self):
        for i in range(self.list_widget.count()):
            list_item = self.list_widget.item(i)
            item_widget = self.list_widget.itemWidget(list_item)
            line_edit = item_widget.findChild(QLineEdit)
            attr = line_edit.objectName()
            value = line_edit.text()
            self.edited_values[attr] = value

    def get_edited_values(self):
        return self.edited_values