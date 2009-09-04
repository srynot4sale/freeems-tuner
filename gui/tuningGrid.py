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


import wx, wx.grid as grid


class tuningGrid(grid.Grid):

    conn = None
    row = 0

    def __init__(self, parent):
        '''
        Setup gui
        '''
        grid.Grid.__init__(self, parent)

        # Generate an empty, unlabeled grid
        self.CreateGrid(16, 16)
        self.SetRowLabelSize(50)

        r = 0
        while r < 16:
            self.SetRowLabelValue(r, str(r + 1))
            r += 1

        c = 0
        while c < 16:
            self.SetColLabelValue(c, str(c + 1))
            self.SetColSize(c, 50)
            c += 1

        self.SetDefaultCellFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
