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

import types

import libs.config


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


def getProtocol(controller):
    '''
    Return protocol, and if none exists - load
    '''
    return loadDefault(controller)


def loadDefault(controller):
    '''
    Load default protocol
    '''

    # Load config
    def_protocol = libs.config.get('Protocol', 'default')
    version = libs.config.get('Protocol', 'default_version')

    # Should end up in the format:
    #   'comms.protocols.FreeEMS.0_17,
    #
    # Which would refer to the file:
    #   $cwd/comms/protocols/FreeEMS/0_17.py

    path = 'comms.protocols.'+def_protocol+'.'+version

    controller.log('comms.protocol', 'DEBUG', 'Loading protocol plugin: %s' % path)

    # Dynamically import
    return __import__(path, globals(), locals(), version)


def to8bit(value, length = None):
    '''Convert a var to an 8 bit list'''
    converted = []

    if not isinstance(value, list):
        if isinstance(value, str):
            value = list(value)
        elif isinstance(value, int):
            value = [value]
        else:
            raise TypeError, 'Unexpected type recieved'

    for byte in value:
        if isinstance(byte, str):
            byte = ord(byte)

        if byte > 256:
            converted.append(byte >> 8)
            byte &= 0xFF

        converted.append(byte)

    # If a specified length is required
    if length and len(converted) < length:
        padding = list(range(0, (length - len(converted))))
        converted = padding + converted

    elif length and len(converted) > length:
        raise IndexError, 'Bytes larger than specified length'
        
    return converted


def from8bit(value):
    '''Convert an 8 bit list to a var'''
    converted = 0
    i = 0

    if not isinstance(value, list):
        raise TypeError, 'Unexpected type recieved'

    for num in reversed(value):
        if i < 1:
            converted += num
        else:
            converted += num * (i * 256)
        i += 1               #No i++ in Python? Really?
        
    return converted


def toHex(bytes):
    '''Convert a list of bytes to a list of hex strings'''
    raw_hex = []
    
    for byte in bytes:
        byte = hex(byte).upper().replace('X','x')
        
        if len(byte) == 3:
            byte = '0x0'+byte[-1]

        raw_hex.append(byte)
            
    return raw_hex


class interface:
    '''Base class for all protocol plugins'''

    def isConnected(self):
        pass

