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


# Some hardcoded values from firmware
MAINTAINABLE_MAX_RPM_LENGTH = 27	    # How many cells on the X axis max
MAINTAINABLE_MAX_LOAD_LENGTH = 21	    # How many cells on the Y axis max
MAINTAINABLE_MAX_MAIN_LENGTH = 462	    # 924B 462 shorts maximum main table length


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

        #self.SetRowLabelValue(r, str(r + 1))

        self.SetDefaultCellFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))


    def updateData(self, packet):

        payload = packet.getPayload()

        # Get rpm axis length
        length_rpm = protocols.shortFrom8bit(payload[0:2])

        # Get load axis length
        length_load = protocols.shortFrom8bit(payload[2:4])

        # Get rpm axis
        rpm_axis = []
        offset = 4
        i = 0
        while i < MAINTAINABLE_MAX_RPM_LENGTH:
            if i < length_rpm:
                value = protocols.shortFrom8bit(payload[offset:offset+2])
                rpm_axis.append(value)

            offset += 2
            i += 1

        # Get load axis
        load_axis = []
        i = 0
        while i < MAINTAINABLE_MAX_LOAD_LENGTH:
            while i < length_load:
                value = protocols.shortFrom8bit(payload[offset:offset+2])
                load_axis.append(value)

            offset += 2
            i += 1

        # Get values
#        while i < MAINTAINABLE_MAX_MAIN_LENGTH:
        
        # Upgrade grid

