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


import types
import protocols
import comms
import logging
import copy


HEADER_IS_PROTO     = protocols.BIT0
HEADER_HAS_ACK      = protocols.BIT1
HEADER_HAS_FAIL     = protocols.BIT2
HEADER_HAS_ADDRS    = protocols.BIT3
HEADER_HAS_LENGTH   = protocols.BIT4

REQUEST_INTERFACE_VERSION   = 0
REQUEST_FIRMWARE_VERSION    = 2
REQUEST_MAX_PACKET_SIZE     = 4
REQUEST_ECHO_PACKET_RETURN  = 6
REQUEST_SOFT_SYSTEM_RESET   = 8
REQUEST_HARD_SYSTEM_RESET   = 10


START_BYTE = 0xAA
END_BYTE = 0xCC
ESCAPE_BYTE = 0xBB

STATE_NOT_PACKET            = 0
STATE_ESCAPE_BYTE           = 1
STATE_IN_PACKET             = 2


# Load logging interface
logger = logging.getLogger('serial.FreeEMS_Vanilla')


class protocol:

    # Comms connection
    _connection = None

    # Utility requests
    _utility_requests = [
            'Interface Version',
            'Firmware Version',
            'Max Packet Size',
            'Echo Packet Return'
    ]

    _utility_request_packets = [
            'requestInterfaceVersion',
            'requestFirmwareVersion',
            'requestMaxPacketSize',
            'requestEchoPacketReturn',
    ]


    def getUtilityRequestList(self):
        '''Return a list of this protocols utility requests'''
        return self._utility_requests


    def sendUtilityRequest(self, request_type = None):
        '''Send a utility request'''
        packet = getattr(self, self._utility_request_packets[request_type])()

        self._sendPacket(packet)


    def sendUtilityHardResetRequest(self):
        '''Send a hardware reset utility request'''
        packet = self.requestHardSystemReset()
        
        self._sendPacket(packet)


    def sendUtilitySoftResetRequest(self):
        '''Send a hardware reset utility request'''
        packet = self.requestSoftSystemReset()
        
        self._sendPacket(packet)


    def _getComms(self):
        '''Return the protocols comm connection'''
        if not self._connection:
            self._connection = comms.getConnection()

        if not self._connection.isConnected():
            raise Exception, 'Serial comms not connected!'

        return self._connection 


    def _sendPacket(self, packet):
        '''Send a packet'''
        self._getComms().send(packet)


    def processRecieveBuffer(self, buffer):
        '''Check for any incoming packets and return if found'''

        # Check buffer is long enough to contain an entire packet
        if len(buffer) < 4:
            return
        
        # Check to make sure a start byte and an end byte exists in the buffer
        if START_BYTE not in buffer or END_BYTE not in buffer:
            return
        
        # Begin state control machine :-)
        state = STATE_NOT_PACKET
        index = -1
        packet = []

        # Loop through buffer_copy, delete from buffer
        buffer_copy = copy.copy(buffer)

        for byte in buffer_copy:
            index += 1

            # If have not started a packet yet check for start_byte
            if state == STATE_NOT_PACKET:
                # If not a start byte, its bad/incomplete data to trash it
                if byte != START_BYTE:
                    logger.error('Bad/incomplete data found in buffer before start byte: %X' % byte)
                # Otherwise, start packet
                else:
                    state = STATE_IN_PACKET
                    packet.append(START_BYTE)

            # We are in a packet, save byte unless we find an end byte
            elif state == STATE_IN_PACKET:
                if byte == END_BYTE:
                    state = STATE_NOT_PACKET
                    packet.append(END_BYTE)
                elif byte == ESCAPE_BYTE:
                    state = STATE_ESCAPE_BYTE
                else:
                    packet.append(byte)

            # If we are in escape mode (previous byte was an escape), escape byte
            elif state == STATE_ESCAPE_BYTE:
                esc_byte = byte ^ 0xFF
                
                # Check it is a legitimately escaped byte
                if esc_byte in (START_BYTE, ESCAPE_BYTE, END_BYTE):
                    packet.append(esc_byte)
                else:
                    logger.error('Wrongly escaped byte found in buffer: %X' % byte)

            del buffer[0]

            # Check if we have a complete packet
            if len(packet) and state == STATE_NOT_PACKET:
                return packet


    class packet:
        '''Serial packet base definition'''

        # Flags
        _headerFlags = protocols.ZEROS

        # Payload id
        _payload_id = 0

        # Payload
        _payload = ''

        def getHeaderFlags(self):
            '''Returns header flags'''
            return self._headerFlags


        def setHeaderProtocolFlag(self, bool = True):
            '''Flag this as a protocol packet'''
            if bool:
                self._headerFlags |= HEADER_IS_PROTO
            else:
                self._headerFlags &= ~HEADER_IS_PROTO
            

        def hasHeaderProtocolFlag(self):
            '''Return if this is a protocol packet'''
            return self._headerFlags & HEADER_IS_PROTO


        def setHeaderAckFlag(self, bool = True):
            '''Flag this packet as sending/requiring an ack'''
            if bool:
                self._headerFlags |= HEADER_HAS_ACK
            else:
                self._headerFlags &= ~HEADER_HAS_ACK


        def hasHeaderAckFlag(self):
            '''Return if this packet is sending/requires an ack'''
            return self._headerFlags & HEADER_HAS_ACK


        def setHeaderLengthFlag(self, bool = True):
            '''Flag this packet as having a payload length'''
            if bool:
                self._headerFlags |= HEADER_HAS_LENGTH
            else:
                self._headerFlags &= ~HEADER_HAS_LENGTH


        def hasHeaderLengthFlag(self):
            '''Return if this packet has a payload length'''
            return self._headerFlags & HEADER_HAS_LENGTH


        def setPayloadId(self, id):
            '''Set payload id'''
            if not isinstance(id, types.IntType):
                raise TypeError, 'Integer required for payload id'

            self._payload_id = id


        def getPayloadId(self):
            '''
            Return payload id
            This is padded with a 0 byte for inserting directly into packet
            '''
            return protocols.to8bit(self._payload_id, 2)


        def setPayload(self, payload):
            '''Save payload'''
            self._payload = payload


        def getPayload(self):
            '''Return payload'''
            return self._payload


        def getPayloadBytes(self):
            '''Return payload as bytes for inserting directly into packet'''
            return protocols.to8bit(self.getPayload())


        def getPayloadLength(self):
            '''Return length of payload'''
            return protocols.to8bit(len(self.getPayload()), 2)


        def getChecksum(self, bytes):
            '''Generate checksum of bytes'''
            checksum = 0
            for byte in bytes:
                checksum += byte

            if checksum <= 256:
                return checksum

            checksum = checksum % 256
            return checksum 


        def __str__(self):
            '''Generate a string for serial connections'''
            packet = self.getEscaped()
            string = ''.encode('latin-1')

            for byte in packet:
                if byte <= 256:
                    string += chr(byte)
                else:
                    raise TypeError, 'Byte too big, what do I do??? %d' % byte
            
            return string


        def buildPacket(self):
            '''Generate a packet''' 

            packet = []

            # Ensure the payload length packet header is set if required
            if self.getPayloadLength():
                self.setHeaderLengthFlag()

            packet.append   ( self.getHeaderFlags() )
            packet.extend   ( self.getPayloadId() )

            if self.getPayloadLength():
                packet.extend   ( self.getPayloadLength() )
                packet.extend   ( self.getPayloadBytes() )

            packet.append   ( self.getChecksum(packet) )
            packet.insert   ( 0, START_BYTE )
            packet.append   ( END_BYTE )
            
            return packet


        def getEscaped(self):
            '''Return an escaped packet'''
            packet = self.buildPacket()
            escaped = []

            x = 0
            length = len(packet)

            for byte in packet:
                # If first, last or not special - dont escape
                if x == 0 or x == length - 1 or byte not in (START_BYTE, ESCAPE_BYTE, END_BYTE):
                    escaped.append(byte)
                    continue

                # Add escape byte and escaped packet
                escaped.extend([ESCAPE_BYTE, byte | 0xFF])

            return escaped


        def getPacketHex(self):
            '''Return a packet as hex strings'''
            packet = self.getEscaped()

            raw_hex = []
            for byte in packet:
                byte = hex(byte).upper().replace('X','x')
                if len(byte) == 3:
                    byte = '0x0'+byte[-1]

                raw_hex.append(byte)
            
            return raw_hex


    # Request
    class request(packet):

        def __init__(self):
            self.setHeaderProtocolFlag()


    # Interface version request
    class requestInterfaceVersion(request):

        def __init__(self):

            protocol.request.__init__(self)
            self.setPayloadId(REQUEST_INTERFACE_VERSION)


    # Firmware version request
    class requestFirmwareVersion(request):

        def __init__(self):

            protocol.request.__init__(self)
            self.setPayloadId(REQUEST_FIRMWARE_VERSION)

    
    # Firmware max packet size request
    class requestMaxPacketSize(request):

        def __init__(self):

            protocol.request.__init__(self)
            self.setPayloadId(REQUEST_MAX_PACKET_SIZE)


    # Firmware echo packet return request
    class requestEchoPacketReturn(request):

        def __init__(self):

            protocol.request.__init__(self)
            self.setPayloadId(REQUEST_ECHO_PACKET_RETURN)
            self.setPayload('test')


    # Firmware system reset request (hard)
    class requestHardSystemReset(request):

        def __init__(self):

            protocol.request.__init__(self)
            self.setPayloadId(REQUEST_HARD_SYSTEM_RESET)


    # Firmware system reset request (soft)
    class requestSoftSystemReset(request):

        def __init__(self):

            protocol.request.__init__(self)
            self.setPayloadId(REQUEST_SOFT_SYSTEM_RESET)


