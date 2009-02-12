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

import copy, types

import libs.thread, comms.protocols as protocols, __init__ as protocol, packet as packetlib, responses


class thread(libs.thread.thread):
    '''
    Thread for handling the receive queue and
    abstract -> raw packet processing
    '''

    # Comms plugin that created this thread
    comms = None

    # Buffer of raw data to process into packet classes
    _buffer = []

    # Queue of processed packets ready to be handled by the controller
    queue = []


    def __init__(self, name, controller, comms):
        '''
        Sets up threading stuff
        '''
        self._setup(name, controller)
        self.comms = comms

        self._debug('Receive thread created')
        self.start()

    
    def received(self, buffer):
        '''
        Add to buffer and wake thread
        '''
        self._buffer.append(buffer)
        #self._debug('Received %d bytes of buffer' % len(buffer))
        self.wake()


    def run(self):
        '''
        Loop through buffer and process into complete packets
        '''
        while self._alive:
            # If buffer non-empty, process
            if len(self._buffer):
                self._process()

            # Otherwise wait to be awoken
            else:
                self._checkBlock()

        self._final()


    def _process(self):
        '''
        Processes buffer into packets

        The reason for having a cache string and not processing the raw
        buffer directly is to keep things thread safe simpler. By processing
        the cache and only adding to it from the same thread, we can be sure
        it is not going to be added to mid-processing.
        '''
        cache = ''

        # Check for any complete packets
        while self._buffer or cache:
            
            if len(self._buffer):
                cache += self._buffer.pop(0)

            try:
                packet = self._processBuffer(cache)
            except ParsingException, msg:
                self._error('processReceiveBuffer could not parse buffer. %s' % msg, protocols.toHex(cache))
                continue
            except Exception, msg:
                # Program error, clean buffer
                self._error('processReceiveBuffer threw exception, wiping buffer: %s' % msg, protocols.toHex(cache))
                cache = ''
                continue
        
            if not packet:
                continue

            # Tell controller to handle newly received packets
            self.queue.append(packet)
    
            data = { 'comms': self.comms, 'queue': self.queue }
            self._controller.action('comms.handleReceivedPackets', data)
   

    def _processBuffer(self, buffer):
        '''
        Check for any incoming packets and return if found

        - Removing anything before first START_BYTE
        - Check for END_BYTE
        - Loop though buffer copy
            - If complete packet found, remove length from buffer
            - If incomplete packet, leave buffer and try again later
        '''
        # Remove any buffer before the first start byte
        if buffer[0] !== protocol.START_BYTE:
            if protocol.START_BYTE not in buffer:
                tmp = buffer
                del buffer[:]
            else:
                index = buffer.index(protocol.START_BYTE)
                tmp = buffer[:index]
                del buffer[:index]

            raise ParsingException, 'Bad/incomplete packet found in buffer before start byte %s' % protocol.toHex(tmp)

        # If no end byte in buffer, return as it must not contain a complete packet
        if protocol.END_BYTE not in buffer:
            return

        # Grab packet from buffer (minus start and end bytes)
        end = buffer.index(protocol.END_BYTE)
        packet = buffer[1:end-1] 

        # Clear processed buffer
        del buffer[:end]

        # Process packet
        return self._processIncomingPacket(packet)


    def _processIncomingPacket(self, packet):
        '''
        Takes a raw packet, checks it and returns the correct packet class
        '''
        # Check for special bytes n packet that shouldn't be there
        if (protocol.START_BYTE, protocol.END_BYTE) in packet:
            raise ParsingException, 'Unescaped bytes found in packet: %s' % protocols.toHex(packet)
        
        # Process escapes
        while protocol.ESCAPE_BYTE in packet:
            i = packet.index(protocol.ESCAPE_BYTE)
            if packet[i + 1] in (protocol.START_BYTE, protocol.END_BYTE, protocol.ESCAPE_BYTE):
                del packet[i]
                # Convert escaped byte to an integer to XOR, and then convert back to a string
                packet[i] = chr(ord(packet[i]) ^ 0xFF)
            else:
                raise ParsingException, 'Wrongly escaped byte found in packet: %s' % protocols.toHex(packet)

        # Split up packet
        contents = {
                'flags':        packet[0],
                'payload_id':   protocols.from8bit(packet[1:2]),
                'payload':      packet[3:-2]
                'checksum':     packet[-1]
        }

        # Check checksum
        gen_checksum = packetlib.getChecksum(packet)

        if contents['checksum'] != gen_checksum:
            raise ParsingException, 'Checksum is incorrect! Provided: %d, generated: %d' % (contents['checksum'], gen_checksum)

        # Create response packet object
        response = responses.getPacket(contents['payload_id'])

        # Populate data
        response.parseHeaderFlags(contents['flags'])
        response.setPayloadId(contents['payload_id'])
        response.parsePayload(contents['payload'])
        response.validate()

        return response


class ParsingException(Exception):
    pass
