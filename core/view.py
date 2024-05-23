import math
from PyQt5 import QtGui
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QDialog
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from config import windowConfig

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

def adjustGraphicsView(self, idx, media_w, media_h):
    '''Adjust QGraphicsView geometry in the main window to build media view grids.
    Args:
        idx: specify the index of the graphicsViews list. 
            used to 1) calculate the position of the view in the main window, and 2) set view geometry.
        media_w: media width in the scene.
        media_h: media height in the scene.
    TODO: the computation of x_num, vsize need to be optimized.
    '''
    # assert media_h and media_w, 'media size should not be zero nor None'
    if windowConfig.DEBUG:
        print('Adjusting view... Media size (w, h)', media_w, media_h)
    if not media_w or not media_h:
        return

    border = windowConfig.BORDER
    x_margin, y_margin = windowConfig.MARGIN_W, windowConfig.MARGIN_H
    screen_w, screen_h = self.size().width(), self.size().height() # app window size
    vsize_w, vsize_h = media_w, media_h # view size, default to media size
    # 获取主屏幕长宽
    # screen = QDesktopWidget().screenGeometry()
    # screen_w, screen_h = screen.width(), screen.height()
    x_num = windowConfig.X_NUM
    media_num = len(self.folderPaths.keys())
    print(media_num)
    if x_num == 'auto':
        # 预设的media面积远大于屏幕面积，需要调整view的缩放比例
        v_scale = max(1, media_num*media_h*media_w // (screen_w*screen_h) - 1)
        vsize_w /= v_scale; vsize_h /= v_scale
        windowConfig.X_NUM = x_num = max(1, (screen_w - 2 * x_margin) // (vsize_w + border))
        # print(x_num, 'screen w', screen_w, 'vsize_w', vsize_w + border)
    y_num = math.ceil(media_num / x_num)

    # readjust unsuitable view size to fit the app screen window
    if x_num * vsize_w + border > screen_w:
        vsize_w = (screen_w - 2 * x_margin - border * (x_num - 1)) // x_num
        vsize_h = (media_h / media_w) * vsize_w # keep the aspect ratio
    if y_num * vsize_h + border > screen_h:
        vsize_h = (screen_h - 2 * y_margin - border * (y_num - 1)) // y_num
        vsize_w = (media_w / media_h) * vsize_h # keep the aspect ratio
    # print('vsize_w adjusted', vsize_w, 'vsize_h adjusted', vsize_h)
    
    x_crt = idx % (x_num)
    y_crt = idx // (x_num)
    x = x_margin + x_crt * (vsize_w + border)
    y = y_margin + y_crt * (vsize_h + border)
    list(self.graphicsViews.values())[idx].setGeometry(x, y, vsize_w, vsize_h)

    if windowConfig.DEBUG:
        print('view pos', x, y, vsize_w, vsize_h)

class DynamicGridView:
    def __init__(self, main_widget, file_handler):
        self.main_window = main_widget
        self.file_handler = file_handler
        self.initAll()

    def initAll(self):
        self.graphicsViews = {}
        self.currentIndex = -1  # current page index
    
    def add(self, base_key):
        # view = SyncedGraphicsView(self)
        view = QGraphicsView(self.main_window)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
        scene = QGraphicsScene(self.main_window)
        view.setScene(scene)
        # print('view and scene created')
        self.graphicsViews[base_key] = view

    def save(self):
        if self.currentIndex == -1:
            print('No data to save!')
            return 
        save_folder = QFileDialog.getExistingDirectory(self.main_window, "Select Folder")
        # save_folder = '/Users/celine/Desktop/DiffBIR/head figure/BSR_crop'
        # print('save_folder', save_folder)
        if save_folder:
            self.save_dir = save_folder
            save_folder = QDir.toNativeSeparators(save_folder)
            self.file_handler.saveImageGroup(self.graphicsViews, self.currentIndex, save_folder)

    def delete(self):
        base_key = self.file_handler.deleteFolder()
        if base_key is None:
            return
        # clear the view and scene
        # remove QGraphicsView frmo main window
        self.graphicsViews[base_key].setParent(None)
        del self.graphicsViews[base_key]

    def __del__(self):
        for key, view in self.graphicsViews.items():
            view.setParent(None)
            del view