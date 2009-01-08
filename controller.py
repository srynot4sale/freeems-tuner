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


import threading, datetime, time
import libs.thread, comms

class app(libs.thread.thread):
    '''
    Controls program logic and manages threads
    '''

    # Queue of actions to perform, use .action() to add an action
    _actionQueue = []

    # Queue of low priority actions to perform, use .actionLowPriority()
    _actionQueueLowPriority = []

    # Queue of blocking actions to be performed, use .actionBlocking()
    _actionQueueBlocking = []

    # Blocking action data
    _actionBlockingLastId = 0
    _actionBlockingBlocks = {}
    _actionBlockingData = {}

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

        # Start threading!
        self.start()

    
    def action(self, action, data = None):
        '''
        Wakes up this thread and performs an action
        
        Action is a string that refers to a method:

        If no "." in the string, its refers to a method
        in this class and will be prepended with _action

        If the string contains at least one ".", it refers
        to an actions module or submodule of and a method e.g.
        config.load = actions.config.load() or
        serial.receive.translate = actions.receive.translate()
        '''
        self._actionQueue.append((action, data))
        self.wake()


    def actionLowPriority(self, action, data = None):
        '''
        Wakes up this thread and performs a low priority action
        after all the higher priority actions have finished.

        See self.action() for more details
        '''
        self._actionQueueLowPriority.append((action, data))
        self.wake()

    
    def actionBlocking(self, action, data = None):
        '''
        Wakes up this thread and performs an action and does
        not return until the action has been completed, effectively
        blocking the calling thread.

        See self.action() for more details
        '''
        # Get unique blocking id
        self._actionBlockingLastId += 1
        id = self._actionBlockingLastId

        # Create block
        block = self._actionBlockingBlocks[id] = threading.Event()
        
        # Queue action and wake controller
        self._actionQueueBlocking.append((action, data, id))
        self.wake()

        # Wait for block
        block.wait()

        # Get data
        data = self._actionBlockingData[id]

        # Remove block and data
        del self._actionBlockingBlocks[id]
        del self._actionBlockingData[id]

        # Return data
        return data


    def log(self, section, severity, message, data = None):
        '''
        Application logging
        '''
        time = datetime.datetime.now()

        self.actionLowPriority('Log', (time, section, severity, message, data))


    def shutdown(self):
        '''
        Simply public access to shutdown routine
        '''
        self.action('Shutdown')


    def run(self):
        '''
        Perform controller logic
        '''
        # Queue sizes (for logging)
        actionQueueSize = 0
        actionQueueLowPrioritySize = 0
        actionQueueBlockingSize = 0
        log_actions = False

        # Continue running until no other threads are left except
        # this one and the main thread
        while threading.activeCount() > 2:

            # If no actions in queue, block
            if not self._actionQueue:
                self._checkBlock()
            
            # Loop through actions
            while self._actionQueue or self._actionQueueLowPriority or self._actionQueueBlocking:
                
                # Log the size of the queues if they have changed
                if actionQueueSize != len(self._actionQueue) or actionQueueLowPrioritySize != len(self._actionQueueLowPriority) or actionQueueBlockingSize != len(self._actionQueueBlocking):
                    log_actions = True

                actionQueueSize = len(self._actionQueue)
                actionQueueLowPrioritySize = len(self._actionQueueLowPriority)
                actionQueueBlockingSize = len(self._actionQueueBlocking)

                if log_actions:
                    log_actions = False
                    self._log('DEBUG', 'Size of action queues, blocking: %s, actions: %s, low-priority: %s' %
                                (actionQueueBlockingSize, actionQueueSize, actionQueueLowPrioritySize))
                
                # Actions in _actionQueueBlocking are top priority so always
                # get done before low priority actions
                if self._actionQueueBlocking:
                    queue = self._actionQueueBlocking
                    actionQueueBlockingSize -= 1
                elif self._actionQueue:
                    queue = self._actionQueue
                    actionQueueSize -= 1
                else:
                    queue = self._actionQueueLowPriority
                    actionQueueLowPrioritySize -= 1
                
                # Grab oldest action in queue
                action = queue.pop(0)

                # Split data into relevant chunks
                if len(action) == 3:
                    (action, data, block_id) = action
                else:
                    block_id = None
                    (action, data) = action
                
                # Log action
                if action != 'Log':
                    self._log('DEBUG', 'Performing %s action' % action)

                # Check where action is located
                if '.' in action:
                    # Run method in action module
                    loc = action.rfind('.')
                    module = action[0:loc]
                    method = action[loc+1:]
                    action_method = getattr(__import__(module, globals(), locals(), 'actions'), 'actions')
                    result = getattr(action_method, method)(self, data).run()
                else:
                    # Run actions internal method
                    action = '_action'+action
                    result = getattr(self, action)(data)

                # Save result and release lock for blocking actions
                if block_id:
                    self._actionBlockingData[block_id] = result
                    self._actionBlockingBlocks[block_id].set()

        # Print one last log message instead of running _final()
        # like other threads, which would just create a log action
        # that would never got run
        self._log('DEBUG', 'Shutting down controller thread')

    
    def _log(self, severity, message, data = None):
        '''
        Internal controller logging, only to be run from run() method
        '''
        time = datetime.datetime.now()

        self._actionLog((time, 'controller.app', severity, message, data))


    def _actionLog(self, data = None):
        '''
        Prints log to console (for now)
        '''
        (time, section, severity, message, data) = data

        time = time.strftime('%H:%M:%S')

        if data == None:
            data = ''

        print '%s %-25s %s %s %s' % (time, section, severity, message, data)


    def _actionShutdown(self, data = None):
        '''
        Shutdown all threads in app
        '''
        # Shutdown threads
        for thread in threading.enumerate():
            
            if not isinstance(thread, threading._MainThread):
                thread.exit()

