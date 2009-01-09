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

import libs.thread, comms.protocols as protocols


class thread(libs.thread.thread):
    '''
    Thread for handling the receive queue and
    abstract -> raw packet processing
    '''

    # Comms plugin that created this thread
    comms = None

    # Buffer of packet request to process into packet classes
    _buffer = []


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
        self._debug('Received buffer: %s' % ','.join(protocols.toHex(buffer)))
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
        self._debug('Processing buffer')
        self._buffer = []
        return
#        self.comms.queuePacket(packet.getPacketRawBytes())
        # Check for any complete packets
#        cache = copy.copy(self._buffer)

#        try:
#            packet = protocol.processRecieveBuffer(self._buffer)
#        except Exception, msg:
#            self._debug('processReceiveBuffer failed to parse packet from buffer: %s' % join(protocols.toHex(cache)), msg)
#            self._buffer = []
#            continue
        
#        if not packet:
#            continue

#                logger.debug('Packet received by test comms connection: %s' % packet.getPacketHex())

#                for watcher in self._receive_watchers:
#                    watcher(packet)
