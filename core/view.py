import math
import os
from copy import deepcopy
import imageio

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QFileDialog, QDialog, QMessageBox
from PyQt5.QtCore import QDir, Qt

from config import windowConfig
from utils.geometry import transform_gif

def captureView(view, img_path=None, save_path=None, remove_item=None):
    if remove_item is not None:
        view.scene().removeItem(remove_item)

    if save_path.endswith(windowConfig.SUPPORTED_FILES['image']):
        cropView(view).save(save_path)
    elif save_path.endswith('.gif'):
        cropGIF(view, img_path, save_path)
    else:
        QMessageBox.warning(None, 'Unsupported file format', f'Currently not support to crop {os.path.splitext(save_path)[-1]} file format')

    if remove_item is not None:
        view.scene().addItem(remove_item)

def cropGIF(view, gif_path, save_path):
    q_transform = view.transform()

    # Extract the matrix elements from QTransform
    sx, sy = q_transform.m11(), q_transform.m22()
    dx, dy = view.horizontalScrollBar().value(), view.verticalScrollBar().value()

    # 获取视图的可视区域
    viewport_rect = view.rect()
    width = viewport_rect.width() - 20
    height = viewport_rect.height() - 20
    transform_gif(gif_path, save_path, (width, height, dx, dy, sx, sy))

def cropView(view):
    view_rect = view.viewport().rect()

    # create QPixmap
    pixmap = QtGui.QPixmap(view_rect.size())
    pixmap.fill(Qt.transparent)

    # QPainter pixmap
    painter = QtGui.QPainter(pixmap)
    view.render(painter, source=view_rect)
    painter.end()
    return pixmap

def captureVideo(view, filename, duration=5, fps=10):
    pass
    # frames = []
    # num_frames = duration * fps

    # for i in range(num_frames):
    #     # Scale the view (example: gradually zoom in)
    #     # scale_factor = 1 + (i / num_frames)
    #     # view.resetTransform()
    #     # view.scale(scale_factor, scale_factor)
        
    #     # Capture the current view
    #     pixmap = captureView(view)
    #     image = pixmap.toImage()
    #     buffer = QtCore.QBuffer()
    #     buffer.open(QtCore.QBuffer.ReadWrite)
    #     image.save(buffer, 'PNG')
    #     # create numpy from byte stream
    #     frame = imageio.imread(buffer.data().data())
    #     frames.append(frame)
    
    # # Save as MP4
    # if filename.endswith('.mp4'):
    #     imageio.mimsave(filename, frames, fps=fps, codec='libx264')
    # # Save as GIF
    # elif filename.endswith('.gif'):
    #     imageio.mimsave(filename, frames, fps=fps)

def adjustGraphicsView(self, idx=-1, media_w=None, media_h=None):
    '''Adjust QGraphicsView geometry in the main window to build media view grids.
    Args:
        idx: specify the index of the graphicsViews list. 
            used to 1) calculate the position of the view in the main window, and 2) set view geometry.
        media_w: media width in the scene.
        media_h: media height in the scene.
    TODO: the computation of x_num, vsize need to be optimized.
    '''
    # assert media_h and media_w, 'media size should not be zero nor None'
    if not hasattr(windowConfig, 'media_w'.upper()):
        assert media_h and media_w, 'media size should not be zero nor None'
        print('Adjusting view... Media size (w, h)', media_w, media_h)
        windowConfig.__setattr__('media_w'.upper(), media_w)
        windowConfig.__setattr__('media_h'.upper(), media_h)

    if media_h is None:
        media_h = int(windowConfig.MEDIA_H)
        
    if media_w is None:
        media_w = int(windowConfig.MEDIA_W)

    border = int(windowConfig.BORDER)
    x_margin, y_margin = int(windowConfig.MARGIN_W), int(windowConfig.MARGIN_H)
    screen_w, screen_h = self.size().width(), self.size().height() # app window size
    vsize_w, vsize_h = media_w, media_h # view size, default to media size

    # 获取主屏幕长宽
    # screen = QDesktopWidget().screenGeometry()
    # screen_w, screen_h = screen.width(), screen.height()
    x_num = int(windowConfig.X_NUM)
    media_num = len(self.folderPaths.keys())
    # print(media_num)
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
    
    if idx == -1:
        # adjust all views
        for idx in range(media_num):
            adjustGraphicsView(self, idx, vsize_w, vsize_h)
        return
    
    x_crt = idx % (x_num)
    y_crt = idx // (x_num)
    x = x_margin + x_crt * (vsize_w + border)
    y = y_margin + y_crt * (vsize_h + border)
    list(self.graphicsViews.values())[idx].setGeometry(x, y, vsize_w, vsize_h)

    # print('view pos', x, y, vsize_w, vsize_h)

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
        view.resize(windowConfig.IMG_SIZE_W, windowConfig.IMG_SIZE_W)
        # print('view and scene created')
        self.graphicsViews[base_key] = view

    def save(self, scaled=False):
        if self.currentIndex == -1:
            print('No data to save!')
            return 
        save_folder = QFileDialog.getExistingDirectory(self.main_window, "Select Folder")
        if save_folder:
            self.save_dir = save_folder
            save_folder = QDir.toNativeSeparators(save_folder)
            self.file_handler.saveImageGroup(self.graphicsViews, self.currentIndex, save_folder, scale_view=scaled)

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