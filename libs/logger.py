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


import logging, config, data

LEVELS = {
    'debug':    logging.DEBUG,
    'info':     logging.INFO,
    'warning':  logging.WARNING,
    'error':    logging.ERROR,
    'critical': logging.CRITICAL
}

LOG_FILENAME = data.getPath()+'app.log'


def setup():

    global LEVELS, LOG_FILENAME

    # Get log level from config
    config_level = config.load('Logging', 'verboseness')
    level = LEVELS.get(config_level, logging.NOTSET)

    # Setup config
    base = logging.getLogger()
    base.setLevel(level)

    # Get log types from config
    if config.loadBool('Logging', 'to_file'):
        handler = logging.FileHandler(LOG_FILENAME, 'w')
        base.addHandler(handler)

    if config.loadBool('Logging', 'to_terminal'):
        handler = terminalHandler()
        base.addHandler(handler)

    base.debug('Logging set up')


# Logging handler for printing to terminal
class terminalHandler(logging.Handler):
    
    def emit(self, record):
        print record
