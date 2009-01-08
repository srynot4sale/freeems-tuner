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

import comms.protocols as protocols, __init__ as protocol


class packet:
    '''Serial packet base definition'''

    # Flags
    _headerFlags = protocols.ZEROS

    # Payload id
    _payload_id = 0

    # Parsed payload length
    _payload_parsed_len = 0

    # Payload
    _payload = []


    def getHeaderFlags(self):
        '''Returns header flags'''
        return self._headerFlags


    def parseHeaderFlags(self, flags):
        '''Saves header flags'''
        self._headerFlags = flags


    def setHeaderProtocolFlag(self, bool = True):
        '''Flag this as a protocol packet'''
        if bool:
            self._headerFlags |= protocol.HEADER_IS_PROTO
        else:
            self._headerFlags &= ~protocol.HEADER_IS_PROTO
        

    def hasHeaderProtocolFlag(self):
        '''Return if this is a protocol packet'''
        return self._headerFlags & protocol.HEADER_IS_PROTO


    def setHeaderAckFlag(self, bool = True):
        '''Flag this packet as sending/requiring an ack'''
        if bool:
            self._headerFlags |= protocol.HEADER_HAS_ACK
        else:
            self._headerFlags &= ~protocol.HEADER_HAS_ACK


    def hasHeaderAckFlag(self):
        '''Return if this packet is sending/requires an ack'''
        return self._headerFlags & protocol.HEADER_HAS_ACK


    def setHeaderLengthFlag(self, bool = True):
        '''Flag this packet as having a payload length'''
        if bool:
            self._headerFlags |= protocol.HEADER_HAS_LENGTH
        else:
            self._headerFlags &= ~protocol.HEADER_HAS_LENGTH


    def hasHeaderLengthFlag(self):
        '''Return if this packet has a payload length'''
        return self._headerFlags & protocol.HEADER_HAS_LENGTH


    def setPayloadId(self, id):
        '''Set payload id'''
        if isinstance(id, list):
            id = protocols.from8bit(id)

        self._payload_id = id


    def getPayloadId(self):
        '''
        Return payload id
        This is padded with a 0 byte for inserting directly into packet
        '''
        return protocols.to8bit(self.getPayloadIdInt(), 2)


    def getPayloadIdInt(self):
        '''Return payload id as int'''
        return self._payload_id


    def setPayload(self, payload):
        '''Save payload as 8bit bytes'''
        if isinstance(payload, list):
            self._payload = payload
        else:
            self._payload = protocols.to8bit(payload)


    def getPayload(self):
        '''Return payload as string'''
        return self.__str__(self.getPayloadBytes())


    def getPayloadBytes(self):
        '''Return payload as bytes for inserting directly into packet'''
        return self._payload


    def getPayloadLength(self):
        '''Return length of payload'''
        return protocols.to8bit(self.getPayloadLengthInt(), 2)


    def getPayloadLengthInt(self):
        '''Return length of payload as int'''
        return len(self.getPayloadBytes())


    def setPayloadLengthParsed(self, length):
        '''Save parsed payload length'''
        if isinstance(length, list):
            length = protocols.from8bit(length)

        self._payload_parsed_length = length


    def getPayloadLengthParsed(self):
        '''Return parsed payload length'''
        return self._payload_parsed_length


    def __str__(self, bytes = None):
        '''
        Generate a raw string.
        Main use is for sending to serial connections
        '''
        if not bytes:
            bytes = self.getEscaped()

        string = ''.encode('latin-1')

        for byte in bytes:
            if byte <= 256:
                string += chr(byte)
            else:
                raise TypeError, 'Byte too big, what do I do??? %d' % byte
        
        return string


    def _buildPacket(self):
        '''
        Generate a packet
        ''' 

        packet = []

        # Ensure the payload length packet header is set if required
        if self.getPayloadLength():
            self.setHeaderLengthFlag()

        packet.append   ( self.getHeaderFlags() )
        packet.extend   ( self.getPayloadId() )

        if self.getPayloadLength():
            packet.extend   ( self.getPayloadLength() )
            packet.extend   ( self.getPayloadBytes() )

        packet = escape(packet)

        packet.append   ( getChecksum(packet) )
        packet.insert   ( 0, protocol.START_BYTE )
        packet.append   ( protocol.END_BYTE )
        
        return packet


    def getPacketRawBytes(self):
        '''
        Return a packet as raw bytes
        '''
        return self._buildPacket()


    def getPacketHex(self):
        '''Return a packet as hex strings'''
        packet = self._buildPacket()
        return protocols.toHex(packet)


def escape(packet):
    '''
    Escape a raw packet
    '''
    escaped = []

    x = 0
    length = len(packet)

    for byte in packet:
        # If first, last or not special - dont escape
        if x == 0 or x == length - 1 or byte not in (protocol.START_BYTE, protocol.ESCAPE_BYTE, protocol.END_BYTE):
            escaped.append(byte)
            continue

        # Add escape byte and escaped packet
        escaped.extend([protocol.ESCAPE_BYTE, byte | 0xFF])

    return escaped


def getChecksum(bytes):
    '''
    Generate checksum of bytes
    '''
    checksum = 0
    for byte in bytes:
        checksum += byte

    if checksum <= 256:
        return checksum

    checksum = checksum % 256
    return checksum 
