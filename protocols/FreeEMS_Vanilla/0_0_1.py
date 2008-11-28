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
REQUEST_ASYNC_ERROR_CODE    = 12
REQUEST_ASYNC_DEBUG_INFO    = 14

RETRIEVE_BLOCK_FROM_RAM     = 4
RETRIEVE_BLOCK_FROM_FLASH   = 6
BURN_BLOCK_FROM_RAM_TO_FLASH = 8

RESPONSE_INTERFACE_VERSION  = 1
RESPONSE_FIRMWARE_VERSION   = 3
RESPONSE_MAX_PACKET_SIZE    = 5
RESPONSE_ECHO_PACKET_RETURN = 7
RESPONSE_SOFT_SYSTEM_RESET  = 9
RESPONSE_HARD_SYSTEM_RESET  = 11
RESPONSE_ASYNC_ERROR_CODE   = 13
RESPONSE_ASYNC_DEBUG_INFO   = 15

PACKET_IDS = {
        REQUEST_INTERFACE_VERSION:   "ifVer",
        RESPONSE_INTERFACE_VERSION:  "ifVer",
        REQUEST_FIRMWARE_VERSION:    "firmVer",
        RESPONSE_FIRMWARE_VERSION:   "firmVer",
        REQUEST_MAX_PACKET_SIZE:     "maxPktSize",
        RESPONSE_MAX_PACKET_SIZE:    "maxPktSize",
        REQUEST_ECHO_PACKET_RETURN:  "echoPacket",
        RESPONSE_ECHO_PACKET_RETURN: "echoPacket",
        REQUEST_SOFT_SYSTEM_RESET:   "softReset",
        RESPONSE_SOFT_SYSTEM_RESET:  "softReset",
        REQUEST_HARD_SYSTEM_RESET:   "hardReset",
        RESPONSE_HARD_SYSTEM_RESET:  "hardReset",
        REQUEST_ASYNC_ERROR_CODE:    "asyncError",
        RESPONSE_ASYNC_ERROR_CODE:   "asyncError",
        REQUEST_ASYNC_DEBUG_INFO:    "asyncDebug",
        RESPONSE_ASYNC_DEBUG_INFO:   "asyncDebug"
}

START_BYTE = 0xAA
END_BYTE = 0xCC
ESCAPE_BYTE = 0xBB

STATE_NOT_PACKET            = 0
STATE_ESCAPE_BYTE           = 1
STATE_IN_PACKET             = 2

