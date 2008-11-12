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

        self.CreateGrid(1, 5)
        self.SetRowLabelSize(50)
        self.SetColLabelValue(0, 'Time')
        self.SetColSize(0, 120)
        self.SetColLabelValue(1, 'Flags')
        self.SetColSize(1, 60)
        self.SetColLabelValue(2, 'Pld Id')
        self.SetColSize(2, 70)
        self.SetColLabelValue(3, 'Payload')
        self.SetColSize(3, 130)
        self.SetColLabelValue(4, 'Raw Bytes')
        self.SetColSize(4, 300)

        self.conn = comms.getConnection()
        self.conn.bindSendWatcher(self.printSentPacket)
        self.conn.bindRecieveWatcher(self.printRecievedPacket)


    def printSentPacket(self, request):
       
        time = datetime.datetime.time(datetime.datetime.now())
        header = request.getHeaderFlags()
        payload_id = request.getPayloadId()
        payload = request.getPayload()
        raw_hex = request.getPacketHex()
        raw_hex = ','.join(raw_hex)

        self.AppendRows()
        self.SetCellValue(self.row, 0, str(time))
        self.SetCellValue(self.row, 1, str(header))
        self.SetCellValue(self.row, 2, str(payload_id))
        self.SetCellValue(self.row, 3, str(payload))
        self.SetCellValue(self.row, 4, str(raw_hex))

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
        self.SetCellValue(self.row, 4, str(raw_hex))
        
        self.MakeCellVisible(self.row + 1, 1)
        self.ForceRefresh()

        self.row += 1
