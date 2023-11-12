import os 
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QFileDialog
# QPushButton, , QGraphicsPixmapItem
from PyQt5 import QtGui, QtWidgets, QtCore

from ui.main import Ui_MainWindow
from .widgets import SyncedGraphicsView, ImageLabel
from .config import Config

class ViewerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ViewerApp, self).__init__()
        self.initAll()

        # UI window
        self.setWindow(self)
        self.setupUi(self)

        self.bindEvent()
    
    def initAll(self):
        self.folderPaths = {}
        self.graphicsViews = {}
        self.scenes = {}

        self.imageFilenames = None
        self.currentIndex = 0  # 当前显示的图片索引

    def bindEvent(self):
        self.actionLoadSubFolders.triggered.connect(self.loadAllSubFolders)
        self.actionAdd1Folder.triggered.connect(self.addFolder)
        # self.pushButtonAdd1Folder.clicked.connect(self.loadFolders)

        self.actionDel1Folder.triggered.connect(lambda: self.deleteFolder(list(self.folderPaths.keys())[-1]))
        # self.pushButtonDel1Folder.clicked.connect(lambda: self.deleteFolder(list(self.folderPaths.keys())[-1]))
    
    def checkFolder(self, verbose=False):
        for filename in self.imageFilenames:
            for k, folder in self.folderPaths.items():
                if not os.path.exists(os.path.join(folder, filename)):
                    if verbose:
                        print(f'File {filename} does not exist in folder {folder}')
                    continue
            self.imageFilenames.remove(filename)
                    

    def deleteFolder(self, base_key):
        del self.folderPaths[base_key]
        # del self.imageFilenames[base_key]
        # clear the view and scene
        self.graphicsViews[base_key].scene().clear()
        del self.graphicsViews[base_key]
        del self.scenes[base_key]
        
        self.checkFolder()

    def loadFolder(self, folder):
        if folder:
            base_key = os.path.basename(folder)
            if base_key in self.folderPaths.keys():
                print(f'Folder {folder} already loaded')
                return
            self.folderPaths[base_key] = folder
            self.createGraphicsView(base_key)
            tmp_files = self.scanDir(base_key, full_path=False)
            print(f'Folder {folder}, {len(tmp_files)} files found')

            # in case of different file length in folders, collect all file names
            if self.imageFilenames is None:
                self.imageFilenames = tmp_files
            else:
                self.imageFilenames = list(set((*tmp_files, *self.imageFilenames)))
            print(f'Total {len(self.imageFilenames)} files counted')
            self.update()

    def addFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.loadFolder(folder)

    def loadAllSubFolders(self):
        self.initAll()
        target = QFileDialog.getExistingDirectory(self, "Select Folder")
        # target = '/Users/celine/Downloads/LFW'
        # target = '/Users/celine/Downloads/test'
        dirs = os.listdir(target)
        for d in dirs:
            if d.startswith('.'):
                continue
            folder = os.path.join(target, d)
            self.loadFolder(folder)
    
    def scanDir(self, base_key, recursive=False, full_path=False, suffix=('.png', '.jpg', '.jpeg')):
        '''
        Args:
            recursive: to load images in folder and subfolders recursively. (#TODO)
        '''
        folder = self.folderPaths[base_key]
        if not recursive:
            filenames = [f for f in os.listdir(folder) if f.endswith(suffix)]
        if full_path:
            filenames = [os.path.join(folder, f) for f in filenames]
        filenames.sort()

        return filenames

    def loadImages(self, path):
        pixmap = QtGui.QPixmap(path).scaledToWidth(Config['IMG_SIZE'])
        return pixmap

    def update(self):
        imgname = self.imageFilenames[self.currentIndex]
        # print('crt', imgname)
        for key, view in self.graphicsViews.items():
            view.scene().clear()

            # add image
            img_path = os.path.join(self.folderPaths[key], imgname)
            title_str = key+'/'+os.path.basename(img_path)[:-4]
            if not os.path.exists(img_path):
                title_str += f'\nDoes not exist :('
            else:
                Qimage = self.loadImages(img_path)
                view.scene().addPixmap(Qimage)
                title_str += f'\n(index: {self.currentIndex})'

            # add title
            qText = QGraphicsTextItem(title_str)
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
        # if k == QtCore.Qt.Key_Left or k == QtCore.Qt.Key_Up:
        if k == QtCore.Qt.Key_A or k == QtCore.Qt.Key_W:
            self.currentIndex -= 1
            if self.currentIndex < 0:
                self.currentIndex = 0
        # elif k == QtCore.Qt.Key_Right or k == QtCore.Qt.Key_Down:
        elif k == QtCore.Qt.Key_Space or k == QtCore.Qt.Key_S or k == QtCore.Qt.Key_D:
            self.currentIndex += 1
            image_num = len(self.imageFilenames)
            if self.currentIndex >= image_num:
                self.currentIndex = image_num - 1
        self.update()