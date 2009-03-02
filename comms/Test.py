#   Copyright 2008, 2009 Aaron Barnes
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
import libs.config as config, comms.interface, protocols


class connection(comms.interface.interface):
    '''
    Fake comms interface for testing
    '''

    # Fake receive buffer
    _buffer = ''


    def __init__(self, name, controller):
        '''
        Initialise comms thread
        '''
        comms.interface.interface.__init__(self, name, controller)

        # Load protocol
        self.getProtocol()

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


    def _disconnect(self):
        '''
        "Disconnect" from fake serial connection
        '''
        self._disconnWanted = False

        self.stopLogging()

        if not self.isConnected():
            return

        self._connected = False
        self._debug('Test comms connection disconnected')


    def _send(self, packet):
        '''
        "Sends" a packet over the fake serial connection
        and generates a suitable reply

        In the interest of testing the packet parsers, this
        comms plugin also parses the sent raw packets back
        into abstract packets.
        '''
        # Reparse packet to check all is ok
        #self.getProtocol().checkPacket(packet)

        # Get preset return packet
        response = self.getProtocol().getTestResponse(packet)
        if response:
            # Append to input buffer
            # In this fake comms plugin, all sent packets
            # are reflected back at the moment
            response.prepare()
            self._buffer += response.getBinary()

        # Log packet hex
        self._debug('Packet sent to test comms connection: %s' % packet.getHex())


    def run(self):
        '''
        Check for and receive packets waiting in the connection
        '''

        # Get protocol
        protocol = self.getProtocol()

        # Create send and receive threads
        self._createSendThread()
        self._createReceiveThread()

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
                self._disconnect()
                continue

            # If stuff in receive buffer
            if len(self._buffer):
                self.logBuffer(self._buffer)
                self._receive(self._buffer)
                self._buffer = ''

            # If stuff in send buffer
            while len(self._queue):
                self._send(self._queue.pop(0))

            self._checkBlock()

        self._final()
