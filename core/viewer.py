import os
from typing import Dict
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QFileDialog
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QDir, QPoint

from .ui import Ui_MainWindow
from .config import Config


class ViewerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ViewerApp, self).__init__()
        self.folderPaths = {}
        self.imageFilenames = {}
        self.graphicsViews: Dict[str, QGraphicsView] = {}
        self.scenes = {}
        self.currentIndex = 0  # 当前显示的图片索引
        self.mousePressed = False
        self.lastMousePos = QPoint()
        self.setupUi(self)
        self.bindEvent()
        
        self.titles = {}

    def bindEvent(self):
        self.pushButton_Add.clicked.connect(self.loadFolders)
        self.pushButton_delete.clicked.connect(lambda: self.deleteFolder(list(self.folderPaths.keys())[-1]))
    
    def deleteFolder(self, base_key):
        del self.folderPaths[base_key]
        del self.imageFilenames[base_key]
        # clear the view and scene
        self.graphicsViews[base_key].scene().clear()
        del self.graphicsViews[base_key]
        del self.scenes[base_key]

    def loadFolders(self):
        target = QFileDialog.getExistingDirectory(self, "Select Folder")
        target = QDir.toNativeSeparators(target)
        # target = '/Users/celine/Downloads/LFW'
        dirs = os.listdir(target)
        for d in dirs:
            if d.startswith('.'):
                continue
            folder = os.path.join(target, d)
            print(folder)
            if folder:
                base_key = os.path.basename(folder)
                self.folderPaths[base_key] = folder
                self.createGraphicsView(base_key)
                self.scanDir(base_key)
    
    def scanDir(self, base_key):
        self.imageFilenames[base_key] = []
        folder = self.folderPaths[base_key]
        for filename in os.listdir(folder):
            if filename.endswith(('.jpg', '.png')):
                self.imageFilenames[base_key].append(os.path.join(folder, filename))
        self.imageFilenames[base_key].sort()
        self.update()
        # print('loaded')

    def loadImages(self, path):
        pixmap = QtGui.QPixmap(path).scaledToWidth(Config['IMG_SIZE'])
        return pixmap

    def update(self):
        for key, view in self.graphicsViews.items():
            view.scene().clear()

            # add image
            img_path = self.imageFilenames[key][self.currentIndex]
            Qimage = self.loadImages(img_path)
            view.scene().addPixmap(Qimage)

            # add title
            title = f"{os.path.basename(key)[:10]},{os.path.basename(img_path)}"
            qText = QGraphicsTextItem(title)
            qText.setDefaultTextColor(QtCore.Qt.red)
            qText.setScale(1.5)
            view.scene().addItem(qText)
            self.titles[key] = qText

            view.show()
    
    def createGraphicsView(self, base_key):
        size_w = size_h = Config['WINDOW_SIZE']
        border = Config['BORDER']
        x_margin = 10
        y_margin = 30
        
        # view = SyncedGraphicsView(self)
        view = QGraphicsView(self)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
        scene = QGraphicsScene(self)
        view.setScene(scene)
        # print('view and scene created')
        self.graphicsViews[base_key] = view
        self.scenes[base_key] = scene

        # cnt = self.width() // (size + border)
        x_crt = (len(self.graphicsViews.keys()) - 1) % (Config['X_NUM'])
        y_crt = (len(self.graphicsViews.keys()) - 1) // (Config['X_NUM'])
        # print(x_crt, y_crt)
        x = x_margin + x_crt * (size_w + border)
        y = y_margin + y_crt * (size_h + border)
        view.setGeometry(x, y, size_w, size_h)
        # print(x, y, size_w, size_h, self.graphicsViews.keys())
    
    def keyPressEvent(self, event):
        k = event.key()
        # print('pressed', k)
        # if k == QtCore.Qt.Key_Left or k == QtCore.Qt.Key_Up:
        if k == QtCore.Qt.Key_A or k == QtCore.Qt.Key_W:
            self.currentIndex -= 1
            if self.currentIndex < 0:
                self.currentIndex = 0
        # elif k == QtCore.Qt.Key_Right or k == QtCore.Qt.Key_Down:
        elif k == QtCore.Qt.Key_Space or k == QtCore.Qt.Key_S or k == QtCore.Qt.Key_D:
            self.currentIndex += 1
            image_num = len(self.imageFilenames[list(self.folderPaths.keys())[-1]])
            if self.currentIndex >= image_num:
                self.currentIndex = image_num - 1
        self.update()

    def wheelEvent(self, event):
        for key in self.graphicsViews.keys():
            view = self.graphicsViews[key]
            factor = 1.1
            if event.angleDelta().y() < 0:
                factor = 1.0 / factor
            view.scale(factor, factor)
            title_item = self.titles[key]
            # 获取视图的左上角在场景中的坐标
            targetPos = view.mapToScene(0, 0)  # 视图左上角的场景坐标
            title_item.setPos(targetPos)  # 吸附到目标位置
            title_item.setScale(title_item.scale() * (1 / factor))

    def mousePressEvent(self, event):
        self.mousePressed = True
        self.lastMousePos = event.pos()

    def mouseReleaseEvent(self, event):
        self.mousePressed = False

    def mouseMoveEvent(self, event) -> None:
        if self.mousePressed:
            # 计算鼠标移动距离
            dx = event.x() - self.lastMousePos.x()
            dy = event.y() - self.lastMousePos.y()
            self.lastMousePos = event.pos()

            # 更新图片位置 and titles
            for key in self.graphicsViews.keys():
                view = self.graphicsViews[key]
                h, v = view.horizontalScrollBar().value(), view.verticalScrollBar().value()
                view.horizontalScrollBar().setValue(h - dx)
                view.verticalScrollBar().setValue(v - dy)
                title_item = self.titles[key]
                # 获取视图的左上角在场景中的坐标
                targetPos = view.mapToScene(0, 0)  # 视图左上角的场景坐标
                title_item.setPos(targetPos)  # 吸附到目标位置
