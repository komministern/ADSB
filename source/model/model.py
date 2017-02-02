#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log = logging.getLogger('model')

from PySide import QtCore, QtGui, QtNetwork

import time
import json
from sets import Set
import adsbprocessor

mcast_addr = "239.255.43.21"
mcast_port = 45454

ACTIVE = 1
PASSIVE = 0

PRESENT = 1
PAST = 0

#class Multicast_Receiver(QtCore.QtObject):
#    def __init__(self):
        

class Udp_Multicast_Listener(QtCore.QObject):
    
    def __init__(self, mcast_address, mcast_port, action):
        super(Udp_Multicast_Listener, self).__init__()
        self.action = action
        self.groupAddress = QtNetwork.QHostAddress(mcast_address)        
        self.udpSocket = QtNetwork.QUdpSocket(self)
        self.udpSocket.bind(mcast_port, QtNetwork.QUdpSocket.DefaultForPlatform)
        self.udpSocket.joinMulticastGroup(self.groupAddress)
        self.udpSocket.readyRead.connect(self.processPendingDatagrams)

    def processPendingDatagrams(self): 
        while self.udpSocket.hasPendingDatagrams():
            datagram, host, port = self.udpSocket.readDatagram(self.udpSocket.pendingDatagramSize())
            self.action(datagram)
            # This does not seem right. Will not work if multiple listeners are active
            # without the use of semaphores and stuff. Hmmmm....

    def kill(self):
        self.udpSocket.leaveMulticastGroup(self.groupAddress)
        log.debug('Left multicast group')


class Udp_Unicast_Listener(QtCore.QObject):
    def __init__(self, ucast_port, action):
        super(Udp_Unicast_Listener, self).__init__()
        self.action = action
        self.udpSocket = QtNetwork.QUdpSocket(self)
        self.udpSocket.bind(ucast_port, QtNetwork.QUdpSocket.DefaultForPlatform)
        self.udpSocket.readyRead.connect(self.processPendingDatagrams)    

    def processPendingDatagrams(self): 
        while self.udpSocket.hasPendingDatagrams():
            datagram, host, port = self.udpSocket.readDatagram(self.udpSocket.pendingDatagramSize())
            self.action(datagram)
            # This does not seem right. Will not work if multiple listeners are active
            # without the use of semaphores and stuff. Hmmmm....

    def kill(self):
        pass


class Udp_Sender(QtCore.QObject):
    
    def __init__(self, address, port):
        super(Udp_Sender, self).__init__()
        self.udpSocket = QtNetwork.QUdpSocket(self)
        self.address = QtNetwork.QHostAddress(address)
        self.port = port

    def send(self, message):
        self.udpSocket.writeDatagram(message, self.address, self.port)



class Tcp_Unicast_Listener(QtCore.QObject):
    def __init__(self, address, port, action):
        super(Tcp_Unicast_Listener, self).__init__()
        self.action = action
        self.tcpSocket = QtNetwork.QTcpSocket(self)
        
        self.tcpSocket.readyRead.connect(self.read)
        self.tcpSocket.abort()
        self.tcpSocket.connectToHost(address, port)


    def read(self):
        
        i = QtCore.QDataStream(self.tcpSocket)
        i.setVersion(QtCore.QDataStream.Qt_4_0)
        
        n = self.tcpSocket.bytesAvailable()
        chunk = i.readRawData(n)

        self.action(chunk)

#        extracted_data = self.adsb.extract(chunk)
#        if extracted_data:
#            print extracted_data



#        while self.udpSocket.hasPendingDatagrams():
#            datagram, host, port = self.udpSocket.readDatagram(self.udpSocket.pendingDatagramSize())
#            self.action(datagram)
            # This does not seem right. Will not work if multiple listeners are active
            # without the use of semaphores and stuff. Hmmmm....

    def kill(self):
        pass




class MyModel(QtCore.QObject):

    update_adsb = QtCore.Signal(dict)

    def __init__(self):
        super(MyModel, self).__init__() 

        self.adsb = adsbprocessor.ADSB_Extractor()

        self.listeners = []
        self.senders = []
        self.output_files = []

        self._state = PASSIVE   # ACTIVE or PASSIVE
        self._tense = PRESENT   # PRESENT or PAST
        self._time = 0          # Will need some good format here. Same as used in ASTERIX prefered.

        self.plots = {}


    def stop(self):
        for each in self.listeners:
            each.kill()
        self.listeners = []
        log.debug('All listeners stopped')

        self.senders = []
        log.debug('All senders stopped')
        
        for each in self.output_files:
            each.close()

        self.output_files = []
        log.debug('Closed all output files')

        self.plots = {}

        #print 'stopped all listeners'

    def register_listener(self, alistener):
        self.listeners.append(alistener)
        log.debug('Registered a listener')

    def register_sender(self, asender):
        self.senders.append(asender)
        log.debug('Registered a sender')


    def getnewdata(self):
        d = json.load(self.input_file)
        self.processDatagram(d)


    def start(self, atuple):

        inputs, outputs = atuple

