# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class BaseUI(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1378, 701)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1378, 24))
        self.menubar.setObjectName("menubar")
        self.menuFolder = QtWidgets.QMenu(self.menubar)
        self.menuFolder.setObjectName("menuFolder")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoadSubFolders = QtWidgets.QAction(MainWindow)
        self.actionLoadSubFolders.setObjectName("actionLoadSubFolders")
        self.actionAdd1Folder = QtWidgets.QAction(MainWindow)
        self.actionAdd1Folder.setObjectName("actionAdd1Folder")
        self.actionDel1Folder = QtWidgets.QAction(MainWindow)
        self.actionDel1Folder.setObjectName("actionDel1Folder")
        self.menuFolder.addAction(self.actionLoadSubFolders)
        self.menuFolder.addAction(self.actionAdd1Folder)
        self.menuFolder.addAction(self.actionDel1Folder)
        self.menubar.addAction(self.menuFolder.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFolder.setTitle(_translate("MainWindow", "Folder"))
        self.actionLoadSubFolders.setText(_translate("MainWindow", "Load All SubFolders"))
        self.actionAdd1Folder.setText(_translate("MainWindow", "+ Add 1Folder"))
        self.actionDel1Folder.setText(_translate("MainWindow", "- Del 1Folder"))
