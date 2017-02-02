#!/usr/bin/env python

import os

os.system('pyside-uic mainwindow.ui -o ui_mainwindow.py')
os.system('cp ui_mainwindow.py ../source/view/.')

