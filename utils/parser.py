# FreeEMS - the open source engine management system
#
# Copyright 2009 Fred Cooke, Aaron Barnes
#
# This file is part of the FreeEMS project.
#
# FreeEMS software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FreeEMS software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with any FreeEMS software.  If not, see http://www.gnu.org/licenses/
#
# We ask that if you make any changes to this file you email them upstream to
# us at admin(at)diyefi(dot)org or, even better, fork the code on github.com!
#
# Thank you for choosing FreeEMS to run your engine!


# Special byte definitions
ESCAPE_BYTE             = 0xBB
START_BYTE              = 0xAA
STOP_BYTE               = 0xCC
ESCAPED_ESCAPE_BYTE     = 0x44
ESCAPED_START_BYTE      = 0x55
ESCAPED_STOP_BYTE       = 0x33


import sys, os


def main():
    if len(sys.argv) == 1:
        print 'No argument supplied!! Please supply a file to parse.'
        sys.exit(2)
    elif len(sys.argv) != 2:
        print 'Wrong number of arguments!! Was %i should be 1...\n' % sys.argc - 1
        sys.exit(2)

    inputFile = open(sys.argv[1], 'rb');

    inputFile.seek(0, os.SEEK_END)
    length = inputFile.tell()
    inputFile.seek(0, os.SEEK_SET)
    print 'The length of file %s is %i\n\n' % (sys.argv[1], length)
    print 'Attempting to parse file...\n\n'

    # Statistic collection variables
    packets = 0
    charsDropped = 0
    badChecksums = 0
    goodChecksums = 0
    startsInsidePacket = 0
    totalFalseStartLost = 0
    doubleStartByteOccurances = 0
    strayDataBytesOccurances = 0
    escapeBytesFound = 0
    escapedStopBytesFound = 0
    escapedStartBytesFound = 0
    escapedEscapeBytesFound = 0
    escapePairMismatches = 0

    # Loop and state variables
    insidePacket = 0
    unescapeNext = 0
    processed = 0
    checksum = 0
    lastChar = 0
    currentPacketLength = 0

    # Iterate through the file char at a time
    while processed < length:
        processed += 1
        character = ord(inputFile.read(1))

        # Look for a start byte to indicate a new packet
        if character == START_BYTE:
            # If we are had already found a start byte
            if insidePacket:
                # Increment the counter
                startsInsidePacket += 1
                if currentPacketLength == 0:
                    doubleStartByteOccurances += 1
                    # print 'Double start byte occurred following packet number %i\n' % packets
                else:
                    totalFalseStartLost += currentPacketLength # remember how much we lost
                    strayDataBytesOccurances += 1
                    # print 'Stray data or unfinished packet found following packet number %n\n' % packets

            # Reset to us using it unless someone else was
            insidePacket = 1
            checksum = 0
            currentPacketLength = 0

        elif insidePacket:
            if unescapeNext:
                # Clear escaped byte next flag
                unescapeNext = 0

                if character == ESCAPED_ESCAPE_BYTE:
                    # Store and checksum escape byte
                    checksum += ESCAPE_BYTE
                    lastChar = ESCAPE_BYTE
                    escapedEscapeBytesFound += 1
                    currentPacketLength += 1
                elif character == ESCAPED_START_BYTE:
                    # Store and checksum start byte
                    checksum += START_BYTE
                    lastChar = START_BYTE
                    escapedStartBytesFound += 1
                    currentPacketLength += 1
                elif character == ESCAPED_STOP_BYTE:
                    # Store and checksum stop byte
                    checksum += STOP_BYTE
                    lastChar = STOP_BYTE
                    escapedStopBytesFound += 1
                    currentPacketLength += 1
                else:
                    # Otherwise reset and record as data is bad
                    insidePacket = 0
                    checksum = 0
                    currentPacketLength = 0
                    escapePairMismatches += 1

            elif character == ESCAPE_BYTE:
                # Set flag to indicate that the next byte should be un-escaped.
                unescapeNext = 1
                escapeBytesFound += 1
            elif character == STOP_BYTE:
                packets += 1

                # Bring the checksum back to where it should be
                checksum -= lastChar

                checksum = checksum % 256

                # Check that the checksum matches
                if checksum != lastChar:
                    badChecksums += 1
                    print 'Packet number %i ending of length %i at char number %i failed checksum! Received %i Calculated %i\n' % (packets, currentPacketLength, processed, lastChar, checksum)
                else:
                    goodChecksums += 1
                    #printf("Packet number %u ending of length %u at char number %u checked out OK! Received %u Calculated %u\n", packets, currentPacketLength, processed, lastChar, checksum);
                
                # Clear the state
                insidePacket = 0
                currentPacketLength= 0
                checksum = 0

            else:
                # If it isn't special checksum it!
                checksum += character
                lastChar = character
                currentPacketLength += 1
            
        else:
            # Do nothing : drop the byte
            charsDropped += 1
        
    

    print '\nData stream statistics :\n'

    print '\nPackets and checksums :\n'
    print '%i packets were found\n' % packets
    print '%i had good checksums\n' % goodChecksums
    print '%i had incorrect checksums\n' % badChecksums

    print '\nGeneral issues :\n'
    print '%i leading characters were dropped\n' % charsDropped
    print '%i false starts occurred\n' % startsInsidePacket
    print '%i double start bytes occurred\n' % doubleStartByteOccurances
    print '%i stray part packets occurred\n' % strayDataBytesOccurances
    print '%i chars lost from false starts \n' % totalFalseStartLost

    print '\nEscaped byte profile :\n'
    print '%i escape bytes were found\n' % escapeBytesFound
    print '%i escaped stop bytes were found\n' % escapedStopBytesFound
    print '%i escaped start bytes were found\n' % escapedStartBytesFound
    print '%i escaped escape bytes were found\n' % escapedEscapeBytesFound
    print '%i escape pairs were mismatched\n' % escapePairMismatches


if __name__ == "__main__":
    main()
