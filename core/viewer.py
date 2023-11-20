import os
import math
from PyQt5.QtWidgets import (QMainWindow, QDialog, QMessageBox, QDesktopWidget)
from PyQt5.QtCore import QPoint

from ui import MainWindowUI
from utils.file import fuzzySearchList
from utils.check import checkOverflow
from config import SSH_CONFIG, windowConfig
from .dialogs import Dialog
from .media import QmediaObjHandler
from .files import fileHandler
from .remote import SSHConnection
from .events import EventHandler

class ViewerApp(QMainWindow, MainWindowUI):
    def __init__(self):
        super(ViewerApp, self).__init__()
        # for debug
        import cProfile
        self.profiler = cProfile.Profile()

        # files
        self.file_handler = fileHandler(self)
        self.media_handler = QmediaObjHandler()
        # defind func to fit remote or local features
        self.ssh_connector = None

        # UI window
        self.view_adjusted = False
        self.setWindow(self)
        self.mousePressed = False
        self.lastMousePos = QPoint()
        self.setupUi(self)
        self.bindEvent()

    def set_ssh_connector(self, client):
        self.ssh_connector = client
        setattr(self.media_handler, 'load_func', dict(img=client.get_remote_file_content, vide=client.get_remote_file_content))
        setattr(self.media_handler, 'check_path_func', any) # TODO: path in remote not checked now

    @property
    def imageFilenames(self):
        return self.file_handler.imageFilenames
    
    @property
    def folderPaths(self):
        return self.file_handler.folderPaths
    
    @property
    def graphicsViews(self):
        return self.file_handler.graphicsViews
    
    @property
    def currentIndex(self):
        return self.file_handler.currentIndex
    
    @currentIndex.setter
    def currentIndex(self, value):
        '''currentIndex.setter func
        When self.currentIndex is set (arbitrary 'self.currentIndex=' clause), 
            this func will be called automatically with param value as the set value.
        This feature is based on self.currentIndex is decorated as a property key.
        '''
        setattr(self.file_handler, 'currentIndex', value)
        max_image_idx = len(self.imageFilenames) - 1
        if self.currentIndex < 0:
            QMessageBox.information(self, 'Info', 'The beginning of the images! Skip to the tail...')
            setattr(self.file_handler, 'currentIndex', max_image_idx)
        elif self.currentIndex > max_image_idx:
            QMessageBox.information(self, 'Info', 'The end of the images! Skip to the start...')
            setattr(self.file_handler, 'currentIndex', 0)
    
    @property
    def titles(self):
        return self.file_handler.titles

    def bindEvent(self):
        # file
        self.actionLoadSubFolders.triggered.connect(self.file_handler.loadAllSubFolders)
        self.actionAdd1Folder.triggered.connect(self.file_handler.addFolder)
        self.actionDel1Folder.triggered.connect(lambda: self.file_handler.deleteFolder())
        self.actionSave.triggered.connect(self.file_handler.actionSaveTriggered)
        self.actionOpenRemote.triggered.connect(lambda: self.connectRemote('PAI-aliyun-A100'))

        self.actionGoTo.triggered.connect(self.actionGoToTriggered)
        self.actionGoToName.triggered.connect(lambda: self.actionGoToTriggered(by_name=True))

    def update(self):
        self.profiler.enable()
        # load_func = load_image if load_func is None else load_func
        filename = self.imageFilenames[self.currentIndex]
        for idx, (key, view) in enumerate(self.graphicsViews.items()):
            file_path = os.path.join(self.folderPaths[key], filename)
            qText = self.media_handler.get_title(self, file_path, key)

            # add media obj
            view.scene().clear() # scene clearing after qText created, avoid qText to be cleared
            self.media_handler.request(view, file_path)
            if not self.view_adjusted:
                self.adjustGraphicsView(idx, view, self.media_handler.width, self.media_handler.height)
            view.scene().addItem(qText)
            view.show()

        self.view_adjusted = True
        self.profiler.disable()
        # self.profiler.print_stats()

    def adjustGraphicsView(self, idx, view, media_w, media_h):
        border = windowConfig.BORDER
        x_margin, y_margin = windowConfig.MARGIN_W, windowConfig.MARGIN_H

        print(media_w + 2 * border, self.size().width())
        # total_len = len(self.folderPaths.keys())
        x_num = windowConfig.X_NUM

        size_w, size_h = windowConfig.WINDOW_SIZE_W, windowConfig.WINDOW_SIZE_H
        if size_w == 'auto':
            # 获取主屏幕
            # screen = QDesktopWidget().screenGeometry()
            # screen_w, screen_h = screen.width(), screen.height()
            screen_w, screen_h = self.size().width(), self.size().height()
            size_w = (screen_w - 2 * x_margin - border * (x_num - 1)) // x_num
            size_h = (media_h / media_w) * size_w
            y_num = math.ceil(len(self.folderPaths.keys()) / x_num)
            if y_num * size_h + border > screen_h:
                size_h = (screen_h - 2 * y_margin - border * (y_num - 1)) // y_num
                size_w = (media_w / media_h) * size_h
            windowConfig.WINDOW_SIZE_W, windowConfig.WINDOW_SIZE_H = size_w, size_h
        # print(size_w, size_h)
        
        x_crt = idx % (x_num)
        y_crt = idx // (x_num)
        x = x_margin + x_crt * (size_w + border)
        y = y_margin + y_crt * (size_h + border)
        view.setGeometry(x, y, size_w, size_h)
        # print('view pos', x, y, size_w, size_h)

    def keyPressEvent(self, event):
        EventHandler.keyPressedEvent(self, event)

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
        print('move', self.mousePressed)
        if self.mousePressed:
            # 计算鼠标移动距离
            dx = event.x() - self.lastMousePos.x()
            dy = event.y() - self.lastMousePos.y()
            self.lastMousePos = event.pos()

            # 更新图片位置 and titles
            for key in self.graphicsViews.keys():
                view = self.graphicsViews[key]
                h, v = view.horizontalScrollBar().value(), view.verticalScrollBar().value()
                if not checkOverflow(h - dx, 'int32') or not checkOverflow(v - dy, 'int32'):
                    print(f'Int32 overflow... could not scale to {h - dx}, {v - dy}')
                    return
                view.horizontalScrollBar().setValue(h - dx)
                view.verticalScrollBar().setValue(v - dy)
                title_item = self.titles[key]
                # 获取视图的左上角在场景中的坐标
                targetPos = view.mapToScene(0, 0)  # 视图左上角的场景坐标
                title_item.setPos(targetPos)  # 吸附到目标位置
    
    def resizeEvent(self, event):
        # 调用基类的 resizeEvent 方法
        super(ViewerApp, self).resizeEvent(event)
        windowConfig.WINDOW_SIZE_W = 'auto'
        self.view_adjusted = False

    def actionGoToTriggered(self, by_name=False):
        text = 'Name' if by_name else 'Index'
        dialog = Dialog(title='GoTo', text=text)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            input_text = dialog.get_input_text()
            print("Input Text:", input_text)
            index = fuzzySearchList(input_text, self.imageFilenames) if by_name else int(input_text)
            if index > len(self.imageFilenames) - 1 or index < 0:
                QMessageBox.Critical(f'Invalid Index {index}!')
                return 
            self.currentIndex = index
            self.update()

    def connectRemote(self, cfg_name):
        cfg = SSH_CONFIG[cfg_name]
        # try:
        client = SSHConnection(
            host = cfg['HostName'],
            user = cfg['User'],
            port = cfg['Port'],
            private_key_path=os.path.expanduser(cfg['PrivateKeyPath']))
        self.set_ssh_connector(client)
        # dialog = Dialog(title=f'Remote '+cfg['HostName'], text='paths(split by ;)')
        # result = dialog.exec_()
        # if result == QDialog.Accepted:
            # self.file_handler.initAll()
            # input_text = dialog.get_input_text()
            # path_list = input_text.split(';')
            # print(path_list)
        path_list = '/cpfs01/user/chenziyan/BFRxBenchmark/tmp/GFPGAN/experiments/train_GFPGANv3_video_v1_sliding_window/visualization/Clip+_HebIzK_LP4+P2+C1+F16589-16715/5000;/cpfs01/user/chenziyan/BFRxBenchmark/tmp/GFPGAN/experiments/train_GFPGANv3_video_v1_sliding_window/visualization/Clip+_HebIzK_LP4+P2+C1+F16589-16715/10000;/cpfs01/user/chenziyan/BFRxBenchmark/tmp/GFPGAN/experiments/train_GFPGANv3_video_v1_sliding_window/visualization/Clip+_HebIzK_LP4+P2+C1+F16589-16715/20000'.split(';')
        for path in path_list:
            # print(self.ssh_connector.getAllFiles(path))
            self.file_handler.loadFolder(
                path, 
                check_dir=any, # path not need to be checked for files are from ls clause
                scan_func=self.ssh_connector.getAllFiles)
        self.update()
        