#        print 'starting input'

        failed = False

        input_type, input_args = inputs[0]

        if input_type == 'udpMulticast':
            mcast_address, mcast_port = input_args
            try:
                listener = Udp_Multicast_Listener(mcast_address, int(mcast_port), self.processDatagram)
                self.register_listener(listener) 
            except Exception:
                log.error('UDP Multicast listener failed when initializing')
                self.stop()
                failed = True

        elif input_type == 'udpUnicast':
            ucast_address, ucast_port = input_args
            try:
                listener = Udp_Unicast_Listener(ucast_address, int(ucast_port), self.processDatagram)
                self.register_listener(listener)
            except Exception:
                log.error('UDP Unicast listener failed when initializing')
                self.stop()
                failed = True

        elif input_type == 'tcpUnicast':
            tcp_address, tcp_port = input_args
            print input_args
            try:
                listener = Tcp_Unicast_Listener(tcp_address, int(tcp_port), self.processReceivedData)
                self.register_listener(listener)
            except Exception:
                log.error('TCP Unicast listener failed when initializing')
                self.stop()
                failed = True


        elif input_type == 'file':
            try:
                with open(input_args, 'r') as f:
                    file_data = f.read()

            except Exception:
                log.error('Could not open input file')
                self.stop()

            
            
        

            
#            self.timer = QtCore.QTimer(self)
#            self.timer.timeout.connect(self.getnewdata)
#            self.timer.start(500)




        else:
            log.critical('No input chosen - This should not be possible')
            
#        print 'starting output'

        #if not failed:

        for each in outputs:

            if not failed:

#                print 'choice'

                output_type, output_args = each
                if output_type == 'udp':
                    address, port = output_args
                    try:
                        sender = Udp_Sender(address, int(port))
                        self.register_sender(sender)
#                        print 'registered a sender'
                    except Exception:
                        log.error('Sender failed while initializing')
                        self.stop()
                        failed = True
                elif output_type == 'file': 
                    try:
                        output_file = open(output_args, 'w')
                        self.output_files.append(output_file)
                    except Exception:
                        log.error('Could not open writeable output file')
                        self.stop()
                elif output_type == 'mapview':
                    pass
                else:
                    log.critical('Unknown output type - This should not be possible')
        
#        print len(self.senders)


    def processReceivedData(self, data):

        #print 'anything'

        extracted_adsb_data = self.adsb.extract(data)

        if extracted_adsb_data:
            self.update_plots(extracted_adsb_data)
#            print extracted_adsb_data

#        for each in self.senders:
#            try:
#                each.send(str(datagram))
#            except Exception:
#                log.error('Sender failed while trying to send a datagram')
#                self.stop()

#        for each in self.output_files:
#            json.dump(str(datagram), each)
            #each.write(datagram)


    def update_plots(self, extracted_adsb):

        # self.plots is a dictionary with the ICAO number as key.
        # {icao: (alt, lon, lat, callsign, latest_update)}

        # Only the most recent information for each ICAO number is stored in self.plots

        present_time = time.time()

        for position in extracted_adsb['positions']:

            icao, new_alt, new_lon, new_lat = position

            if icao in Set( [key for key in self.plots] ):

                alt, lon, lat, callsign, latest_update = self.plots[icao]
                self.plots[icao] = (new_alt, new_lon, new_lat, callsign, present_time)

            else:

                self.plots[icao] = (new_alt, new_lon, new_lat, 'XXXXXX', present_time)



        for cs in extracted_adsb['callsigns']:

            icao, new_callsign = cs

            if icao in Set( [key for key in self.plots] ):

                alt, lon, lat, callsign, latest_update = self.plots[icao]

                if callsign == 'XXXXXX':

                    self.plots[icao] = (alt, lon, lat, new_callsign, present_time)

        # Remove all plots who hasnt been updated in 60 s.

        for icao, plot in self.plots.items():
            alt, lon, lat, callsign, latest_update = plot

            if present_time - latest_update > 60.0:
                del self.plots[icao]

       
        # Send signal with plot list to the view here. (?)

        self.update_adsb.emit(self.plots)



    def processDatagram(self, datagram):
        print 'Received: ' + datagram
#        for each in self.senders:
#            try:
#                each.send(str(datagram))
#            except Exception:
#                log.error('Sender failed while trying to send a datagram')
#                self.stop()

#        for each in self.output_files:
#            json.dump(str(datagram), each)
            #each.write(datagram)




    def quit(self):
        """ graceful exit here """
        self.stop()
        QtGui.QApplication.quit()

