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


import comms.protocols as protocols, send, receive, requests, responses, test


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

RESPONSE_INTERFACE_VERSION      = 1
RESPONSE_FIRMWARE_VERSION       = 3
RESPONSE_MAX_PACKET_SIZE        = 5
RESPONSE_ECHO_PACKET_RETURN     = 7
RESPONSE_SOFT_SYSTEM_RESET      = 9
RESPONSE_HARD_SYSTEM_RESET      = 11
RESPONSE_ASYNC_ERROR_CODE       = 13
RESPONSE_ASYNC_DEBUG_INFO       = 15

RETRIEVE_BLOCK_FROM_RAM         = 4
RETRIEVE_BLOCK_FROM_FLASH       = 6
BURN_BLOCK_FROM_RAM_TO_FLASH    = 8

REQUEST_PACKET_TITLES = {
        REQUEST_INTERFACE_VERSION:   "InterfaceVersion",
        REQUEST_FIRMWARE_VERSION:    "FirmwareVersion",
        REQUEST_MAX_PACKET_SIZE:     "MaxPacketSize",
        REQUEST_ECHO_PACKET_RETURN:  "EchoPacket",
        REQUEST_SOFT_SYSTEM_RESET:   "SoftReset",
        REQUEST_HARD_SYSTEM_RESET:   "HardReset",
        REQUEST_ASYNC_ERROR_CODE:    "AsyncError",
        REQUEST_ASYNC_DEBUG_INFO:    "AsyncDebug",
}

RESPONSE_PACKET_TITLES = {
        RESPONSE_INTERFACE_VERSION:  "InterfaceVersion",
        RESPONSE_FIRMWARE_VERSION:   "FirmwareVersion",
        RESPONSE_MAX_PACKET_SIZE:    "MaxPacketSize",
        RESPONSE_ECHO_PACKET_RETURN: "EchoPacket",
        RESPONSE_ASYNC_ERROR_CODE:   "AsyncError",
        RESPONSE_ASYNC_DEBUG_INFO:   "AsyncDebug"
}
        
MEMORY_PACKET_TITLES = {
        RETRIEVE_BLOCK_FROM_RAM:     "RetrieveBlockFromRAM",
        RETRIEVE_BLOCK_FROM_FLASH:   "RetrieveBlockFromFlash",
        BURN_BLOCK_FROM_RAM_TO_FLASH:"BurnBlockFromRamToFlash"
}


UTILITY_REQUEST_PACKETS = {
        'Interface Version':        'InterfaceVersion',
        'Firmware Version':         'FirmwareVersion',
        'Max Packet Size':          'MaxPacketSize',
        'Echo Packet Return':       'EchoPacketReturn'
}


def getSendObject(name, controller, comms):
    return send.thread(name, controller, comms)


def getReceiveObject(name, controller, comms):
    return receive.thread(name, controller, comms)


def getRequestPacket(type):
    '''
    Create and return a request packet
    '''
    return getattr(requests, 'request'+type)()


def getResponsePacket(type):
    '''
    Create and return a response packet
    '''
    return getattr(responses, 'response'+type)()


def getPacketName(id):
    '''
    Return human readable packet type
    '''
    if id in REQUEST_PACKET_TITLES:
        return REQUEST_PACKET_TITLES[id]
    elif id in RESPONSE_PACKET_TITLES:
        return RESPONSE_PACKET_TITLES[id]
    else:
        return 'Unknown'


def getMemoryRequestPayloadIdList():
    '''
    Return list of memory request payload ids
    '''
    return MEMORY_PACKET_TITLES


def getTestResponse(packet):
    '''
    Generate and return the correct response to apacket
    '''
    return test.getResponse(packet)
