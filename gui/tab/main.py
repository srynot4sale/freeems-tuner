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

from gui.commsUtilityRequests import commsUtilityRequests 
from gui.commsDiagnostics import commsDiagnostics
from gui.commsUtilityFirmwareSoftResetButton import commsUtilityFirmwareSoftResetButton
from gui.commsUtilityFirmwareHardResetButton import commsUtilityFirmwareHardResetButton


logger = logging.getLogger('gui.tabs.main')


# Helper value for inserting spacing into sizers
blank = (0,0)


class tab(wx.Panel):
    '''Main tab, contains mostly serial stuff for now'''

    def __init__(self, parent):
        '''Setup interface elements'''
        wx.Panel.__init__(self, parent)

        self.requests       = commsUtilityRequests(self)
        self.button_red     = commsUtilityFirmwareHardResetButton(self)
        self.button_orange  = commsUtilityFirmwareSoftResetButton(self)

        self.comms = commsDiagnostics(self)

        # Try keep all spaces at 1/60th of the screen width or height
        # This first sizer will only add up to 58 tho as it is enclosed in another
        # horizontal sizer
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.requests, 15, wx.EXPAND)
        sizer3.Add(blank, 12)
        sizer3.Add(self.button_orange, 15, wx.EXPAND)
        sizer3.Add(blank, 1)
        sizer3.Add(self.button_red, 15, wx.EXPAND)

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(blank, 1)
        sizer2.Add(self.comms, 45, wx.EXPAND)
        sizer2.Add(blank, 1)
        sizer2.Add(sizer3, 12, wx.EXPAND)
        sizer2.Add(blank, 1)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer2, 58, wx.EXPAND)
        sizer1.Add(blank, 1)

        self.SetSizer(sizer1)
        self.Layout()
