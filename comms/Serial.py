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


import libs.serial as serial
import libs.serial.serialutil as serialutil
import libs.config as config
import logging
import copy
import comms
import protocols

logger = logging.getLogger('comms.Serial')

class connection(comms.interface):

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


    # Watching objects
    _send_watchers = []
    _recieve_watchers = []


    # Unprocessed buffer contents
    _buffer = []

    def __init__(self):

        section     = 'Comms_Serial'
        s           = self._settings
        s.port      = config.load(section, 'port')
        s.baudrate  = int(config.load(section, 'baudrate'))
        s.bytesize  = int(config.load(section, 'bytesize'))
        s.parity    = config.load(section, 'parity')
        s.stopbits  = int(config.load(section, 'stopbits'))
        s.timeout   = int(config.load(section, 'timeout'))
        s.xonxoff   = config.loadBool(section, 'xonxoff')
        s.rtscts    = config.loadBool(section, 'rtscts')

        s.parity    = s.parity[0:1]


    def isConnected(self):

        return bool(self._connection)# and self.isOpen()

    
    def getConnection(self):

        if not self.isConnected():
            raise Exception, 'Not connected'
        
        return self._connection


    def connect(self):

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
            raise comms.CannotconnectException, msg

        
        logger.info('Serial connection established to %s' % s.port)
        
        conn.setRTS(1)
        conn.setDTR(1)
        conn.flushInput()
        conn.flushOutput()


    def disconnect(self):
        
        if not self.isConnected():
            return

        self._connection.close()
        self._connection = None

        logger.info('Serial connection to %s closed' % self._settings.port)


    def bindSendWatcher(self, watcher):
        self._send_watchers.append(watcher)


    def bindRecieveWatcher(self, watcher):
        self._recieve_watchers.append(watcher)


    def send(self, packet):
        '''Send a packet over the connection'''
        self.getConnection().write(packet.__str__())
        self.getConnection().flushOutput()
        
        logger.debug('Packet sent over Serial connection: %s' % packet.getPacketHex())

        for watcher in self._send_watchers:
            watcher(packet)


    def recieve(self):
        '''Check for and recieve packets waiting in the connection'''
        conn = self.getConnection()
        buffer_size = conn.inWaiting()

        # If nothing in serial buffer, and nothing unprocessed
        # don't hold up the UI any longer than we have to
        if not buffer_size and not len(self._buffer):
            return

        # If anything new in the buffer, convert to bytes and
        # append to what we have left unprocessed
        if buffer_size:
            buffer = conn.read(buffer_size)

            for char in buffer:
                self._buffer.append(ord(char))

        # Get protocol
        protocol = protocols.getProtocol()

        # Check for any complete packets
        try:
            cache = copy.copy(self._buffer)
            packet = protocol.processRecieveBuffer(self._buffer)
        except Exception, msg:
            logger.error(msg)
            logger.error('processRecieveBuffer failed to parse packet from buffer: %s' % cache)
            self._buffer = []
            return

        if not packet:
            return

        logger.debug('Packet received by Serial connection: %s' % packet.getPacketHex())

        for watcher in self._recieve_watchers:
            watcher(packet)
