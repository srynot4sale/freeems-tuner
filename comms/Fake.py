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


import config
import logging
import comms

logger = logging.getLogger('comms.Fake')

class connection(comms.interface):
    '''
    Fake comms interface for testings
    '''

    # Connected flag
    __connected = False

    # Watching objects
    __send_watchers = []
    __recieve_watchers = []

    def isConnected(self):

        return self.__connected

    
    def connect(self):

        if self.isConnected():
            return

        self.__connected = True
        
        logger.info('Fake development comms connection connected')


    def disconnect(self):
        
        if not self.isConnected():
            return

        self.__connected = False

        logger.info('Fake development comms connection disconnected')


    def bindSendWatcher(self, watcher):
        self.__send_watchers.append(watcher)


    def bindRecieveWatcher(self, watcher):
        self.__recieve_watchers.append(watcher)


    def send(self, packet):

        # Get packet contents
        contents = packet.getEscaped()
        hex_contents = packet.getPacketHex()

        # Log packet hex
        logger.debug('Packet sent to fake comms connection: %s' % hex_contents)
        
        for watcher in self.__send_watchers:
            watcher(packet)
