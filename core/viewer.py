import os 
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QFileDialog
# QPushButton, , QGraphicsPixmapItem
from PyQt5 import QtGui, QtWidgets, QtCore

from .ui import Ui_MainWindow
from .widgets import SyncedGraphicsView, ImageLabel
from .config import Config

class ViewerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ViewerApp, self).__init__()
        self.folderPaths = {}
        self.imageFilenames = {}
        self.graphicsViews = {}
        self.scenes = {}
        self.currentIndex = 0  # 当前显示的图片索引
        self.setupUi(self)

        self.bindEvent()

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
        # print('delete ', base_key, len(self.folderPaths))
        # self.update()

    def loadFolders(self):
        target = QFileDialog.getExistingDirectory(self, "Select Folder")
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
            qText = QGraphicsTextItem(key+'/'+os.path.basename(img_path)[:-4]+f'({self.currentIndex})')
            # qText.adjustSize(Config['IMG_SIZE'] // 18)
            qText.setDefaultTextColor(QtCore.Qt.red)
            view.scene().addItem(qText)

            # view.fitInView(view.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
            view.show()
    
    def createGraphicsView(self, base_key):
        size_w = size_h = Config['WINDOW_SIZE']
        border = Config['BORDER']
        x_margin = 10
        y_margin = 30
        
        view = SyncedGraphicsView(self)
        # view = QGraphicsView(self)
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
        if k == QtCore.Qt.Key_Left or k == QtCore.Qt.Key_Up:
            self.currentIndex -= 1
            if self.currentIndex < 0:
                self.currentIndex = 0
        elif k == QtCore.Qt.Key_Right or k == QtCore.Qt.Key_Down:
            self.currentIndex += 1
            image_num = len(self.imageFilenames[list(self.folderPaths.keys())[-1]])
            if self.currentIndex >= image_num:
                self.currentIndex = image_num - 1
        self.update()