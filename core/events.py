from PyQt5.QtCore import Qt

from utils.check import checkOverflow

class EventHandler:
    @staticmethod
    def keyPressedEvent(main_window, event) -> None:
        k = event.key()
        # print('pressed', k)
        if k == Qt.Key_A or k == Qt.Key_W:
            main_window.currentIndex -= 1
        elif k == Qt.Key_Space or k == Qt.Key_S or k == Qt.Key_D:
            main_window.currentIndex += 1
        elif k == Qt.Key_P:
            # for video player
            pass
        main_window.update()

    @staticmethod
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
                if not checkOverflow(h - dx, 'int32') or not checkOverflow(v - dy, 'int32'):
                    print(f'Int32 overflow... could not scale to {h - dx}, {v - dy}')
                    return
                view.horizontalScrollBar().setValue(h - dx)
                view.verticalScrollBar().setValue(v - dy)
                title_item = self.titles[key]
                # 获取视图的左上角在场景中的坐标
                targetPos = view.mapToScene(0, 0)  # 视图左上角的场景坐标
                title_item.setPos(targetPos)  # 吸附到目标位置


    @staticmethod
    def wheelEvent(self, event) -> None:
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