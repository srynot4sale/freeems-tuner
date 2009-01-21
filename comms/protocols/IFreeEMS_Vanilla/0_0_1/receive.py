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


STATE_NOT_PACKET            = 0
STATE_ESCAPE_BYTE           = 1
STATE_IN_PACKET             = 2


class thread(libs.thread.thread):
    '''
    Thread for handling the receive queue and
    abstract -> raw packet processing
    '''

    # Comms plugin that created this thread
    comms = None

    # Buffer of packet request to process into packet classes
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
        self._buffer.extend(buffer)
        self._debug('Received %d bytes of buffer' % len(buffer))
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
        '''
        # Check for any complete packets
        cache = copy.copy(self._buffer)

        while self._buffer:
            try:
                packet = self._processReceiveBuffer(self._buffer)
            except Exception, msg:
                self._debug('processReceiveBuffer threw exception (%s) while trying to parse packet from buffer so resetting buffer' % protocols.toHexString(cache), msg)
                self._buffer = []
                continue
        
            if not packet:
                continue

            # Tell controller to handle newly received packets
            self.queue.append(packet)
    
            data = { 'comms': self.comms, 'queue': self.queue }
            self._controller.action('comms.handleReceivedPackets', data)

        return
   

    def _processReceiveBuffer(self, buffer):
        '''
        Check for any incoming packets and return if found

        - Keep removing bytes until START_BYTE found
        - Check for END_BYTE
        - Loop though buffer copy
            - If complete packet found, remove length from buffer
            - If incomplete packet, leave buffer and try again later
        '''
        # Remove any buffer before the first start byte
        bad_bytes = []
        while len(buffer) and buffer[0] != protocol.START_BYTE:
            # Remove byte and append to bad_buffer
            bad_bytes.append(buffer.pop(0))

        if len(bad_bytes):
            self._debug('Bad/incomplete packet found in buffer before start byte: %s' % protocols.toHexString(bad_bytes))
            bad_bytes = []

        # If no buffer left or no end byte in buffer, return
        if not len(buffer) or protocol.END_BYTE not in buffer:
            return

        # Begin state control machine :-)
        state = STATE_NOT_PACKET
        packet = []
        index = 0

        # Loop through buffer_copy
        buffer_copy = copy.copy(buffer)

        for byte in buffer_copy:

            # Keep track of how many bytes we have processed
            index += 1

            # If have not started a packet yet check for start_byte
            if state == STATE_NOT_PACKET:
                # If not a start byte, we should never have got here
                if byte != protocol.START_BYTE:
                    self._debug('Should never have got here, expecting a start byte 0x%X' % byte)
                    continue
                # Otherwise, start packet
                else:
                    state = STATE_IN_PACKET
                    packet.append(protocol.START_BYTE)
                    continue

            # We are in a packet, save byte unless we find an end byte
            elif state == STATE_IN_PACKET:
                if byte == protocol.END_BYTE:
                    state = STATE_NOT_PACKET
                    packet.append(protocol.END_BYTE)
                    break
                elif byte == protocol.ESCAPE_BYTE:
                    state = STATE_ESCAPE_BYTE
                    continue
                else:
                    packet.append(byte)
                    continue

            # If we are in escape mode (previous byte was an escape), escape byte
            elif state == STATE_ESCAPE_BYTE:
                esc_byte = byte ^ 0xFF
                
                # Check it is a legitimately escaped byte
                if esc_byte in (protocol.START_BYTE, protocol.ESCAPE_BYTE, protocol.END_BYTE):
                    packet.append(esc_byte)
                    state = STATE_IN_PACKET
                    continue
                else:
                    self._debug('Wrongly escaped byte found in buffer: 0x%X' % byte)
                    continue
        
        # Check if we have a complete packet
        if len(packet) and state == STATE_NOT_PACKET:

            # Remove this byte from buffer as it has been processed
            del buffer[0:index]
            return self._processIncomingPacket(packet)


    def _processIncomingPacket(self, packet):
        '''
        Takes a raw packet, checks it and returns the correct packet class
        '''
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
        contents['payload_id'] = payload_id = protocols.from8bit(packet[index:index+2])
        index += 2

        # Grab payload
        contents['payload'] = payload = packet[index:(len(packet) - 2)]
        index += len(payload)

        # Grab checksum
        contents['checksum'] = checksum = packet[index]
        index += 1

        # Check checksum
        gen_checksum = packetlib.getChecksum(packet[1:index-1])

        if checksum != gen_checksum:
            self._debug('Checksum is incorrect! Provided: %d, generated: %d' % (checksum, gen_checksum))
            return False

        # Just double check we only have one byte left
        if index != (len(packet) - 1):
            self._debug('Packet incorrectly processed, %d bytes left' % (len(packet) - 1 - index))
            return False

        # Create response packet object
        if flags & protocol.HEADER_IS_PROTO:
            response = responses.getProtocolPacket(payload_id)
        else:
            response = responses.getFirmwarePacket(payload_id)

        # Populate data
        response.parseHeaderFlags(contents['flags'])
        response.setPayloadId(contents['payload_id'])
        response.parsePayload(contents['payload'])
        response.validate()

        return response
