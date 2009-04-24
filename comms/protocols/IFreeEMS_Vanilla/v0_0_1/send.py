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

import libs.thread


class thread(libs.thread.thread):
    '''
    Thread for handling the send queue and
    abstract -> raw packet processing
    '''

    # Comms plugin that created this thread
    comms = None

    # Buffer of packet request to process into raw bytes
    _buffer = []


    def __init__(self, name, controller, comms):
        '''
        Sets up threading stuff
        '''
        libs.thread.thread.__init__(self)

        self._setup(name, controller)
        self.comms = comms

        self._debug('Send thread created')
        self.start()

    
    def send(self, packet):
        '''
        Add packet object to buffer and wake thread
        '''
        self._buffer.append(packet)
        self.wake()


    def run(self):
        '''
        Loop through buffer and process into raw packets
        '''
        while self._alive:
            # If buffer non-empty, process
            if len(self._buffer):
                self._process(self._buffer.pop(0))

            # Otherwise wait to be awoken
            else:
                self._checkBlock()

        self._final()


    def _process(self, packet):
        '''
        Processes packet to raw bytes and sends to
        comms thread
        '''
        self.comms.triggerSendWatchers(packet)
        packet.prepare()

        self.comms.queuePacket(packet)
