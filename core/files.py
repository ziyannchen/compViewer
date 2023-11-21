import os
from natsort import natsorted

from PyQt5 import QtGui
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QDialog
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from utils.file import copyFile, scanDir
# ssh
from config import sshConfig
from .dialogs import Dialog

SUPPORTED_FILES = ('.png', '.jpg', '.jpeg', '.mp4')

class fileHandler:
    def __init__(self, main_window) -> None:
        self.main_window = main_window
        self.initAll()
        
    def initAll(self):
        self.folderPaths = {}
        self.graphicsViews = {}

        self.imageFilenames = None
        self.currentIndex = -1  # 当前显示的图片索引
        self.titles = {}
    
    def set_imageFilenames(self, value):
        if self.imageFilenames is None:
            self.imageFilenames = value
        else:
            self.imageFilenames = list(set((*value, *self.imageFilenames)))
        self.imageFilenames = natsorted(self.imageFilenames)
        # print(f'Total {len(self.imageFilenames)} files counted')

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
        # remove QGraphicsView frmo main window
        self.graphicsViews[base_key].setParent(None)
        del self.graphicsViews[base_key]
    
    def createGraphicsView(self, base_key):
        # view = SyncedGraphicsView(self)
        view = QGraphicsView(self.main_window)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
        scene = QGraphicsScene(self.main_window)
        view.setScene(scene)
        # print('view and scene created')
        self.graphicsViews[base_key] = view

    def loadFolder(self, folder, check_dir=os.path.isdir, scan_func=scanDir):
        if check_dir(folder):
            base_key = os.path.basename(folder)
            if base_key in self.folderPaths.keys():
                print(f'Folder {folder} already loaded')
                return
            self.folderPaths[base_key] = folder
            self.createGraphicsView(base_key)
            tmp_files = scan_func(folder=self.folderPaths[base_key], suffix=SUPPORTED_FILES, full_path=False)
            # print('tmp files', tmp_files)
            print(f'Folder {folder} loaded, {len(tmp_files)} files found')

            # in case of different file length in folders, collect all file names
            self.set_imageFilenames(tmp_files)
            self.currentIndex = 0 if len(self.imageFilenames) > 0 else -1

    def addFolder(self):
        folder = QFileDialog.getExistingDirectory(self.main_window, "Select Folder")
        # folder = '/Users/celine/Desktop/Benchmark/gfpgan/video_v1'
        self.loadFolder(folder)
        self.main_window.update()

    def loadAllSubFolders(self):
        # target = QFileDialog.getExistingDirectory(self.main_window, "Select Folder")
        # target = '/Users/celine/Desktop/Benchmark/test'
        target = '/Users/celine/Desktop/DiffBIR/data/LFW'
        if not target:
            return
        target = QDir.toNativeSeparators(target)
        dirs = natsorted(os.listdir(target))
        for d in dirs:
            if d.startswith('.'):
                continue
            folder = os.path.join(target, d)
            self.loadFolder(folder)
        self.main_window.update()
    
    def loadFromRemote(self, path_list, ssh_client):
        # path_list = '/cpfs01/user/chenziyan/BFRxBenchmark/tmp/GFPGAN/experiments/train_GFPGANv3_video_v1_sliding_window/visualization/Clip+_HebIzK_LP4+P2+C1+F16589-16715/5000;/cpfs01/user/chenziyan/BFRxBenchmark/tmp/GFPGAN/experiments/train_GFPGANv3_video_v1_sliding_window/visualization/Clip+_HebIzK_LP4+P2+C1+F16589-16715/10000;/cpfs01/user/chenziyan/BFRxBenchmark/tmp/GFPGAN/experiments/train_GFPGANv3_video_v1_sliding_window/visualization/Clip+_HebIzK_LP4+P2+C1+F16589-16715/20000'.split(';')
        for path in path_list:
            # print(self.ssh_connector.getAllFiles(path))
            self.loadFolder(
                path, 
                check_dir=any, # path not need to be checked for files are from ls clause
                scan_func=ssh_client.getAllFiles)
        self.main_window.update()
    
    def actionSaveTriggered(self):
        if self.currentIndex == -1:
            print('No data to save!')
            return 
        save_folder = QFileDialog.getExistingDirectory(self.main_window, "Select Folder")
        # save_folder = '/Users/celine/Desktop/DiffBIR/head figure/BSR_crop'
        print('save_folder', save_folder)
        if save_folder:
            self.save_dir = save_folder
            save_folder = QDir.toNativeSeparators(save_folder)
            self.saveImageGroup(save_folder)
    
    def saveImageGroup(self, save_dir, scale_view=False):
        imgname, ext = os.path.splitext(self.imageFilenames[self.currentIndex])
        save_dir = os.path.join(save_dir, f'{self.currentIndex}_{imgname}')
        os.makedirs(save_dir, exist_ok=True)
        
        info_str = {'title':'Info', 
                    'text': 'All imgaes are saved susccessfully'}
        for key, view in self.graphicsViews.items():
            img_path = os.path.join(self.folderPaths[key], imgname+ext)
            target_path = os.path.join(save_dir, f'{key}{ext}')
            if scale_view:
                captureView(view, remove_item=self.titles[key]).save(target_path)
                print('Saved ', target_path)
            else:
                if not copyFile(target_path, img_path):
                    print(f'Copy {img_path} failed')
                    info_str['title'] = 'Error'
                    info_str['text'] = f'Copy {img_path} failed\n'
        QMessageBox.information(self.main_window, info_str['title'], info_str['text'])

    def __del__(self):
        for key, view in self.graphicsViews.items():
            view.setParent(None)
            del view

def captureView(view, remove_item=None):
    if remove_item is not None:
        # temporarily remove the item from the view
        view.scene().removeItem(remove_item)
    # 获取视图的矩形区域
    view_rect = view.viewport().rect()

    # 创建一个空的QPixmap
    pixmap = QtGui.QPixmap(view_rect.size())
    pixmap.fill(Qt.transparent)

    # 使用QPainter将视图内容绘制到pixmap上
    painter = QtGui.QPainter(pixmap)
    view.render(painter, source=view_rect)
    painter.end()

    if remove_item is not None:
        # add the item back
        view.scene().addItem(remove_item)
    return pixmap