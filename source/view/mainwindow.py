#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore
from ui_mainwindow import Ui_MainWindow

class MyMainwindow(QtGui.QMainWindow, Ui_MainWindow):

    quit = QtCore.Signal()

    def __init__(self, **kwds):
        super(MyMainwindow, self).__init__(**kwds)
        self.setupUi(self)

    def closeEvent(self, event):
        event.ignore()
        self.quit.emit()
        

