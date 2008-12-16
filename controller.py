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


import threading, logging
import comms, protocols, gui


class app(threading.Thread):
    '''
    Controls program logic and manages threads
    '''

    # Keep-alive flag, thread will terminate when not True
    _alive = True

    # Blocking object to keep thread idle between actions
    _idleBlock = None

    # Queue of actions to perform, use .action() to add an action
    _actionQueue = []


    def __init__(self):
        '''
        Initialisation routine
        '''

        logger = logging.getLogger('controller.app')
        logger.debug('Controller class started')

        # Setup default comms thread
        comms.createConnection()

        # Load default hardware interface protocol
        protocols.loadDefault()

        threading.Thread.__init__(self, name = 'controller.app')
        self.start()


    def shutdown(self):
        '''
        Start shutdown routine
        '''
        self.action('Shutdown')


    def _checkIdleBlock(self):
        '''
        Starts blocking using self._idleBlock
        The thread will remained blocked (halted)
        until another thread runs the action() method
        '''
        if self._idleBlock == None:
            self._idleBlock = threading.Event()

        logger = logging.getLogger('controller.app')
        logger.debug('Waiting')

        self._idleBlock.wait()

    
    def action(self, action, data = None):
        '''
        Wakes up this thread and performs an action
        '''
        self._actionQueue.append((action, data))

        # Just in case we get here before creating the block
        if self._idleBlock:
            self._idleBlock.set()


    def run(self):
        '''
        Perform controller logic
        '''
        while self._alive:

            # If no actions in queue, block
            if not self._actionQueue:
                self._checkIdleBlock()

            # Loop through actions
            while self._actionQueue:

                # Grab first action in queue
                (action, data) = self._actionQueue.pop(0)

                # Run actions internal method
                action = '_action'+action
                getattr(self, action)(data)


    def exit(self):
        pass

    def _actionShutdown(self, data = None):
        '''
        Shutdown all threads in app
        '''
        #logger = logging.getLogger('controller.app')
        #logger.debug('Shutdown action performed')

        # Shutdown this thread 
        self._alive = False

        # Shutdown other threads
        for thread in threading.enumerate():
            
            # Runs thread.__del__()
            #del thread
            if not isinstance(thread, threading._MainThread):
                #del thread
                thread.exit()
