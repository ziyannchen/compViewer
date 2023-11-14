import os
from natsort import natsorted
from PyQt5.QtWidgets import (QMainWindow, QGraphicsView, QGraphicsScene, 
                             QGraphicsTextItem, QFileDialog, QDialog, QMessageBox)
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QDir, QPoint

from ui import MainWindowUI
from utils.file import copyFile, fuzzySearchList
from config.window import WindowConfig
from .dialogs import Dialog
# from .widgets import SyncedGraphicsView, ImageLabel


class ViewerApp(QMainWindow, MainWindowUI):
    def __init__(self):
        super(ViewerApp, self).__init__()
        self.initAll()

        # UI window
        self.setWindow(self)
        self.mousePressed = False
        self.lastMousePos = QPoint()
        self.setupUi(self)
        self.bindEvent()
    
    def initAll(self):
        self.folderPaths = {}
        self.graphicsViews = {}

        self.imageFilenames = None
        self.currentIndex = -1  # 当前显示的图片索引
        self.titles = {}

    def bindEvent(self):
        # file
        self.actionLoadSubFolders.triggered.connect(self.loadAllSubFolders)
        self.actionAdd1Folder.triggered.connect(self.addFolder)
        self.actionDel1Folder.triggered.connect(lambda: self.deleteFolder())

        self.actionGoTo.triggered.connect(self.actionGoToTriggered)
        self.actionGoToName.triggered.connect(lambda: self.actionGoToTriggered(by_name=True))
        self.actionSave.triggered.connect(self.actionSaveTriggered)

    def checkFolder(self, verbose=False):
        for filename in self.imageFilenames:
            for k, folder in self.folderPaths.items():
                if not os.path.exists(os.path.join(folder, filename)):
                    if verbose:
                        print(f'File {filename} does not exist in folder {folder}')
                    continue
            self.imageFilenames.remove(filename)
                    
    def deleteFolder(self):
        '''
        Delete the last one folder by default.
        TODO: delete the selected folder.
        '''
        if len(self.folderPaths) == 0:
            print('No folder loaded')
            return
        base_key = list(self.folderPaths.keys())[-1]
        del self.folderPaths[base_key]
        self.checkFolder()

        # clear the view and scene
        self.graphicsViews[base_key].scene().clear()
        del self.graphicsViews[base_key]

    def loadFolder(self, folder):
        if os.path.isdir(folder):
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
            self.currentIndex = 0 if len(self.imageFilenames) > 0 else -1
            self.imageFilenames = natsorted(self.imageFilenames)
            print(f'Total {len(self.imageFilenames)} files counted')
            self.update()

    def addFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.loadFolder(folder)

    def loadAllSubFolders(self):
        self.initAll()
        # target = QFileDialog.getExistingDirectory(self, "Select Folder")
        target = '/Users/celine/Downloads/LFW'
        target = QDir.toNativeSeparators(target)
        # target = '/Users/celine/Downloads/test'
        dirs = natsorted(os.listdir(target))
        for d in dirs:
            if d.startswith('.'):
                continue
            folder = os.path.join(target, d)
            self.loadFolder(folder)
    
    def scanDir(self, base_key, recursive=False, full_path=False, suffix=('.png', '.jpg', '.jpeg')):
        '''
        Args:
            recursive: to load images in folder and subfolders recursively. (TODO)
        '''
        folder = self.folderPaths[base_key]
        if not recursive:
            filenames = [f for f in os.listdir(folder) if f.endswith(suffix)]
        if full_path:
            filenames = [os.path.join(folder, f) for f in filenames]
        filenames.sort()

        return filenames

    def loadImages(self, path):
        pixmap = QtGui.QPixmap(path).scaledToWidth(WindowConfig['IMG_SIZE_W'])
        return pixmap

    def update(self):
        imgname = self.imageFilenames[self.currentIndex]
        # print('crt', imgname)
        for key, view in self.graphicsViews.items():
            view: QGraphicsView
            # create new title
            img_path = os.path.join(self.folderPaths[key], imgname)
            dataset = self.folderPaths[key].split(os.sep)[-2]
            # title_str = f'{os.sep}'.join([dataset, key, os.path.basename(img_path)[:-4]])
            title_str = f'\n'.join([dataset, key, os.path.basename(img_path)[:-4]])
            if not os.path.exists(img_path):
                title_str += f'\nDoes not exist :('
            else:
                # title_str += f'\n(index: {self.currentIndex})'
                title_str += f' ({self.currentIndex})'
            qText = QGraphicsTextItem(title_str)
            qText.setDefaultTextColor(QtCore.Qt.red)
            if key in self.titles:
                qText.setScale(self.titles[key].scale())
                qText.setPos(self.titles[key].pos())
            else:
                qText.setScale(1.5)
            self.titles[key] = qText
            view.scene().clear()

            # add image
            Qimage = self.loadImages(img_path)
            view.scene().addPixmap(Qimage)
            view.scene().addItem(qText)

            view.show()
    
    def createGraphicsView(self, base_key):
        size_w = WindowConfig['WINDOW_SIZE_W']; size_h = WindowConfig['WINDOW_SIZE_H']
        border = WindowConfig['BORDER']
        x_margin = y_margin = 10
        
        # view = SyncedGraphicsView(self)
        view = QGraphicsView(self)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
        scene = QGraphicsScene(self)
        view.setScene(scene)
        # print('view and scene created')
        self.graphicsViews[base_key] = view

        x_crt = (len(self.graphicsViews.keys()) - 1) % (WindowConfig['X_NUM'])
        y_crt = (len(self.graphicsViews.keys()) - 1) // (WindowConfig['X_NUM'])
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
        # elif k == QtCore.Qt.Key_Plus:
        #     print(k)
        # elif k == QtCore.Qt.Key_Minus:
        #     print(k)
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

    def dataLoadedCheck(self):
        if self.imageFilenames is None: # equals to self.currentIndex == -1
            print('No data loaded')
            return False
        return True
    
    def actionSaveTriggered(self):
        if self.currentIndex == -1:
            print('No data to save!')
            return 
        save_folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        print('save_folder', save_folder)
        if save_folder:
            self.save_dir = save_folder
            save_folder = QDir.toNativeSeparators(save_folder)
            self.saveImageGroup(save_folder)

    def saveImageGroup(self, save_dir):
        os.makedirs(save_dir, exist_ok=True)
        imgname, ext = os.path.splitext(self.imageFilenames[self.currentIndex])

        info_str = {
            'title':'Info', 
            'text': 'All imgaes are saved susccessfully'}
        for key in self.graphicsViews.keys():
            img_path = os.path.join(self.folderPaths[key], imgname+ext)
            target_path = os.path.join(save_dir, f'{self.currentIndex}_{imgname}', f'{key}{ext}')
            if not copyFile(target_path, img_path):
                print(f'Copy {img_path} failed')
                info_str['title'] = 'Error'
                info_str['text'] = f'Copy {img_path} failed\n'
        QMessageBox.information(self, info_str['title'], info_str['text'])

    def actionGoToTriggered(self, by_name=False):
        text = 'Name' if by_name else 'Index'
        dialog = Dialog(title='GoTo', text=text)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            input_text = dialog.get_input_text()
            print("Input Text:", input_text)
            index = fuzzySearchList(input_text, self.imageFilenames) if by_name else int(input_text)
            self.currentIndex = index
            self.update()