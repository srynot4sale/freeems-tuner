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

from gui.tuningGrid import tuningGrid


# Helper value for inserting spacing into sizers
blank = (0,0)


class tab(wx.Panel):
    '''
    Tuning tables tab

    Contains a basic grid for tuning, and buttons for syncing
    '''

    # Controller
    controller = None

    # Main grid
    grid = None

    def __init__(self, parent):
        '''
        Setup interface elements
        '''
        wx.Panel.__init__(self, parent)

        self.controller = parent.GetParent().getController()

        self.grid = tuningGrid(self)

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(blank, 1)
        sizer2.Add(self.grid, 58, wx.EXPAND)
        sizer2.Add(blank, 1)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer2, 58, wx.EXPAND)
        sizer1.Add(blank, 1)

        self.SetSizer(sizer1)
        self.Layout()
