import os
import math
from copy import deepcopy
from PyQt5.QtWidgets import (QMainWindow, QDialog, QMessageBox, QDesktopWidget)
from PyQt5.QtCore import QPoint

from ui import MainWindowUI
from utils.file import fuzzy_search_list
from config import windowConfig

from core.view import adjustGraphicsView
from core.dialogs import EditDialog, ListDialog
from core.media import QMediaObj, getQTitle
from core.files import fileHandler, load_file_bytes
from core.remote import get_all_hostnames, create_ssh_client
from core.events import EventHandler
from core.view import DynamicGridView


class ViewerApp(QMainWindow, MainWindowUI):
    def __init__(self):
        super(ViewerApp, self).__init__()
        # for time-consumption debug
        # import cProfile
        # self.profiler = cProfile.Profile()

        # files
        self.file_handler = None
        self.ssh_client = None
        # defind func to fit remote or local features
        self.initApp()

        # UI window
        self.setWindow(self)
        self.lastMousePos = QPoint()
        self.setupUi(self)
        self.bindEvent()

    def initApp(self, keep_ssh=False):
        if not keep_ssh and self.ssh_client is not None:
            del self.ssh_client # # call __del__ func of ssh_client
            self.ssh_client = None
        if self.file_handler is not None:
            del self.file_handler # call __del__ func of fileHandler

        self.setCentralWidget(None) # clear the whole window
        self.file_handler = fileHandler(self)
        self.view = DynamicGridView(self, self.file_handler)

        # self.windowCfg = deepcopy(windowConfig)
        self.view_adjusted = False
        self.mousePressed = False

    @property
    def imageFilenames(self):
        return self.file_handler.imageFilenames
    
    @property
    def folderPaths(self):
        return self.file_handler.folderPaths
    
    @property
    def graphicsViews(self):
        return self.view.graphicsViews
    
    @property
    def currentIndex(self):
        return self.view.currentIndex
    
    @currentIndex.setter
    def currentIndex(self, value):
        '''currentIndex.setter func
        When self.currentIndex is set (arbitrary 'self.currentIndex=' clause), 
            this func will be called automatically with param value as the set value.
        This feature is based on self.currentIndex is decorated as a property key.
        '''
        setattr(self.view, 'currentIndex', value)
        max_image_idx = len(self.imageFilenames) - 1
        if self.currentIndex < 0:
            QMessageBox.information(self, 'Info', 'You\'re in the beginning of the directory! Skip to the tail...')
            setattr(self.view, 'currentIndex', max_image_idx)
        elif self.currentIndex > max_image_idx:
            QMessageBox.information(self, 'Info', 'You\'re in the end of the directory! Skip to the start...')
            setattr(self.view, 'currentIndex', 0)
    
    @property
    def titles(self):
        return self.file_handler.titles

    def bindEvent(self):
        # file
        self.actionLoadSubFolders.triggered.connect(self.loadAllSubFolders)
        # need to use key lambda when call func from prop even though no param passed
        self.actionAdd1Folder.triggered.connect(lambda: self.addFolder())
        # TODO: del assigned dir
        self.actionDel1Folder.triggered.connect(lambda: self.view.delete())
        self.actionSave.triggered.connect(lambda: self.view.save())
        # self.actionSave.triggered.connect(self.save)
        # TODO: log in assigned host
        self.actionOpenRemote.triggered.connect(lambda: self.connectRemote())

        self.actionGoTo.triggered.connect(self.actionGoToTriggered)
        self.actionGoToName.triggered.connect(lambda: self.actionGoToTriggered(by_name=True))
        

    def update(self):
        if self.currentIndex == -1:
            print('No media loaded')
            return 
        # self.profiler.enable()
        for idx, (key, view) in enumerate(self.graphicsViews.items()):
            paths = self.folderPaths[key].split(os.sep)
            
            # add media obj
            fpath, file_bytes = load_file_bytes(self, paths, key)
            # print(file_bytes, fpath, fpath_local, relative_fdir)
            qTitle = getQTitle(self, fpath, key)
            qMedia = QMediaObj(fpath, bytes=file_bytes, fdir='', view=view)

            qMedia.show_in_view(qTitle)
            if not self.view_adjusted: adjustGraphicsView(self, idx, qMedia.width, qMedia.height)

        self.view_adjusted = True
        # self.profiler.disable()
        # self.profiler.print_stats()

    def loadAllSubFolders(self):
        self.initApp() # init app window
        folders = self.file_handler.getAllSubFolders()
        # folders = ['/Users/celine/Desktop/VideoLM/exps/codeformer/comp/val_out', 
        #            '/Users/celine/Desktop/VideoLM/exps/codeformer/comp/visualization/90000',
        #            '/Users/celine/Desktop/VideoLM/exps/codeformer/comp/visualization/20000'
        #            ]
        for folder in folders:
            self.addFolder(folder, update=False)
        self.update()

    def addFolder(self, folder=None, update=True, **kargs):
        # folder = '/Users/celine/Desktop/VideoLM/exps/codeformer/0520/1'
        file_num, base_key = self.file_handler.addFolder(folder, **kargs)
        print('file_num', file_num, 'base_key', base_key, file_num)
       
        if file_num > 0:
            self.view.add(base_key)
            self.currentIndex = 0  # return to page 0 everytime new folder loaded
            if update:
                self.update()
        else:
            if file_num < 0:
                error_str = f'Folder {folder} already loaded'
                QMessageBox.critical(self, "Folder Error", error_str)
    
    def loadSSHFolders(self):
        dialog = EditDialog(title=f'Remote '+self.ssh_client.host, label='paths(split by ;)', edit='text')
        result = dialog.exec_()
        if result == QDialog.Accepted:
            input_text = dialog.get_input_text()
            path_list = [p.strip() for p in input_text.split(';')] #parse path string
            self.initApp(keep_ssh=True) # init app window
            # self.file_handler.loadFromRemote(path_list, self.ssh_client)
            for path in path_list:
            # print(self.ssh_connector.getAllFiles(path))
                self.addFolder(path, update=False, check_dir=any, scan_func=self.ssh_client.getAllFiles)
        self.update()

    def connectRemote(self):
        dialog = ListDialog(get_all_hostnames(), title='Select Host')
        if dialog.exec_() == QDialog.Accepted:
            selected_host = dialog.get_selected_item()

            ssh_flag = True # avoid false from loading files
            try:
                self.ssh_client = create_ssh_client(selected_host)
            except Exception as e:
                print(e)
                ssh_flag = False
                # QMessageBox.critical(self, "SSH Connection Error", f'Could not connect to {cfg["HostName"]}!')
                QMessageBox.critical(self, "SSH Error", f'{e}!')

            if ssh_flag:
                # print(self.ssh_client)
                self.loadSSHFolders()

    def keyPressEvent(self, event):
        EventHandler.keyPressedEvent(self, event)

    def wheelEvent(self, event):
        EventHandler.wheelEvent(self, event)

    def mousePressEvent(self, event):
        self.mousePressed = True
        self.lastMousePos = event.pos()

    def mouseReleaseEvent(self, event):
        self.mousePressed = False

    def mouseMoveEvent(self, event) -> None:
        EventHandler.mouseMoveEvent(self, event)
    
    def resizeEvent(self, event):
        # super(ViewerApp, self).resizeEvent(event)
        # self.windowCfg.X_NUM = windowConfig.X_NUM # reset x_num
        windowConfig.X_NUM = 'auto' if self.view_adjusted else windowConfig.X_NUM
        # readjust view grid when the app window resized
        self.view_adjusted = False
        self.update()

    def actionGoToTriggered(self, by_name=False):
        label = 'Name' if by_name else 'Index'
        dialog = EditDialog(title='GoTo', label=label)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            input_text = dialog.get_input_text()
            # print("Input Text:", input_text)
            if label == 'Name':
                index = fuzzy_search_list(input_text, self.imageFilenames)
                if index == -1:
                    QMessageBox.critical(self, "Name Not found", f'No filename includes \'{input_text}\'!')
                    return
            else:
                index = int(input_text)
                #TODO: check int
                if index > len(self.imageFilenames) - 1 or index < 0:
                    QMessageBox.critical(f'Invalid Index {index}!')
                    return 
            self.currentIndex = index
            self.update()
        
        