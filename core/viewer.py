import os
import math
from copy import deepcopy
from PyQt5.QtWidgets import (QMainWindow, QDialog, QMessageBox, QDesktopWidget, QWidget, QVBoxLayout)
from PyQt5.QtCore import QPoint

from ui import MainWindowUI
from utils.file import fuzzy_search_list
from config import windowConfig

from core.view import adjustGraphicsView
from core.dialogs import EditDialog, ListDialog, EditableListDialog
from core.media import QMediaObj, getQTitle
from core.files import fileHandler
from core.remote import get_all_hostnames, create_ssh_client
from core.events import EventHandler
from core.view import DynamicGridView


class ViewerApp(QMainWindow, MainWindowUI, EventHandler):
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
        self.actionSaveCrop.triggered.connect(lambda: self.view.save(scaled=True))
        # self.actionSave.triggered.connect(self.save)
        self.actionOpenRemote.triggered.connect(lambda: self.connectRemote())

        # config
        self.actionConfigWindow.triggered.connect(self.configWindow)

        # action
        self.actionGoTo.triggered.connect(self.actionGoToTriggered)
        self.actionGoToName.triggered.connect(lambda: self.actionGoToTriggered(by_name=True))
        
    def update(self):
        if self.currentIndex == -1:
            print('No media loaded')
            return 
        print('Updating...')
        # self.profiler.enable()
        # TODO: optimize this, this is added for video(mp4) playing.
        # QGraphicsVideoItem+QMediaPlayer cannot dispalyed in QGraphicsView without QWidget in the QMainwindow
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        for idx, (key, view) in enumerate(self.graphicsViews.items()):
            # add media obj
            fpath, file_bytes = self.file_handler.loadFileBytes(key)
            
            # print(fpath)
            qTitle = getQTitle(self, fpath, key)
            qMedia = QMediaObj(fpath, bytes=file_bytes, fdir='', view=view)
            layout.addWidget(qMedia)

            qMedia.show_in_view(qTitle)
            if not self.view_adjusted: adjustGraphicsView(self, idx, qMedia.width, qMedia.height)

        self.view_adjusted = True
        # self.profiler.disable()
        # self.profiler.print_stats()

    def loadAllSubFolders(self):
        self.initApp() # init app window
        folders = self.file_handler.getAllSubFolders()
        for folder in folders:
            self.addFolder(folder, update=False)
        self.update()

    def addFolder(self, folder=None, update=True, **kargs):
        folder = '/Users/celine/Desktop/VideoLM/test_samples/pexels'
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

    def actionGoToTriggered(self, by_name=False):
        label = 'Name' if by_name else 'Index'
        dialog = EditDialog(title='GoTo', label=label)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            input_text = dialog.get_input_text()
            if input_text == '':
                return 
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

    def configWindow(self):
        dialog = EditableListDialog(windowConfig)
        print(windowConfig)
        if dialog.exec_() == QDialog.Accepted:
            edited_values = dialog.get_edited_values()
            windowConfig.set(edited_values)
            self.view_adjusted = False
            print("Edited Values:", edited_values, windowConfig)
            self.update()

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
        super(ViewerApp, self).resizeEvent(event)
        windowConfig.X_NUM = windowConfig.X_NUM # reset x_num
        # windowConfig.X_NUM = 'auto'
        # readjust view grid when the app window resized
        self.view_adjusted = False
        self.update()
        
        