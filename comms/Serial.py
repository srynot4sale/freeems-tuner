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
import libs.config as config, libs.serial as serial, libs.serial.serialutil as serialutil, comms.interface, protocols


class connection(comms.interface.interface):
    '''
    Serial comms connection thread
    '''

    # Serial connection
    _connection = None

    class _settings:
        port        = 0
        baudrate    = 0
        bytesize    = 0
        parity      = 0
        stopbits    = 0
        timeout     = 0
        xonxoff     = 0
        rtscts      = 0


    # Unprocessed buffer contents
    _buffer = []


    def __init__(self, name, controller):
        '''
        Initialise comms thread and setup serial
        '''
        comms.interface.interface.__init__(self, name, controller)

        section     = 'Comms_Serial'
        s           = self._settings
        s.port      = config.get(section, 'port')
        s.baudrate  = int(config.get(section, 'baudrate'))
        s.bytesize  = int(config.get(section, 'bytesize'))
        s.parity    = config.get(section, 'parity')
        s.stopbits  = int(config.get(section, 'stopbits'))
        s.timeout   = int(config.get(section, 'timeout'))
        s.xonxoff   = config.getBool(section, 'xonxoff')
        s.rtscts    = config.getBool(section, 'rtscts')

        s.parity    = s.parity[0:1]

        # Load protocol
        self.getProtocol()

        self.start()


    def _getConnection(self):
        '''
        Return connection
        '''

        if not self.isConnected():
            raise Exception, 'Not connected'
        
        return self._connection


    def _connect(self):
        '''
        Connect serial connection
        '''
        self._connWanted = False
        
        if self.isConnected():
            return

        s = self._settings

        try:
            self._connection = conn = serial.Serial(
                s.port,
                baudrate    = s.baudrate,
                bytesize    = s.bytesize,
                parity      = s.parity,
                stopbits    = s.stopbits,
                timeout     = s.timeout,
                xonxoff     = s.xonxoff,
                rtscts      = s.rtscts,
            )

        except serialutil.SerialException, msg:
            raise comms.interface.CannotconnectException, msg

        self._connected = True
        self._debug('Serial comms connection established to %s' % self._settings.port)

        conn.setRTS(1)
        conn.setDTR(1)
        conn.flushInput()
        conn.flushOutput()


    def _disconnect(self):
        '''
        "Disconnect" from fake serial connection
        '''
        self._disconnWanted = False

        if not self.isConnected():
            return

        self._connection.close()
        self._connection = None

        self._connected = False
        self._debug('Serial comms connection to %s closed' % self._settings.port)

    
    def _send(self, packet):
        '''
        Send a packet over the connection
        '''
        self.getConnection().write(''.join(packet))
        self.getConnection().flushOutput()
        
        # Log packet hex
        self._debug('Packet sent to test comms connection: %s' % ','.join(protocols.toHex(packet)))
        return
        for watcher in self._send_watchers:
            watcher(packet)


    def run(self):
        '''Check for and receive packets waiting in the connection'''

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
            conn = self.getConnection()
            if conn.inWaiting():
                buffer = conn.read(buffer_size)

                for char in buffer:
                    self._buffer.append(ord(char))

                self._receive(self._buffer)
                self._buffer = []

            # If stuff in send buffer
            while len(self._queue):
                self._send(self._queue.pop(0))

            self._checkBlock()

        self._final()
