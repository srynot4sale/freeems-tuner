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
import logging
import sys

import comms
import protocols
import version

class memoryRequestFrame(wx.Frame):
    """Memory request frame"""

    display = None

    def __init__(self, parent):
        """Create a frame instance."""
        wx.Frame.__init__(self, parent, id=-1, title='Memory Block Request', pos=wx.DefaultPosition, size=(500,300))

        self.BuildWindow()
        self.Center()
        self.Show()


    def BuildWindow(self):
        '''Build / position window elements'''
        self.window = window = wx.Panel(parent=self, id=-1)

        self.display = display = self.CreateDisplay(window) 

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add((0,0), 1)
        sizer2.Add(display, 18, wx.EXPAND)
        sizer2.Add((0,0), 1)

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add((0,0), 1)
        sizer1.Add(sizer2, 18, wx.EXPAND)
        sizer1.Add((0,0), 1)

        window.SetSizer(sizer1)
        window.Layout()
       

