#   Copyright 2008, 2009 Aaron Barnes
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

import struct

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


def shortFrom8bit(value):
    '''
    Get an unsigned short from a 8 bit string
    '''
    return struct.unpack('>H', value)[0]


def intFrom8bit(value):
    '''
    Get an unsigned int from a 8 bit string
    '''
    return struct.unpack('>I', value)[0]


def longFrom8bit(value):
    '''
    Get an unsigned long from a 8 bit string
    '''
    return struct.unpack('>L', value)[0]


def shortTo8bit(value):
    '''
    Convert an unsigned short to a 8 bit string
    '''
    return struct.pack('>H', value)


def intTo8bit(value):
    '''
    Convert an unsigned int to a 8 bit string
    '''
    return struct.pack('>I', value)


def longTo8bit(value):
    '''
    Convert an unsigned long to a 8 bit string
    '''
    return struct.pack('>L', value)


def toHex(bytes):
    '''
    Convert a string to a human readable hex string
    '''
    hexlist = []
    
    for byte in bytes:
        byte = hex(ord(byte)).upper().replace('X','x')
        
        if len(byte) == 3:
            byte = '0x0'+byte[-1]

        hexlist.append(byte)

    return ','.join(hexlist)
