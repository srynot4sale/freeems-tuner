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

import packet
import __init__ as protocol

# Request
class request(packet.packet):

    def __init__(self):
        self.setHeaderProtocolFlag()


# Interface version request
class requestInterfaceVersion(request):

    def __init__(self):

        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_INTERFACE_VERSION)


# Firmware version request
class requestFirmwareVersion(request):

    def __init__(self):

        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_FIRMWARE_VERSION)

    
# Firmware max packet size request
class requestMaxPacketSize(request):

    def __init__(self):

        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_MAX_PACKET_SIZE)


# Firmware echo packet return request
class requestEchoPacketReturn(request):

    def __init__(self):

        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_ECHO_PACKET_RETURN)
        self.setPayload('test')


# Firmware memory block request
#class retrieveBlockFromRAM(request):
#
#    def __init__(self, block_id):
#
#        protocol.request.__init__(self)
#        self.setHeaderProtocolFlag(False)
#        self.setPayloadId(RETRIEVE_BLOCK_FROM_RAM)
#        block_id = protocols.to8bit(block_id, 2)
#        self.setPayload(block_id)


# Firmware memory block request
#    class retrieveBlockFromFlash(request):

#        def __init__(self, block_id):
#            protocol.request.__init__(self)
#            self.setHeaderProtocolFlag(False)
#            self.setPayloadId(RETRIEVE_BLOCK_FROM_FLASH)
#            block_id = protocols.to8bit(block_id, 2)
#            self.setPayload(block_id)

    # Firmware memory block request
#    class burnBlockFromRamToFlash(request):
        
#        def __init__(self, block_id):
#            protocol.request.__init__(self)
 #           self.setHeaderProtocolFlag(False)
#            self.setPayloadId(BURN_BLOCK_FROM_RAM_TO_FLASH)
#            block_id = protocols.to8bit(block_id, 2)
#            self.setPayload(block_id)
            

# Firmware system reset request (hard)
class requestHardSystemReset(request):

    def __init__(self):

        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_HARD_SYSTEM_RESET)


# Firmware system reset request (soft)
class requestSoftSystemReset(request):

    def __init__(self):

        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_SOFT_SYSTEM_RESET)
