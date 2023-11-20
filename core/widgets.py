from PyQt5.QtWidgets import QGraphicsView
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt

# from config.window import WindowConfig

# class SyncedGraphicsView(QGraphicsView):
#     def __init__(self, *args, **kwargs):
#         super(SyncedGraphicsView, self).__init__(*args, **kwargs)
#         self.setDragMode(QGraphicsView.ScrollHandDrag)

#     def wheelEvent(self, event):
#         factor = 1.1
#         if event.angleDelta().y() < 0:
#             factor = 1.0 / factor
#         self.scale(factor, factor)

