from PyQt5.QtCore import Qt

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