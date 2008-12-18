#   Copyright 2008 Aaron Barnes
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


import threading


class thread(threading.Thread):
    '''
    Thread base class including tuner specific logic and methods
    '''

    # Reference to the app controller
    _controller = None
    
    # Keep-alive flag, thread will terminate when not True
    _alive = True

    # Blocking object to keep thread idle between actions
    _block = None

    
    def wake(self):
        '''
        Used for waking the thread if its blocking
        '''
        if self._block:
            self._block.set()


    def exit(self):
        '''
        This method is called on program shutdown and should
        wake the thread and alert the run() method to stop processing
        '''
        self._alive = False

        self.wake()


    def _setup(self, name, controller):
        '''
        Sets up important stuff, should be run first in __init__()
        '''
        self._controller = controller
        self.name = name

        threading.Thread.__init__(self, name = name)


    def _checkBlock(self):
        '''
        Starts blocking using self._block
        The thread will remained blocked (halted)
        until another thread runs the wake() method
        '''
        if self._block == None:
            self._block = threading.Event()
        
        self._block.wait()
        self._block.clear()

    
    def _debug(self, message, data = None):
        '''
        Sends a debug log message to the controller
        '''
        self._controller.log(
                self.name,
                'DEBUG',
                message,
                data
        )
