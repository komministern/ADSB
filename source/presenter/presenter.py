#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log = logging.getLogger('presenter')

from PySide import QtCore, QtGui

class MyPresenter(QtCore.QObject):

    startsignal = QtCore.Signal(tuple)
    stopsignal = QtCore.Signal()

    def __init__(self, model, mainwindow, mapwindow, **kwds):
	super(MyPresenter, self).__init__(**kwds)

        # Store view and model.
        self._model = model
        self._mainview = mainwindow
        self._mapview = mapwindow

        # Setup all signals.
        self.connect_signals()


        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update)
        self.timer.start(1000)



    def update(self):
        
        self.mapview.draw()
        #print '.................... timer is working'


    # PROPERTIES

    @property
    def model(self):
	return self._model

    @property
    def mainview(self):
	return self._mainview

    @property
    def mapview(self):
	return self._mapview




    # METHODS

    def start(self):
        inputs = []

        if self.mainview.radioButton_Input_Mc.isChecked():
            inputs.append( ('udpMulticast', (self.mainview.lineEdit_Input_McAddress.text(), 
                self.mainview.lineEdit_Input_McPort.text())) )
        elif self.mainview.radioButton_Input_Uc.isChecked():
            inputs.append( ('udpUnicast', (self.mainview.lineEdit_Input_UcAddress.text(), self.mainview.lineEdit_Input_UcPort.text()) ) )
        elif self.mainview.radioButton_Input_Tcp.isChecked():
            inputs.append( ('tcpUnicast', (self.mainview.lineEdit_Input_TcpAddress.text(), self.mainview.lineEdit_Input_TcpPort.text()) ) ) 
        elif self.mainview.radioButton_Input_File.isChecked():
            inputs.append( ('file', self.mainview.lineEdit_Input_File.text()) )

        outputs = []

        if self.mainview.checkBox_Output_Udp1.isChecked():
            outputs.append( ('udp', (self.mainview.lineEdit_Output_Udp1Address.text(), 
                self.mainview.lineEdit_Output_Udp1Port.text())) )
        if self.mainview.checkBox_Output_Udp2.isChecked():
            outputs.append( ('udp', (self.mainview.lineEdit_Output_Udp2Address.text(), 
                self.mainview.lineEdit_Output_Udp2Port.text())) )
        if self.mainview.checkBox_Output_Udp3.isChecked():
            outputs.append( ('udp', (self.mainview.lineEdit_Output_Udp3Address.text(), 
                self.mainview.lineEdit_Output_Udp3Port.text())) )
        if self.mainview.checkBox_Output_File.isChecked():
            outputs.append( ('file', self.mainview.lineEdit_Output_File.text()) )
        if self.mainview.checkBox_Output_Mapview.isChecked():
            outputs.append( ('mapview', '') )
        
        t = (inputs, outputs)

        self.startsignal.emit(t)


    def stop(self):
        self.stopsignal.emit()


    def get_input_file(self):

        inputFileName, _ = QtGui.QFileDialog.getOpenFileName(self.mainview,
                unicode('Replay File'),
                unicode('~'),
                unicode("All Files (*.*);;Text Files (*.txt)") )

        if inputFileName != '':
            self.mainview.lineEdit_Input_File.setText(inputFileName)

        #print inputFileName

    def get_output_file(self):

        outputFileName, _ = QtGui.QFileDialog.getOpenFileName(self.mainview,
                unicode('Replay File'),
                unicode('~'),
                unicode("All Files (*.*);;Text Files (*.txt)") )

        if outputFileName != '':
            self.mainview.lineEdit_Output_File.setText(outputFileName)

        #print outputFileName


    





    # SIGNALS

    def connect_signals(self):

        self.mainview.quit.connect(self.model.quit)
        self.mainview.pushButton_Quit.pressed.connect(self.model.quit)
        self.mapview.quit.connect(self.model.quit)

        self.mainview.pushButton_Draw.pressed.connect(self.mapview.draw)

        self.mainview.pushButton_Input_File.pressed.connect(self.get_input_file)
        self.mainview.pushButton_Output_File.pressed.connect(self.get_output_file)

        self.mainview.pushButton_Start.pressed.connect(self.start)
        self.mainview.pushButton_Stop.pressed.connect(self.stop)

        self.startsignal.connect(self.model.start)
        self.stopsignal.connect(self.model.stop)

        self.model.update_adsb.connect(self.mapview.update_adsb_plots)

