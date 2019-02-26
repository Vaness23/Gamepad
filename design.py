# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(500, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setGeometry(QtCore.QRect(10, 10, 481, 381))
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.listWidget = QtWidgets.QListWidget(self.splitter_2)
        self.listWidget.setAutoScroll(True)
        self.listWidget.setObjectName("listWidget")
        self.comboBox = QtWidgets.QComboBox(self.splitter_2)
        self.comboBox.setObjectName("comboBox")
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.disconnectBtn = QtWidgets.QPushButton(self.splitter)
        self.disconnectBtn.setObjectName("disconnectBtn")
        self.connectBtn = QtWidgets.QPushButton(self.splitter)
        self.connectBtn.setObjectName("connectBtn")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.disconnectBtn.setText(_translate("MainWindow", "Disconnect"))
        self.connectBtn.setText(_translate("MainWindow", "Connect"))


