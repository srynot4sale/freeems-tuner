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


import wx
import wx.grid as grid
import comms
import protocols
import logging
import datetime


logger = logging.getLogger('gui.commsDiagnostics')

class commsDiagnostics(grid.Grid):
    
    conn = None
    row = 0

    def __init__(self, parent):
        grid.Grid.__init__(self, parent)

        self.CreateGrid(1, 4)
        self.SetRowLabelSize(50)
        self.SetColLabelValue(0, 'Time')
        self.SetColSize(0, 110)
        self.SetColLabelValue(1, 'Flags')
        self.SetColSize(1, 45)
        self.SetColLabelValue(2, 'Id')
        self.SetColSize(2, 75)
        self.SetColLabelValue(3, 'Payload')
        self.SetColSize(3, 530)

        self.SetDefaultCellFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.conn = comms.getConnection()
        self.conn.bindSendWatcher(self.printSentPacket)
        self.conn.bindRecieveWatcher(self.printRecievedPacket)


    def printSentPacket(self, request):
        '''Print sent packet to grid'''
        self.insertRow(request)

    
    def printRecievedPacket(self, response):
        '''Print received packet to grid'''
        self.insertRow(response)


    def insertRow(self, packet):
        '''Insert row into grid'''
        time = datetime.datetime.time(datetime.datetime.now())
        header = self.getHeaderFlags(packet)
        payload_hex = packet.getPayloadBytes()
        
        #Format stuff before printing
        payload_id = packet.getPayloadIdInt()
        payload_id_hum = protocols.getProtocol().getPacketType(payload_id)
        payload_hex_hum = self.formatPayloadHex(payload_hex)

        self.AppendRows()
        self.SetCellValue(self.row, 0, str(time))
        self.SetCellValue(self.row, 1, str(header))
        self.SetCellValue(self.row, 2, str(payload_id) + ":" + payload_id_hum)
        self.SetCellValue(self.row, 3, payload_hex_hum)

        # Make sure entire row is visible
        if self.GetCellOverflow(self.row, 3):
            lines = payload_hex_hum.count('\n') + 1
            print lines
            self.SetRowSize(self.row, (lines * 15) + 3)

        self.MakeCellVisible(self.row + 1, 1)
        self.ForceRefresh()

        self.row += 1


    def formatPayloadHex(self, data):
        output = ''
        bytes = []
        i = 0

        for raw_hex in data:
            # If end of line
            if i % 16 == 0:
                
                # If not first line, add string to end
                if i > 0:
                    output += self.getASCII(bytes)+'\n'
                    bytes = []

                # Get offset and pad with 0's
                offset = hex(i)[2:5].rjust(4, '0')
                
                output += offset+':  '
                
            i += 1
            output += hex(raw_hex)[2:5].rjust(2, '0')
            output += ' '
            bytes.append(raw_hex)

            if i % 8 == 0 and i % 16:
                output += " "

        # Pad the end
        while i % 16:
            if not i % 8:
                output += ' '
            output += '-- '
            i += 1

        output += self.getASCII(bytes)
            
        return output


    def getASCII(self, output):
        ascii = "  "
        
        # Replace hex that can't translate to ASCII with an underscore (0x5F)
        for j, str in enumerate(output):

            if str > 128 or str < 20:
                ascii += '_'
            else:
                ascii += chr(str)
        
        return ascii


    def getHeaderFlags(self, packet):
        '''Retrieve noterised version of flag bits'''
        ascii = str()

        if packet.hasHeaderProtocolFlag():
            ascii += 'P'
        else:
            ascii += 'I'

        if packet.hasHeaderLengthFlag():
            ascii += 'L'

        if packet.hasHeaderAckFlag():
            ascii += 'A'

        return ascii
