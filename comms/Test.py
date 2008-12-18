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


import time, copy
import libs.config as config, comms, protocols


class connection(comms.interface):
    '''
    Fake comms interface for testing
    '''

    # Fake buffer
    _buffer = []


    def __init__(self, name, controller):
        '''
        Initialise comms thread
        '''
        comms.interface.__init__(self, name, controller)
        self.start()


    def _connect(self):
        '''
        "Connect" to fake serial connection
        '''
        self._connWanted = False
        
        if self.isConnected():
            return

        self._connected = True
        self._debug('Test comms connection connected')


    def disconnect(self):
        '''
        "Disconnect" from fake serial connection
        '''
        self._disconnWanted = False

        if not self.isConnected():
            return

        self._connected = False
        self._debug('Test comms connection disconnected')


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
        self._debug('Packet sent to test comms connection: %s' % packet.getPacketHex())
        
        for watcher in self._send_watchers:
            watcher(packet)


    def run(self):
        '''Check for and recieve packets waiting in the connection'''

        # Get protocol
        protocol = protocols.getProtocol()

        while self.isConnected() or self._alive:

            # If not connected, block until we are ready to
            if not self.isConnected():

                # If told to connect
                if self._connWanted:
                    self._connect()
                else:
                    self._checkBlock()
                    continue

            # If connected, see if we want to disconnect
            if self.isConnected() and self._disconnWanted:
                self.disconnect()
                continue

            # If stuff in buffer
            if len(self._buffer):

                # Check for any complete packets
                cache = copy.copy(self._buffer)

                try:
                    packet = protocol.processRecieveBuffer(self._buffer)
                except Exception, msg:
                    self._debug('processReceiveBuffer failed to parse packet from buffer: %s' % join(protocols.toHex(cache)), msg)
                    self._buffer = []
                    continue
        
                if not packet:
                    continue

                logger.debug('Packet received by test comms connection: %s' % packet.getPacketHex())

                for watcher in self._receive_watchers:
                    watcher(packet)

            time.sleep(1)

        self._final()