TEST_RESPONSES = {
    REQUEST_INTERFACE_VERSION:      [0xAA, 0x11, 0x00, 0x01, 0x00, 0x14, 0x00, 0x00,
                                     0x02, 0x49, 0x46, 0x72, 0x65, 0x65, 0x45, 0x4D,
                                     0x53, 0x20, 0x56, 0x61, 0x6E, 0x69, 0x6C, 0x6C,
                                     0x61, 0x00, 0xBF, 0xCC],
    REQUEST_FIRMWARE_VERSION:       [0xAA, 0x11, 0x00, 0x03, 0x00, 0x22, 0x46, 0x72,
                                     0x65, 0x65, 0x45, 0x4D, 0x53, 0x20, 0x56, 0x61,
                                     0x6E, 0x69, 0x6C, 0x6C, 0x61, 0x20, 0x76, 0x30,
                                     0x2E, 0x30, 0x2E, 0x31, 0x37, 0x20, 0x70, 0x72,
                                     0x65, 0x2D, 0x61, 0x6C, 0x70, 0x68, 0x61, 0x00,
                                     0xD8, 0xCC],
    REQUEST_MAX_PACKET_SIZE:        [0xAA, 0x01, 0x00, 0x05, 0x04, 0x10, 0x1A, 0xCC],
    REQUEST_ECHO_PACKET_RETURN:     [0xAA, 0x01, 0x00, 0x20, 0x04, 0x10, 0x35, 0xCC],
    REQUEST_SOFT_SYSTEM_RESET: [],
    REQUEST_HARD_SYSTEM_RESET: []
}


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

    _response_protocol_packets = {
        1: 'responseInterfaceVersion',
        3: 'responseFirmwareVersion',
        5: 'responseMaxPacketSize',
        7: 'responseEchoPacketReturn',
    }

    _response_firmware_packets = {}

    _memory_request_block_ids = {
        0: 'VETableMainFlashLocationID',
        1: 'VETableMainFlash2LocationID',
        2: 'VETableSecondaryFlashLocationID',
        3: 'VETableSecondaryFlash2LocationID',
        4: 'VETableTertiaryFlashLocationID',
        5: 'VETableTertiaryFlash2LocationID',
    }

    _memory_request_payload_ids = {
        0: 'retrieveBlockFromRAM',
        1: 'retrieveBlockFromFlash',
        2: 'burnBlockFromRamToFlash',
    }


    def getPacketType(self, id):
        '''Returns human readable packet type'''
        try:
            return PACKET_IDS[id]
        except KeyError:
            return 'unknown'


    def getUtilityRequestList(self):
        '''Return a list of this protocols utility requests'''
        return self._utility_requests


    def getMemoryRequestBlockIdList(self):
        '''Return a list of this protocols memory request block IDs'''
        return self._memory_request_block_ids


    def getMemoryRequestPayloadIdList(self):
        '''Return a list of this protocols memory request payload IDs'''
        return self._memory_request_payload_ids


    def sendUtilityRequest(self, request_type = None):
        '''Send a utility request'''
        packet = getattr(self, self._utility_request_packets[request_type])()

        self._sendPacket(packet)


    def sendMemoryRequest(self, request_type = None, request_type2 = None):
        '''Send a memory request'''
        packet = getattr(self, self._memory_request_payload_ids[request_type])(request_type2)
        
        self._sendPacket(packet)


    def sendUtilityHardResetRequest(self):
        '''Send a hardware reset utility request'''
        packet = self.requestHardSystemReset()
        
        self._sendPacket(packet)


    def sendUtilitySoftResetRequest(self):
        '''Send a hardware reset utility request'''
        packet = self.requestSoftSystemReset()
        
        self._sendPacket(packet)


    def getTestResponse(self, response_to):
        '''Return hardcoded correct raw response packet'''
        if response_to in TEST_RESPONSES:
            return TEST_RESPONSES[response_to]

        else:
            return []

    
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


    def _unEscape(self, packet):
        '''Unescape a raw packet'''
        i = 0
        while i < len(packet):

            if packet[i] == ESCAPE_BYTE:

                del packet[i]
                packet[i] ^= 0xFF

                if packet[i] not in (START_BYTE, ESCAPE_BYTE, END_BYTE):
                    logger.error('Wrongly escaped byte found in packet: %X' % packet[i])

            i += 1

        return packet


    def processRecieveBuffer(self, buffer):
        '''Check for any incoming packets and return if found'''
        
        # Check to make sure the first byte is a start byte
        # If not, clean up bad bytes
        if buffer[0] != START_BYTE:
            # Remove everything before
            start = buffer.index(START_BYTE)
            logger.debug('Bad/incomplete data found in buffer before start byte: %s' % ','.join(protocols.toHex(buffer[0:start])))
            del buffer[0:start]

        # If no end byte, try again later when the rest of the packet has arrived
        if END_BYTE not in buffer:

            # Quick check to make sure there isn't another packet banked up after
            # an incomplete one
            if not buffer.index(START_BYTE, 1):
                return

            start = buffer.index(START_BYTE, 1)
            logger.debug('Bad/incomplete packet found in buffer before a legitimate packet: %s' % ','.join(protocols.toHex(buffer[0:start])))
            del buffer[0:start]
            return
        
        # Begin state control machine :-)
        state = STATE_NOT_PACKET
        index = 0
        packet = []
        bad_bytes = []
        complete = False

        # Loop through buffer_copy, delete from buffer
        buffer_copy = copy.copy(buffer)

        for byte in buffer_copy:

            # If have not started a packet yet check for start_byte
            if state == STATE_NOT_PACKET:
                # If not a start byte, we should never have got here
                if byte != START_BYTE:
                    raise Exception, 'Should never have got here, expecting a start byte'
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

            # Remove this byte from buffer as it has been processed
            del buffer[0]

            index += 1

            # Check if we have a complete packet
            if len(packet) and state == STATE_NOT_PACKET:
                complete = self.processIncomingPacket(packet)
                break

        # Process bad_bytes buffer
        if len(bad_bytes):
            logger.debug('Bad/incomplete data found in buffer before start byte: %s' % ','.join(protocols.toHex(bad_bytes)))

        return complete        


    def processIncomingPacket(self, packet):
        '''Takes a raw packet, checks it and returns the correct packet class'''

        # Quick checks to make sure this is a legitimate packet
        if not isinstance(packet, list):
            raise TypeError, 'Expected a list'

        if packet[0] != START_BYTE or packet[-1] != END_BYTE:
            raise Exception, 'Start and/or end byte missing'

        packet = self._unEscape(packet)

        contents = {}
        contents['flags'] = None
        contents['payload_id'] = None
        contents['payload'] = []
        contents['checksum'] = None

        index = 1

        # Grab flags
        contents['flags'] = flags = packet[index]
        index += 1

        # Grab payload id
        contents['payload_id'] = protocols.from8bit(packet[index:index+2])
        index += 2

        # Grab payload
        contents['payload'] = payload = packet[index:(len(packet) - 2)]
        index += len(payload)

        # Grab checksum
        contents['checksum'] = checksum = packet[index]
        index += 1

        # Check checksum
        gen_checksum = getChecksum(packet[1:index-1])

        if checksum != gen_checksum:
            raise Exception, 'Checksum is incorrect! Provided: %d, generated: %d' % (checksum, gen_checksum)

        # Just double check we only have one byte left
        if index != (len(packet) - 1):
            raise Exception, 'Packet incorrectly processed, %d bytes left' % (len(packet) - 1 - index)

        # Create response packet object
        if contents['flags'] & HEADER_IS_PROTO:
            packet_types = self._response_protocol_packets
        else:
            packet_types = self._response_firmware_packets

        try:
            type = packet_types[contents['payload_id']]
        except KeyError:
            type = 'responseGeneric'

        if not hasattr(self, type):
            type = 'responseGeneric'

        response = getattr(self, type)()

        # Populate data
        response.parseHeaderFlags(contents['flags'])
        response.setPayloadId(contents['payload_id'])
        response.parsePayload(contents['payload'])
        response.validate()

        return response


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

            packet.append   ( getChecksum(packet) )
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
            return protocols.toHex(packet)


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


    # Firmware memory block request
    class retrieveBlockFromRAM(request):

        def __init__(self, block_id):
            protocol.request.__init__(self)
            self.setHeaderProtocolFlag(False)
            self.setPayloadId(RETRIEVE_BLOCK_FROM_RAM)
            block_id = protocols.to8bit(block_id, 2)
            self.setPayload(block_id)


    # Firmware memory block request
    class retrieveBlockFromFlash(request):

        def __init__(self, block_id):
            protocol.request.__init__(self)
            self.setHeaderProtocolFlag(False)
            self.setPayloadId(RETRIEVE_BLOCK_FROM_FLASH)
            block_id = protocols.to8bit(block_id, 2)
            self.setPayload(block_id)

    # Firmware memory block request
    class burnBlockFromRamToFlash(request):
        
        def __init__(self, block_id):
            protocol.request.__init__(self)
            self.setHeaderProtocolFlag(False)
            self.setPayloadId(BURN_BLOCK_FROM_RAM_TO_FLASH)
            block_id = protocols.to8bit(block_id, 2)
            self.setPayload(block_id)
            

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

    
    class response(packet):
        '''Reponse packet'''

        _validation_rules = {}

        def __init__(self):
            '''Set defaults'''

            self._validation_rules = {
                'preset_payload_length': False,
                'requires_length': False,
                'firmware_type': False,
            }


        def validate(self):
            '''Validate packet based on validation rules'''
            
            rules = self._validation_rules
            pid = self.getPayloadIdInt()

            if rules['preset_payload_length']:
                # Check payload is the required length
                if rules['preset_payload_length'] != self.getPayloadLengthInt():
                    raise Exception, 'Packet type %d preset length of %s does not match the actual payload length of %s' % (pid, rules['preset_payload_length'], self.getPayloadLengthInt())
            
            if rules['requires_length']:
                # Check a length was supplied and the payload matches
                if not self.hasHeaderLengthFlag():
                    raise Exception, 'Packet type %s was expecting a length flag to be set' % pid

                length = self.getPayloadLengthParsed()
                if not length:
                    raise Exception, 'Packet type %s was expecting a length to be set' % pid

                if self.getPayloadLengthInt() != length:
                    raise Exception, 'Packet type %s, payload length of %s does not match parsed length of %s' % (pid, self.getPayloadLengthInt(), length)

            if rules['firmware_type']:
                # Check firmware type flag is set
                if self.hasHeaderProtocolFlag():
                    raise Exception, 'Packet type %s requires the firmware flag is set' % pid

            else:
                # Check firmware type flag is not set
                if not self.hasHeaderProtocolFlag():
                    raise Exception, 'Packet type %s requires the protocol flag is set' % pid


        def parsePayload(self, payload):
            '''Parse the payload'''

            if self.hasHeaderLengthFlag():
                # If length set, account for 2 length bytes
                self.setPayloadLengthParsed(payload[0:2])
                self.setPayload(payload[2:])

            else:
                self.setPayload(payload)


    class responseGeneric(response):
        '''Generic EMS response for bad/not yet implemented packets'''

        def __init__(self):
            protocol.response.__init__(self)


    class responseInterfaceVersion(response):
        '''EMS response to interface version request'''

        def __init__(self):
            protocol.response.__init__(self)
            rules = self._validation_rules
            rules['requires_length'] = True


    class responseFirmwareVersion(response):
        '''EMS response to firmware version request'''

        def __init__(self):
            protocol.response.__init__(self)
            rules = self._validation_rules
            rules['requires_length'] = True


    class responseMaxPacketSize(response):
        '''EMS response to max packet length request'''

        def __init__(self):
            protocol.response.__init__(self)
            rules = self._validation_rules
            rules['preset_payload_length'] = 2


def getChecksum(bytes):
    '''Generate checksum of bytes'''
    checksum = 0
    for byte in bytes:
        checksum += byte

    if checksum <= 256:
        return checksum

    checksum = checksum % 256
    return checksum 
