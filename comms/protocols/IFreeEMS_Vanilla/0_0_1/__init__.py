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


import types, copy

import comms.protocols as protocols, comms, logging, send, receive, requests


START_BYTE = 0xAA
END_BYTE = 0xCC
ESCAPE_BYTE = 0xBB

HEADER_IS_PROTO     = protocols.BIT0
HEADER_HAS_ACK      = protocols.BIT1
HEADER_HAS_FAIL     = protocols.BIT2
HEADER_HAS_ADDRS    = protocols.BIT3
HEADER_HAS_LENGTH   = protocols.BIT4

REQUEST_INTERFACE_VERSION       = 0
REQUEST_FIRMWARE_VERSION        = 2
REQUEST_MAX_PACKET_SIZE         = 4
REQUEST_ECHO_PACKET_RETURN      = 6
REQUEST_SOFT_SYSTEM_RESET       = 8
REQUEST_HARD_SYSTEM_RESET       = 10
REQUEST_ASYNC_ERROR_CODE        = 12
REQUEST_ASYNC_DEBUG_INFO        = 14

RETRIEVE_BLOCK_FROM_RAM         = 4
RETRIEVE_BLOCK_FROM_FLASH       = 6
BURN_BLOCK_FROM_RAM_TO_FLASH    = 8

RESPONSE_INTERFACE_VERSION      = 1
RESPONSE_FIRMWARE_VERSION       = 3
RESPONSE_MAX_PACKET_SIZE        = 5
RESPONSE_ECHO_PACKET_RETURN     = 7
RESPONSE_SOFT_SYSTEM_RESET      = 9
RESPONSE_HARD_SYSTEM_RESET      = 11
RESPONSE_ASYNC_ERROR_CODE       = 13
RESPONSE_ASYNC_DEBUG_INFO       = 15

REQUEST_PACKET_TITLES = {
        REQUEST_INTERFACE_VERSION:   "ifVer",
        REQUEST_FIRMWARE_VERSION:    "firmVer",
        REQUEST_MAX_PACKET_SIZE:     "maxPktSize",
        REQUEST_ECHO_PACKET_RETURN:  "echoPacket",
        REQUEST_SOFT_SYSTEM_RESET:   "softReset",
        REQUEST_HARD_SYSTEM_RESET:   "hardReset",
        REQUEST_ASYNC_ERROR_CODE:    "asyncError",
        REQUEST_ASYNC_DEBUG_INFO:    "asyncDebug",
}

RESPONSE_PACKET_TITLES = {
        RESPONSE_INTERFACE_VERSION:  "ifVer",
        RESPONSE_FIRMWARE_VERSION:   "firmVer",
        RESPONSE_MAX_PACKET_SIZE:    "maxPktSize",
        RESPONSE_ECHO_PACKET_RETURN: "echoPacket",
        RESPONSE_SOFT_SYSTEM_RESET:  "softReset",
        RESPONSE_HARD_SYSTEM_RESET:  "hardReset",
        RESPONSE_ASYNC_ERROR_CODE:   "asyncError",
        RESPONSE_ASYNC_DEBUG_INFO:   "asyncDebug"
}

STATE_NOT_PACKET            = 0
STATE_ESCAPE_BYTE           = 1
STATE_IN_PACKET             = 2


# Load logging interface
logger = logging.getLogger('serial.FreeEMS_Vanilla')


def getSendObject(name, controller, comms):
    return send.thread(name, controller, comms)


def getReceiveObject(name, controller, comms):
    return receive.thread(name, controller, comms)


def getRequestPacket(type):
    '''
    Create and return a request packet
    '''
    return getattr(requests, 'request'+type)()


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
                
        # If no start or end byte, try again later when the rest of the packet has arrived
        if START_BYTE not in buffer or END_BYTE not in buffer:
            return
        
        # Find the last start byte before the first end byte
        # Keep looping until there are no start byte after the first and
        # before the first stop byte
        if buffer[0] != START_BYTE:
            start = buffer.index(START_BYTE)
            logger.debug('Bad/incomplete packet found in buffer before start byte: %s' % ','.join(protocols.toHex(buffer[0:start])))
            del buffer[0:start]

        try:
            while buffer.index(START_BYTE, 1, buffer.index(END_BYTE)):
                # Remove everything before second start byte
                start = buffer.index(START_BYTE, 1, buffer.index(END_BYTE))
                logger.debug('Bad/incomplete packet found in buffer before start byte: %s' % ','.join(protocols.toHex(buffer[0:start])))
                del buffer[0:start]
        except ValueError:
            # If we have pruned so much there is no longer a complete packet,
            # try again later
            if START_BYTE not in buffer or END_BYTE not in buffer:
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
                    raise Exception, 'Should never have got here, expecting a start byte %s' % str(byte)
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
                    state = STATE_IN_PACKET
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
