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

import copy, types, threading

import libs.thread, comms.protocols as protocols, __init__ as protocol, packet as packetlib, responses


class thread(libs.thread.thread):
    '''
    Thread for handling the receive queue and
    abstract -> raw packet processing
    '''

    # Comms plugin that created this thread
    comms = None

    # Thread safe lock for protecting the buffer
    _buffer_lock = None

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
        libs.thread.thread.__init__(self)

        self._setup(name, controller)
        self.comms = comms

        # Set up buffer lock
        self._buffer_lock = threading.Lock()

        self._debug('Receive thread created')
        self.start()

    
    def received(self, buffer):
        '''
        Add to buffer and wake thread
        '''
        self._bufferAppend(buffer)
        #self._debug('Received %d bytes of buffer' % len(buffer))
        self.wake()


    def _bufferAppend(self, binary):
        '''
        Append binary to buffer safely
        '''
        self._buffer_lock.acquire()
        self._buffer.append(binary)
        self._buffer_lock.release()


    def _bufferPop(self):
        '''
        Pop oldest binary string off buffer safely,
        or return false if buffer empty
        '''
        self._buffer_lock.acquire()

        if len(self._buffer):
            oldest = self._buffer.pop(0)
        else:
            oldest = False

        self._buffer_lock.release()

        return oldest


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
        packet = True

        while True:
            # Check for any complete packets
            cache = self._bufferPop()

            # If no more buffer
            if cache == False:
                # If we have also processed all the cache
                if len(self._cache) == 0:
                    break
                # If last scan did not find a packet
                elif not packet:
                    break
                else:
                    cache = ''

            self._cache += cache

            try:
                packet = self._processBuffer()
            except IgnorableParsingException, msg:
                # Report nothing
                continue
            except ParsingException, msg:
                self._error('processReceiveBuffer could not parse buffer. %s' % msg)
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
        try:
            index = -1

            # Remove any buffer before the first start byte
            if self._cache[0] != protocol.START_BYTE:
                index = self._cache.find(protocol.START_BYTE, 1)
                if index >= 0:
                    if self._cache[:index] == protocol.END_BYTE:
                        raise IgnorableParsingException, 'Ignorable packet found in buffer before start byte %s' % protocols.toHex(self._cache[:index])
                    else:
                        raise ParsingException, 'Bad/incomplete packet found in buffer before start byte %s' % protocols.toHex(self._cache[:index])

        except ParsingException:
            # Catch parsing eceptions and tidy up the buffer
            if index >= 0:
                self._cache = self._cache[index:]
            else:
               self._cache = ''
            
            raise

        # If another start byte in buffer before next end byte
        s = self._cache.find(protocol.START_BYTE, 1)
        if s >= 0:

            # Find end byte before second start byte
            e = self._cache.find(protocol.END_BYTE, 1, s)

            # If no end byte before second byte, incomplete packet
            if e == -1:
                # Remove from buffer
                # Nasty try/raise/except/raise construct here so we can wipe the cache
                try:
                    if self._cache[:s] == protocol.START_BYTE:
                        raise IgnorableParsingException, 'Ignorable packet found in buffer missing end byte %s' % protocols.toHex(self._cache[:s])
                    else:
                        raise ParsingException, 'Bad/incomplete packet found in buffer missing end byte %s' % protocols.toHex(self._cache[:s])

                except ParsingException:
                    # Tidy up buffer
                    self._cache = self._cache[s:]

                    raise

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

        if not len(packet):
            raise IgnorableParsingException, 'Packet is empty'

        if len(packet) < 4:
            raise ParsingException, 'Packet does not contain required information. Packet content: %s' % protocols.toHex(packet)

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
            raise ParsingException, 'Checksum is incorrect! Provided: %d, generated: %d, packet: [%s]' % (ord(contents['checksum']), ord(gen_checksum), protocols.toHex(packet))

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

class IgnorableParsingException(ParsingException):
    pass
