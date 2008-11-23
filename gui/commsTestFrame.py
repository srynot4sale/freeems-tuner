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
import comms
import protocols
import logging
import datetime

logger = logging.getLogger('gui.commsTestFrame')

class commsTestFrame(wx.Frame):
    """Comms Testing Frame"""

    def __init__(self, parent):
        """Create a Frame instance."""
        wx.Frame.__init__(self, parent, id=-1, title='Comms Test', pos=wx.DefaultPosition, size=(300,500))

        self.BuildWindow()
        self.Show()


    def BuildWindow(self):

        self.window = window = wx.Panel(parent=self, id=-1)

        textbox = wx.StaticText(window, -1, 'To be implemented...')
        start_button = wx.Button(window, -1, 'Start Tests')
        stop_button = wx.Button(window, -1, 'Stop Tests')
        close_button = wx.Button(window, -1, 'Close')

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(start_button, 2)
        sizer3.Add((0,0), 1)
        sizer3.Add(stop_button, 2)
        sizer3.Add((0,0), 11)
        sizer3.Add(close_button, 2)
        
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add((0,0), 1)
        sizer2.Add(textbox, 10, wx.EXPAND)
        sizer2.Add((0,0), 1)
        sizer2.Add(sizer3, 7, wx.EXPAND)
        sizer2.Add((0,0), 1)

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add((0,0), 1)
        sizer1.Add(sizer2, 18, wx.EXPAND)
        sizer1.Add((0,0), 1)

        window.SetSizer(sizer1)
        window.Layout()
       
