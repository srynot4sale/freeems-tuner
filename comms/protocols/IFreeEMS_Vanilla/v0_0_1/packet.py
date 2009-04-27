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

import comms.protocols as protocols, __init__ as protocol


class packet:
    '''
    Serial packet base definition
    '''

    # Flags
    _headerFlags = protocols.ZEROS

    # Payload id
    _payload_id = 0

    # Payload length
    _payload_length = 0

    # Payload
    _payload = []

    # Processed packet
    _processed = []


    def getHeaderFlags(self):
        '''
        Returns header flags
        '''
        return chr(self._headerFlags)


    def parseHeaderFlags(self, flags):
        '''
        Saves header flags
        '''
        self._headerFlags = ord(flags)


    def setHeaderAckFlag(self, bool = True):
        '''
        Flag this packet as sending/requiring an ack
        '''
        if bool:
            self._headerFlags |= protocol.HEADER_HAS_ACK
        else:
            self._headerFlags &= ~protocol.HEADER_HAS_ACK


    def hasHeaderAckFlag(self):
        '''
        Return if this packet is sending/requires an ack
        '''
        return self._headerFlags & protocol.HEADER_HAS_ACK


    def setHeaderLengthFlag(self, bool = True):
        '''
        Flag this packet as having a payload length
        '''
        if bool:
            self._headerFlags |= protocol.HEADER_HAS_LENGTH
        else:
            self._headerFlags &= ~protocol.HEADER_HAS_LENGTH


    def hasHeaderLengthFlag(self):
        '''
        Return if this packet has a payload length
        '''
        return self._headerFlags & protocol.HEADER_HAS_LENGTH


    def setPayloadId(self, id):
        '''
        Set payload id
        '''
        if isinstance(id, str):
            id = protocols.shortFrom8bit(id)

        self._payload_id = id


    def getPayloadId(self):
        '''
        Return payload id as 8-bit string
        '''
        return protocols.shortTo8bit(self.getPayloadIdInt())


    def getPayloadIdInt(self):
        '''
        Return payload id as int
        '''
        return self._payload_id


    def setPayload(self, payload):
        '''
        Save payload as 8bit string
        '''
        if payload == []:
            # Hack around the send thread turning an empty payload into a list
            return
        elif isinstance(payload, str):
            self._payload = payload
        else:
            self._payload = protocols.shortTo8bit(payload)


    def getPayload(self):
        '''
        Return payload as string
        '''
        return self._payload

    
    def setPayloadLength(self, length):
        '''
        Set payload length defined in packet
        '''
        self._payload_length = protocols.shortFrom8bit(length)


    def getPayloadLength(self):
        '''
        Return payload length defined in packet
        '''
        return self._payload_length


    def getCalculatedPayloadLength(self):
        '''
        Return length of payload as 8 bit string
        '''
        return protocols.shortTo8bit(self.getCalculatedPayloadLengthInt())


    def getCalculatedPayloadLengthInt(self):
        '''
        Return length of payload as int
        '''
        return len(self.getPayload())


    def createTestResponse(self, request):
        '''
        Run any code on response to make an acurate test response
        '''
        pass


    def _buildPacket(self):
        '''
        Generate a packet
        ''' 
        packet = ''

        # Ensure the payload length packet header is set if required
        if self.getCalculatedPayloadLengthInt():
            self.setHeaderLengthFlag()

        packet += self.getHeaderFlags()
        packet += self.getPayloadId()

        if self.getCalculatedPayloadLengthInt():
            packet += self.getCalculatedPayloadLength()
            packet += self.getPayload()

        checksum = getChecksum(packet)

        return protocol.START_BYTE + escape(packet) + checksum + protocol.END_BYTE


    def prepare(self):
        '''
        Process a packet into raw bytes for sending
        '''
        self._processed = self._buildPacket()


    def getBinary(self):
        '''
        Return a packet as raw bytes
        '''
        if not self._processed:
            self.prepare()

        return self._processed


    def getHex(self):
        '''
        Return a packet as hex strings
        '''
        packet = self._buildPacket()
        return protocols.toHex(packet)


def escape(packet):
    '''
    Escape a raw packet
    '''
    for special_byte in protocol.SPECIAL_BYTES:

        processed = 0

        # Keep looping if special byte exists after bytes already processed
        while special_byte in packet[processed:]:
            # Check for any unprocessed special bytes
            i = packet.index(special_byte, processed)

            # Insert special escape byte and escaped byte
            packet = packet[:i] + protocol.ESCAPE_BYTE + chr(ord(packet[i]) ^ 0xFF) + packet[i+1:]

            # Reset processed-to index
            processed = i+1
        
    return packet


def getChecksum(bytes):
    '''
    Generate checksum of bytes
    '''
    checksum = 0
    for byte in bytes:
        checksum += ord(byte)

    return chr(checksum % 256)
