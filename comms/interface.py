#   Copyright 2009 Aaron Barnes
#
#   This file is part of the FreeEMS project.
#
#   FreeEMS software is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   FreeEMS software is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with any FreeEMS software.  If not, see <http://www.gnu.org/licenses/>.
#
#   We ask that if you make any changes to this file you send them upstream to us at admin@diyefi.org

import threading, wx, wx.lib.newevent

import libs.thread, protocols


sendEvent, EVT_SEND = wx.lib.newevent.NewEvent()
receiveEvent, EVT_RECEIVE = wx.lib.newevent.NewEvent()


class interface(libs.thread.thread):
    '''
    Base class for all comms plugin threads

    Serial thread overview:
    - Send queue, containing raw packets.

    - run() will check the receive buffer,
      send any receive buffer to the receive thread (after waking it),
      process any packets n the send queue (starting with oldest),
      it will then sleep for no more than 1/2 second unless woken by another thread
      attempting to send/receive/connect/disconnect,
      then loop again.

    - The thread must keep the connected flag up-to-date,
      as other threads will poll this continuously,
      and cant wait for the run() method to answer.

    - The thread starts in a blocked condition, waiting to receive a
      notify from a controller when its to be turned on
    '''

    # Send/receive threads
    _sendThread = None
    _receiveThread = None

    # Connected flag
    _connected = False

    # Connection wanted flag
    _connWanted = False

    # Disconnection wanted flag
    _disconnWanted = False

    # Watching methods
    _send_watchers = []
    _receive_watchers = []

    # Send queue
    _queue = []

    # Protocol module
    _protocol = None


    def __init__(self, name, controller):
        '''
        Sets up threading stuff
        '''
        name = 'comms.'+name
        self._setup(name, controller)


    def isConnected(self):
        '''
        Returns bool flag
        '''
        return self._connected


    def connect(self):
        '''
        Wakes up this thread and connects
        '''
        self._connWanted = True
        self.wake()


    def disconnect(self):
        '''
        Tells thread to disconnect comms
        '''
        self._disconnWanted = True
        self.wake()

    
    def getProtocol(self):
        '''
        Return (and load if necessary) protocol interface
        '''
        if self._protocol:
            return self._protocol

        self._protocol = protocols.getProtocol(self._controller)
        return self._protocol


    def send(self, packet):
        '''
        External interface for sending a packet,
        very high-level
        '''
        self._sendThread.send(packet)


    def queuePacket(self, packet):
        '''
        Adds a raw packet to the send queue
        To be called from send thread
        '''
        self._queue.append(packet)
        self.wake()
    
    
    def _receive(self, buffer):
        '''
        Sending a raw buffer to the receive thread
        '''
        self._receiveThread.received(buffer)

    
    def _createSendThread(self):
        '''
        Create comms send thread
        '''
        self._sendThread = self.getProtocol().getSendObject(self.name+'.send', self._controller, self)


    def _createReceiveThread(self):
        '''
        Create comms receive thread
        '''
        self._receiveThread = self.getProtocol().getReceiveObject(self.name+'.receive', self._controller, self)


    def _checkBlock(self):
        '''
        Overrides parent block function to use
        a smaller timeout

        Starts blocking using self._block
        The thread will remained blocked (halted)
        until another thread runs the wake() method
        '''
        if self._block == None:
            self._block = threading.Event()
        
        # Give this a short time out so we can gather
        # any incoming packets quickly
        self._block.wait(0.5) # 1/2 second
        self._block.clear()
    

    def exit(self):
        '''
        Disconnect and exit thread
        '''
        self.disconnect()
        libs.thread.thread.exit(self)


    def bindSendWatcher(self, watcher):
        '''
        Bind an action to be run when packets are sent
        '''
        self._send_watchers.append(watcher)


    def bindReceiveWatcher(self, watcher):
        '''
        Bind an action to be run when packets are received
        '''
        self._receive_watchers.append(watcher)


    def triggerSendWatchers(self, packet):
        '''
        Trigger actions bound to sent packets
        '''
        # Create event
        send_event = sendEvent(packet=packet)

        # Post the event
        for watcher in self._send_watchers:
            wx.PostEvent(watcher, send_event)


    def triggerReceiveWatchers(self, packet):
        '''
        Trigger actions bound to received packets
        '''
        # Create event
        receive_event = receiveEvent(packet=packet)

        # Post the event
        for watcher in self._receive_watchers:
            wx.PostEvent(watcher, receive_event)
    
    
    def run(self):
        '''
        The actual threaded code
        '''
        pass


class CommsException(Exception):
    pass


class CannotconnectException(CommsException):
    pass
