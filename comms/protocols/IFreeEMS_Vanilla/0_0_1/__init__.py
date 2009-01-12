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

