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

    # Buffer being currently processed
    _cache = ''

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
        self._cache = ''
        packet = True

        # Check for any complete packets
        while self._buffer or self._cache:
            
            if len(self._buffer):
                self._cache += self._buffer.pop(0)
            elif not packet:
                # Hopefully fix a race condition where a
                # unfinished packet at the end of the
                # buffer will cause an endless loop
                break

            try:
                packet = self._processBuffer()
            except ParsingException, msg:
                self._error('processReceiveBuffer could not parse buffer. %s' % msg, protocols.toHex(self._cache))
                continue
            except Exception, msg:
                # Program error, clean buffer
                raise
                self._error('processReceiveBuffer threw exception, wiping buffer: %s' % msg, protocols.toHex(self._cache))
                self._cache = ''
                continue
        
            if not packet:
                continue

            # Tell controller to handle newly received packets
            self.queue.append(packet)
    
            data = { 'comms': self.comms, 'queue': self.queue }
            self._controller.action('comms.handleReceivedPackets', data)
   

    def _processBuffer(self):
        '''
        Check for any incoming packets and return if found

        - Removing anything before first START_BYTE
        - Check for END_BYTE
        - Loop though buffer copy
            - If complete packet found, remove length from buffer
            - If incomplete packet, leave buffer and try again later
        '''
        # Remove any buffer before the first start byte
        if self._cache[0] != protocol.START_BYTE:
            if protocol.START_BYTE not in self._cache:
                tmp = self._cache
                self._cache = ''
            else:
                index = self._cache.index(protocol.START_BYTE)
                tmp = self._cache[:index]
                self._cache = self._cache[index:]

            raise ParsingException, 'Bad/incomplete packet found in buffer before start byte %s' % protocols.toHex(tmp)

        # If no end byte in buffer, return as it must not contain a complete packet
        if protocol.END_BYTE not in self._cache:
            return

        # Grab packet from buffer (minus start and end bytes)
        end = self._cache.index(protocol.END_BYTE)
        packet = self._cache[1:end] 

        # Clear processed buffer
        self._cache = self._cache[end+1:]

        # Process packet
        return self._processIncomingPacket(packet)


    def _processIncomingPacket(self, packet):
        '''
        Takes a raw packet, checks it and returns the correct packet class
        '''
        # Check for special bytes n packet that shouldn't be there
        if protocol.START_BYTE in packet or protocol.END_BYTE in packet:
            raise ParsingException, 'Unescaped bytes found in packet: %s' % protocols.toHex(packet)

        # Process escapes
        processed = 0
        while protocol.ESCAPE_BYTE in packet[processed:]:
            i = packet.index(protocol.ESCAPE_BYTE, processed)
            processed = i+1

            # Convert escaped byte to an integer to XOR, and then convert back to a string
            unescaped = chr(ord(packet[i+1]) ^ 0xFF)

            if unescaped in protocol.SPECIAL_BYTES:
                packet = packet[:i] + unescaped + packet[i+2:]
            else:
                raise ParsingException, 'Wrongly escaped byte found in packet (%s): %s' % (hex(ord(unescaped)), protocols.toHex(packet))

        # Split up packet
        contents = {
                'flags':        packet[0],
                'payload_id':   protocols.shortFrom8bit(packet[1:3]),
                'payload':      packet[3:-1],
                'checksum':     packet[-1]
        }

        # Check checksum
        gen_checksum = packetlib.getChecksum(packet[:-1])

        if contents['checksum'] != gen_checksum:
            raise ParsingException, 'Checksum is incorrect! Provided: %d, generated: %d' % (ord(contents['checksum']), ord(gen_checksum))

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
