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


import threading, datetime, time
import libs.thread, comms, protocols


class app(libs.thread.thread):
    '''
    Controls program logic and manages threads
    '''

    # Queue of actions to perform, use .action() to add an action
    _actionQueue = []

    
    def __init__(self):
        '''
        Initialisation routine
        '''

        self._setup('controller.app', self)
        self._debug('Starting controller thread')

        # Make this thread run as a daemon, which means
        # it will continue to exist after the parent thread
        # is closed. This will let the controller wait for the
        # other threads to gracefully close and continue logging
        # until they are all shutdown.
        self.daemon = True

        # Setup default comms thread
        comms.createConnection(self)

        # Load default hardware interface protocol
        # TODO: comms should load protocol
        protocols.loadDefault()

        # Start threading!
        self.start()

    
    def action(self, action, data = None):
        '''
        Wakes up this thread and performs an action
        '''
        self._actionQueue.append((action, data))

        self.wake()


    def log(self, section, severity, message, data = None):
        '''
        Application logging
        '''
        time = datetime.datetime.now()

        self.action('Log', (time, section, severity, message, data))


    def shutdown(self):
        '''
        Simply public access to shutdown routine
        '''
        self.action('Shutdown')


    def run(self):
        '''
        Perform controller logic
        '''
        # Continue running until no other threads are left except
        # this one and the main thread
        while threading.activeCount() > 2:

            # If no actions in queue, block
            if not self._actionQueue:
                self._checkBlock()
            
            # Loop through actions
            while self._actionQueue:
                
                # Grab first action in queue
                (action, data) = self._actionQueue.pop(0)
                
                # Run actions internal method
                action = '_action'+action
                getattr(self, action)(data)

        # Print one last log message
        # Instead of _final() like other threads, which would just
        # create a log action that would never get done
        self._actionLog( (datetime.datetime.now(), 'controller.app', 'DEBUG', 'Shutting down controller thread', None) )

    
    def _actionLog(self, data = None):
        '''
        Prints log to console (for now)
        '''
        (time, section, severity, message, data) = data

        time = time.strftime('%H:%M:%S')

        if data == None:
            data = ''

        print '%s %-15s %s %s %s' % (time, section, severity, message, data)


    def _actionShutdown(self, data = None):
        '''
        Shutdown all threads in app
        '''
        self._debug('Performing shutdown action')

        # Shutdown threads
        for thread in threading.enumerate():
            
            if not isinstance(thread, threading._MainThread):
                thread.exit()
