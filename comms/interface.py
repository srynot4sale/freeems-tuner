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


import libs.thread


class interface(libs.thread.thread):
    '''
    Base class for all comms plugin threads

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

    _connected = False

    # Connection wanted flag
    _connWanted = False

    # Disconnection wanted flag
    _disconnWanted = False

    _sendBuffer = []

    # Watching methods
    _send_watchers = []
    _receive_watchers = []


    def __init__(self, name, controller):
        '''
        Sets up threading stuff
        '''
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

    
    def exit(self):
        self.disconnect()
        libs.thread.thread.exit(self)


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
