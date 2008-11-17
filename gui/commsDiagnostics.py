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
        self.SetColSize(2, 180)
        self.SetColLabelValue(3, 'Payload')
        self.SetColSize(3, 530)

        self.SetDefaultCellFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.conn = comms.getConnection()
        self.conn.bindSendWatcher(self.printSentPacket)
        self.conn.bindRecieveWatcher(self.printRecievedPacket)


    def printSentPacket(self, request):
        #Get stuff to print
        time = datetime.datetime.time(datetime.datetime.now())
        header = request.getHeaderFlags()
        payload_hex = request.getPayloadHex()
        
        #Format stuff before printing
        payload_id = request.getPayloadIdInt()
        payload_id_hum = protocols.getProtocol().getPacketType(payload_id)
        payload_hex_hum = self.formatPayloadHex(payload_hex)

        self.AppendRows()
        self.SetCellValue(self.row, 0, str(time))
        self.SetCellValue(self.row, 1, str(header))
        self.SetCellValue(self.row, 2, str(payload_id) + ":" + payload_id_hum)
        self.SetCellValue(self.row, 3, payload_hex_hum)
        self.MakeCellVisible(self.row + 1, 1)
        self.ForceRefresh()

        self.row += 1

    
    def printRecievedPacket(self, request):

        time = datetime.datetime.time(datetime.datetime.now())
        header = 'rec'
        raw_hex = []

        for byte in request:
            hex_byte = hex(byte).upper().replace('X','x')

            if len(hex_byte) < 4:
                hex_byte = '0x0'+hex_byte[-1]

            raw_hex.append(hex_byte)


        raw_hex = ','.join(raw_hex)

        self.AppendRows()

        self.SetCellValue(self.row, 0, str(time))
        self.SetCellValue(self.row, 1, str(header))
        self.SetCellValue(self.row, 3, str(raw_hex))
        
        self.MakeCellVisible(self.row + 1, 1)
        self.ForceRefresh()

        self.row += 1


    def formatPayloadHex(self, data):
        seperator = False
        output = ""
        i = 0
        for raw_hex in data:
            if not i % 16 and i > 0:
                output += self.getASCII(output)
                output += "\n"
                offset = "%X" % i               #decimal to hex
                
                #Pad offset with zeros
                while len(offset) < 4:          
                    offset = offset[::-1]       #reverse string
                    offset += "0"               #add zero to "beginning" of string
                    offset = offset[::-1]       #reverse string
                output += offset
                output += ":  "
                
            elif not i % 16:
                output += "0000:  "
                
            i += 1
            output += str(raw_hex)[2:4]
            output += " "
            seperator = False
            if not i % 8 and i % 16:
                output += " "
                seperator = True

        first_row = False
        if i <= 16:
            first_row = True
        #Pad the end with asterisks
        while i % 16:
            if not i % 8 and not seperator:
                output += " "
            output += "** "
            i += 1

        output += self.getASCII(output)
            
        return output

    def getASCII(self, output):
        ascii = "  "
        i = len(output)        
        row_hex = output[i-49:i]
        row_hex = row_hex.replace('*', '')
        row_hex_list = row_hex.split()
        #Replace hex that can't translate to ASCII with an underscore (0x5F)
        for j, str in enumerate(row_hex_list):
            num = int(row_hex_list[j])
            if num > 80 or num < 20:
                row_hex_list[j] = "5F"
        row_hex = "".join(row_hex_list)
        ascii += row_hex.decode("hex")
        
        return ascii

