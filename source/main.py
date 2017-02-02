#!/usr/bin/env python
# -*- coding: utf-8 -*-



import sys
import logging.config
logging.config.fileConfig('logging_asterix.conf')

from PySide import QtGui

from view.mainwindow import MyMainwindow
from view.mapwidget import Map
from presenter.presenter import MyPresenter
from model.model import MyModel


if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)

    mainwindow = MyMainwindow()
    mapwindow = Map()

    model = MyModel()
    presenter = MyPresenter(model, mainwindow, mapwindow)

    mainwindow.show()
    mapwindow.show()

    sys.exit(app.exec_())



