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


import libs.config as config
import logging
import comms
import protocols

logger = logging.getLogger('comms.Test')

class connection(comms.interface):
    '''
    Fake comms interface for testings
    '''

    # Connected flag
    _connected = False

    # Watching objects
    _send_watchers = []
    _recieve_watchers = []

    # Fake buffer
    _buffer = []

    def isConnected(self):

        return self._connected

    
    def connect(self):

        if self.isConnected():
            return

        self._connected = True
        
        logger.info('Test comms connection connected')


    def disconnect(self):
        
        if not self.isConnected():
            return

        self._connected = False

        logger.info('Test comms connection disconnected')


    def bindSendWatcher(self, watcher):
        self._send_watchers.append(watcher)


    def bindRecieveWatcher(self, watcher):
        self._recieve_watchers.append(watcher)


    def send(self, packet):

        # Get protocol
        protocol = protocols.getProtocol()

        # Get return packet
        hex = protocol.getTestResponse(packet.getPayloadIdInt())

        # Append to input buffer
        # In this fake comms plugin, all sent packets
        # are reflected back at the moment
        self._buffer.extend(hex)

        # Log packet hex
        logger.debug('Packet sent to test comms connection: %s' % packet.getPacketHex())
        
        for watcher in self._send_watchers:
            watcher(packet)


    def recieve(self):
        '''Check for and recieve packets waiting in the connection'''
        
        # If nothing in buffer
        if not len(self._buffer):
            return

        # Get protocol
        protocol = protocols.getProtocol()

        # Check for any complete packets
        packet = protocol.processRecieveBuffer(self._buffer)
        
        if not packet:
            return

        logger.debug('Packet received by test comms connection: %s' % packet.getPacketHex())

        for watcher in self._recieve_watchers:
            watcher(packet)
