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

import comms.protocols as protocols, packet, __init__ as protocol


_RESPONSE_PROTOCOL_PACKETS = {
    1: 'responseInterfaceVersion',
    3: 'responseFirmwareVersion',
    5: 'responseMaxPacketSize',
    7: 'responseEchoPacketReturn',
}


def getProtocolPacket(id):
    '''
    Return instance of requested protocol packet
    '''
    if id in _RESPONSE_PROTOCOL_PACKETS:
        return getattr(self, _RESPONSE_PROTOCOL_PACKETS[id])()
    else:
        return responseGeneric()


def getFirmwarePacket(id):
    '''
    Return instance of requested firmware packet
    '''
    return responseGeneric()


class response(packet.packet):
    '''
    Reponse packet
    '''

    _validation_rules = {}

    def __init__(self):
        '''
        Set defaults
        '''

        self._validation_rules = {
            'preset_payload_length': False,
            'requires_length': False,
            'firmware_type': False,
        }


    def validate(self):
        '''
        Validate packet based on validation rules
        '''
            
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


    def parsePayload(self, payload):
        '''
        Parse the payload
        '''

        if self.hasHeaderLengthFlag():
            # If length set, account for 2 length bytes
            self.setPayloadLengthParsed(payload[0:2])
            self.setPayload(payload[2:])

        else:
            self.setPayload(payload)


class responseGeneric(response):
    '''
    Generic EMS response for bad/not yet implemented packets
    '''

    def __init__(self):
        response.__init__(self)


class responseInterfaceVersion(response):
    '''
    EMS response to interface version request
    '''

    def __init__(self):
        response.__init__(self)
        rules = self._validation_rules
        rules['requires_length'] = True


class responseFirmwareVersion(response):
    '''
    EMS response to firmware version request
    '''

    def __init__(self):
        response.__init__(self)
        rules = self._validation_rules
        rules['requires_length'] = True


class responseMaxPacketSize(response):
    '''
    EMS response to max packet length request
    '''

    def __init__(self):
        response.__init__(self)
        rules = self._validation_rules
        rules['preset_payload_length'] = 2
