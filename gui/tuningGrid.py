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


import wx
import wx.grid as grid

import comms.protocols as protocols


class tuningGrid(grid.Grid):

    # Table memory location
    table_id = None

    # Max axis lengths
    max_length_rpm = 0
    max_length_load = 0

    # Max table lengths
    max_length_table = 0

    # Axis lengths
    length_rpm = 0
    length_load = 0

    # Axis values
    axis_rpm = []
    axis_load = []

    # Cell values
    cells = []

    def __init__(self, parent):
        '''
        Setup gui
        '''
        grid.Grid.__init__(self, parent)

        self.SetDefaultCellFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        # Generate an empty, unlabeled grid
        self.CreateGrid(1, 1)
        self.SetRowLabelSize(50)

        self.SetDefaultCellFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))


    def updateData(self, packet):
        '''
        Updating tuning table data to reflect
        loaded table data
        '''
        payload = packet.getPayload()

        # Get table memory location
        self.table_id = protocols.shortFrom8bit(payload[0:2])

        # Get rpm axis max length
        self.max_length_rpm = protocols.shortFrom8bit(payload[2:4])

        # Get load axis max length
        self.max_length_load = protocols.shortFrom8bit(payload[4:6])

        # Get table max length
        self.max_length_table = protocols.shortFrom8bit(payload[6:8])

        # Get rpm axis length
        self.length_rpm = protocols.shortFrom8bit(payload[8:10])

        # Get load axis length
        self.length_load = protocols.shortFrom8bit(payload[10:12])

        # Get rpm axis
        self.axis_rpm = []
        offset = 12
        i = 0
        while i < self.max_length_rpm:
            if i < self.length_rpm:
                value = protocols.shortFrom8bit(payload[offset:offset+2])
                self.axis_rpm.append(value)

            offset += 2
            i += 1

        # Get load axis
        self.axis_load = []
        i = 0
        while i < self.max_length_load:
            if i < self.length_load:
                value = float(protocols.shortFrom8bit(payload[offset:offset+2])) / 100
                self.axis_load.append(value)

            offset += 2
            i += 1

        # Update cell values
        load = 0
        while load < self.length_load:
            rpm = 0
            self.cells.insert(load, [])
            while rpm < self.length_rpm:
                value = float(protocols.shortFrom8bit(payload[offset:offset+2])) / 512
                self.cells[load].append(value)
                offset += 2
                rpm += 1

            load += 1

        self.updateDisplay()


    def updateDisplay(self):
        '''
        Update tuning table grid
        '''
        # Get current size of grid
        rpm_axis_size = self.GetNumberCols()
        load_axis_size = self.GetNumberRows()

        # Update table to reflect new size
        if rpm_axis_size < self.length_rpm:
            self.AppendCols(self.length_rpm - rpm_axis_size)

        if load_axis_size < self.length_load:
            self.AppendRows(self.length_load - load_axis_size)

        # Set axis labels
        i = 0
        while i < self.length_rpm:
            self.SetColLabelValue(i, str(self.axis_rpm[i]))
            self.SetColSize(i, 50)
            i += 1
        
        i = 0
        while i < self.length_load:
            self.SetRowLabelValue(i, '%.2f' % self.axis_load[i])
            i += 1

        load = 0
        while load < self.length_load:
            rpm = 0
            while rpm < self.length_rpm:
                value = '%.3f' % self.cells[load][rpm]
                self.SetCellValue(load, rpm, value)
                rpm += 1

            load += 1
