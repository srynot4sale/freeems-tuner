#   Copyright 2008 Aaron Barnes
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


import logging, threading, wx
import libs.config


# Tuners comms connections
_connection = {}


def createConnection(name = 'default', type = None):
    '''
    Create new comms connection, with an optional name
    '''
    if type == None:
        type = _loadDefault()
    
    type = 'comms.'+type

    # Logger
    logger = logging.getLogger('comms')
    logger.info('Loading comms module: %s' % type)

    # Dynamically import
    _connection[name] = __import__(type, globals(), locals(), 'connection').connection(type)


def getConnection(name = 'default'):
    '''
    Get comms connection
    '''
    return _connection[name]


def _loadDefault():
    '''
    Load default comms connection type from config
    '''
    return libs.config.load('Comms', 'default')


class interface(threading.Thread):
    '''
    Base class for all comms plugins

    Serial thread overview:
    - Send queue, containing raw packets.

    - run() method will process the oldest packet in the queue,
      check the receive buffer,
      send any receive buffer to the receive thread (after waking it),
      then loop again.

    - The thread must keep the connected flag up-to-date,
      as other threads will poll this continuously,
      and cant wait for the run() method to answer.

    - The thread starts in a blocked condition, waiting to receive a
      notify from a controller when its to be turned on
    '''

    _alive = True

    _connected = False
    _connectBlock = None

    _sendBuffer = []

    # Watching methods
    _send_watchers = []
    _receive_watchers = []


    def __init__(self, name):
        '''
        Sets up threading stuff
        '''
        threading.Thread.__init__(self, name = name)


    def isConnected(self):
        '''
        Returns bool flag
        '''
        return self._connected


    def _startConnectBlock(self):
        '''
        Starts blocking using self._connectBlock
        The thread will remained blocked (halted)
        until another thread runs the connect() method
        '''
        self._connectBlock = threading.Event()
        self._connectBlock.wait()

    
    def connect(self):
        '''
        Wakes up this thread and connects
        '''
        self._connectBlock.set()


    def disconnect(self):
        pass


    def exit(self):
        self._alive = False
        self._connectBlock.set()


    def bindSendWatcher(self, watcher):
        pass


    def bindReceiveWatcher(self, watcher):
        pass


    def send(self, packet):
        pass


    def bindSendWatcher(self, watcher):
        self._send_watchers.append(watcher)


    def bindReceiveWatcher(self, watcher):
        self._receive_watchers.append(watcher)
    
    
    def run(self):
        '''
        The actual threaded code
        '''
        pass


class CommsException(Exception):
    pass


class CannotconnectException(CommsException):
    pass
