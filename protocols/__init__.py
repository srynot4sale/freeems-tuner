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


# Generic protocol constants
ZEROS = 0x00    # No bits   = 0
BIT0  = 0x01	# 1st bit	= 1		
BIT1  = 0x02	# 2nd bit	= 2		
BIT2  = 0x04	# 3rd bit	= 4		
BIT3  = 0x08	# 4th bit	= 8		
BIT4  = 0x10	# 5th bit	= 16	
BIT5  = 0x20	# 6th bit	= 32	
BIT6  = 0x40	# 7th bit	= 64	
BIT7  = 0x80	# 8th bit	= 128	


# Currently used protocol
protocol = None


def getProtocol():
    '''Return protocol, and if none exists - load'''
    if not protocol:
        loadDefault()

    return protocol


def loadDefault():
    '''Load default protocol'''

    # Load config
    def_protocol = config.load('Protocol', 'default')
    version = config.load('Protocol', 'default_version')

    # Should end up in the format:
    #   'protocols.FreeEMS.0_17,
    #
    # Which would refer to the file:
    #   $cwd/protocols/FreeEMS/0_17.py
    #
    path = 'protocols.'+def_protocol+'.'+version

    logger = logging.getLogger('protocols')
    logger.info('Loading protocol module: %s' % path)

    # Dynamically import
    global protocol
    protocol = __import__(path, globals(), locals(), 'protocol').protocol()


class interface:
    '''Base class for all protocol plugins'''

    def isConnected(self):
        pass

