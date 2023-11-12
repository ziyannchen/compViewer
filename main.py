import sys
from PyQt5.QtWidgets import QApplication

from core.viewer import ViewerApp

def main():
    app = QApplication(sys.argv)
    ex = ViewerApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()