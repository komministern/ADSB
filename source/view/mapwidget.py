#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

#import copy
import time
from mpl_toolkits.basemap import Basemap
#import matplotlib.pyplot as plt

import numpy as np

#import cPickle as pickle

class Map(QtGui.QWidget):

    quit = QtCore.Signal()

    def __init__(self, parent=None):

        super(Map, self).__init__(parent)
        
        self.adsb_dict = {}

        self.setupUI()

        
    def setupUI(self):  

        self.xlim0 = 1000000.0
        self.ylim0 = 1000000.0

        self.present_xlim = (0.0, self.xlim0)
        self.present_ylim = (0.0, self.ylim0)

        self.lon_0=12.86673
        self.lat_0=56.73105

        self.lon=self.lon_0
        self.lat=self.lat_0
        
        
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)

        self.layout = QtGui.QVBoxLayout(self)
        #self.mpl_toolbar = NavigationToolbar(self.canvas, self, coordinates = False)
        self.layout.addWidget(self.canvas)
        #self.layout.addWidget(self.mpl_toolbar)


        # Set up window to be a square programatically here!!!!!


        self.canvas.mpl_connect('button_press_event', self._on_press)
        self.canvas.mpl_connect('scroll_event', self._on_scroll)

        self.axes = self.fig.add_axes([0.,0.,1.,1.])

        self.setLayout(self.layout)

        self.m = Basemap(width=self.xlim0,height=self.ylim0,
            resolution='i',projection='cass',lon_0=self.lon_0,lat_0=self.lat_0, ax=self.axes)

        self.draw()

    def _on_press(self, event):
        #print event

        if event.button == 3:

            self.present_xlim = (0.0, self.xlim0)
            self.present_ylim = (0.0, self.ylim0)

        elif event.button == 1:

            x0, x1 = self.axes.get_xlim()
            y0, y1 = self.axes.get_ylim()

            delta_x = x1 - x0
            delta_y = y1 - y0
            
            new_centre_x = event.xdata
            new_centre_y = event.ydata

            new_x0, new_x1 = new_centre_x - delta_x / 2, new_centre_x + delta_x / 2
            new_y0, new_y1 = new_centre_y - delta_y / 2, new_centre_y + delta_y / 2

            if new_x0 < 0.0:
                new_x0, new_x1 = 0.0, new_x1 - new_x0
            if new_x1 > self.xlim0:
                new_x0, new_x1 = new_x0 - (new_x1 - self.xlim0), self.xlim0

            if new_y0 < 0.0:
                new_y0, new_y1 = 0.0, new_y1 - new_y0
            if new_y1 > self.ylim0:
                new_y0, new_y1 = new_y0 - (new_y1 - self.ylim0), self.ylim0

            self.present_xlim = (new_x0, new_x1)
            self.present_ylim = (new_y0, new_y1)

        self.draw()


    def _on_scroll(self, event):

        if event.button == 'up':

            x0, x1 = self.axes.get_xlim()
            y0, y1 = self.axes.get_ylim()

            delta_x = x1 - x0
            delta_y = y1 - y0

            self.present_xlim = (x0 + delta_x * 0.1, x1 - delta_x * 0.1)
            self.present_ylim = (y0 + delta_y * 0.1, y1 - delta_y * 0.1)

            self.draw()

        elif event.button == 'down':

            x0, x1 = self.axes.get_xlim()
            y0, y1 = self.axes.get_ylim()


            if (x0, x1) != (0.0, self.xlim0) or (y0, y1) != (0.0, self.ylim0):


                delta_x = x1 - x0
                delta_y = y1 - y0

                new_x0, new_x1 = x0 - delta_x * 0.1, x1 + delta_x * 0.1
                new_y0, new_y1 = y0 - delta_y * 0.1, y1 + delta_y * 0.1

                if new_x0 < 0.0:
                    if new_x1 - new_x0 < self.xlim0:
                        new_x1 = new_x1 - new_x0
                        new_x0 = 0.0
                    else:
                        new_x1 = self.xlim0
                        new_x0 = 0.0

                if new_x1 > self.xlim0:
                    if new_x0 - (new_x1 - self.xlim0) < 0.0:
                        new_x0 = 0.0
                        new_x1 = self.xlim0
                    else:
                        new_x0 = new_x0 - (new_x1 - self.xlim0)
                        new_x1 = self.xlim0

                if new_y0 < 0.0:
                    if new_y1 - new_y0 < self.ylim0:
                        new_y1 = new_y1 - new_y0
                        new_y0 = 0.0
                    else:
                        new_y1 = self.ylim0
                        new_y0 = 0.0

                if new_y1 > self.ylim0:
                    if new_y0 - (new_y1 - self.ylim0) < 0.0:
                        new_y0 = 0.0
                        new_y1 = self.ylim0
                    else:
                        new_y0 = new_y0 - (new_y1 - self.ylim0)
                        new_y1 = self.ylim0

                self.present_xlim = (new_x0, new_x1)
                self.present_ylim = (new_y0, new_y1)

                self.draw()







    def update_adsb_plots(self, adsb_dict):
        self.adsb_dict = adsb_dict
        #self.draw()

    def draw(self):

        plotlist = self.adsb_dict
        #plotlist = {}

        self.axes.cla()
       
        self.m.drawcoastlines()
        self.m.fillcontinents(color='coral',lake_color='aqua',zorder=0)
        
        # draw parallels and meridians. ------------ Minska ner på detta!!!!!!!!!
        self.m.drawparallels(np.arange(-40.,80.,2.))
        self.m.drawmeridians(np.arange(-20.,40.,2.))
        self.m.drawmapboundary(fill_color='aqua')
        


        for icao, plot in plotlist.items():

            alt, lon, lat, callsign, latest_update = plot

            x, y = self.m(lon,lat)

            if time.time() - latest_update > 30.0:
                col = 'r'
            else:
                col = 'k'

            x0, x1 = self.present_xlim
            y0, y1 = self.present_ylim

            if (x > x0) and (x < x1) and (y > y0) and (y < y1):

                self.axes.text(x,y,'  ' + callsign +'\n  ' + str(alt), fontsize=12,fontweight='regular',
                    ha='left',va='top',color=col)

                self.m.scatter(x,y,s=100,marker='+',color='k', ax=self.axes)



        x0, x1 = self.present_xlim
        y0, y1 = self.present_ylim

        self.axes.set_xlim(x0, x1)
        self.axes.set_ylim(y0, y1)


        self.canvas.draw()





    def closeEvent(self, event):
        event.ignore()
        self.quit.emit()


