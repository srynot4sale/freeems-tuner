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


import config, logging


# Tuners comms connection
connection = None


def createConnection():
    '''Create comms connection'''
    loadDefault()


def getConnection():
    '''Get comms connection'''
    return connection


def loadDefault():
    '''Load default comms conenction'''

    # Fetch config data
    comms = config.load('Comms', 'default')
    path = 'comms.'+comms

    logger = logging.getLogger('comms')
    logger.info('Loading comms module: %s' % path)

    # Dynamically import
    global connection
    connection = __import__(path, globals(), locals(), 'connection').connection()


class interface:
    '''Base class for all comms plugins'''

    def isConnected(self):
        pass

    
    def connect(self):
        pass


    def disconnect(self):
        pass


    def bindSendWatcher(self, watcher):
        pass


    def bindRecieveWatcher(self, watcher):
        pass


    def send(self, packet):
        pass


class CommsException(Exception):
    pass


class CannotconnectException(CommsException):
    pass
