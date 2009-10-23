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

    conn = None
    row = 0

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
        Updating tuning table to reflect
        loaded table data
        '''
        payload = packet.getPayload()

        # Get rpm axis max length
        max_length_rpm = protocols.shortFrom8bit(payload[2:4])

        # Get load axis max length
        max_length_load = protocols.shortFrom8bit(payload[4:6])

        # Get table max length
        max_length_table = protocols.shortFrom8bit(payload[6:8])

        # Get rpm axis length
        length_rpm = protocols.shortFrom8bit(payload[8:10])

        # Get load axis length
        length_load = protocols.shortFrom8bit(payload[10:12])

        # Get rpm axis
        rpm_axis = []
        offset = 12
        i = 0
        while i < max_length_rpm:
            if i < length_rpm:
                value = protocols.shortFrom8bit(payload[offset:offset+2])
                rpm_axis.append(value)

            offset += 2
            i += 1

        # Get load axis
        load_axis = []
        i = 0
        while i < max_length_load:
            if i < length_load:
                value = protocols.shortFrom8bit(payload[offset:offset+2])
                load_axis.append(value)

            offset += 2
            i += 1

        # Setup
        # Get current size of grid
        rpm_axis_current = self.GetNumberCols()
        load_axis_current = self.GetNumberRows()

        # Update table to reflect new size
        if rpm_axis_current < length_rpm:
            self.AppendCols(length_rpm - rpm_axis_current)

        if load_axis_current < length_load:
            self.AppendRows(length_load - load_axis_current)

        # Set axis labels
        i = 0
        while i < length_rpm:
            self.SetColLabelValue(i, str(rpm_axis[i]))
            self.SetColSize(i, 50)
            i += 1
        
        i = 0
        while i < length_load:
            self.SetRowLabelValue(i, str(load_axis[i]))
            i += 1

        # Update cell values
        load = 0
        while load < length_load:
            rpm = 0
            while rpm < length_rpm:
                value = '%.2f' % (float(protocols.shortFrom8bit(payload[offset:offset+2])) / 512)
                self.SetCellValue(load, rpm, value)
                offset += 2
                rpm += 1

            load += 1
