from PyQt5.QtWidgets import QGraphicsView
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt

from .config import Config

class SyncedGraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super(SyncedGraphicsView, self).__init__(*args, **kwargs)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, event):
        factor = 1.1
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)

class ImageLabel(QtWidgets.QLabel):
    def __init__(self, parent, image, text, *args, **kwargs):
        super(ImageLabel, self).__init__(parent, *args, **kwargs)
        self.Qimage = image
        self.text
    
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(QtCore.QPoint(), self.Qimage)

        pen = QtGui.QPen(Qt.red)
        pen.setWidth(2)
        qp.setPen(pen)

        font = QtGui.QFont()
        font.setFamily('Times')
        font.setBold(True)
        font.setPointSize(Config['IMG_SIZE'] // 10)
        qp.setFont(font)

        qp.drawText(5, 5, self.text)
        qp.end()