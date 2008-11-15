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

logger = logging.getLogger('gui.commsUtilityFirmwareHardResetButton')

class commsUtilityFirmwareHardResetButton(wx.BoxSizer):

    options = {}
    button = None

    ID_SEND_FIRMWARE_RESET = wx.NewId()


    def __init__(self, parent):

        wx.BoxSizer.__init__(self, wx.VERTICAL)

        button_text  = 'The Big Red Button\n'
        button_text += '  (Hard EMS Reset)'
        self.button = wx.Button(parent, self.ID_SEND_FIRMWARE_RESET, button_text)
        self.button.SetBackgroundColour(wx.RED)
        self.button.SetForegroundColour(wx.WHITE)

        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        self.button.SetFont(font)

        self.Add((0,0), 1)
        self.Add(self.button, 15, wx.EXPAND)
        self.Add((0,0), 1)

        self.button.Bind(wx.EVT_BUTTON, self.sendRequest, id=self.ID_SEND_FIRMWARE_RESET)


    def sendRequest(self, event):

        protocols.getProtocol().sendUtilityHardResetRequest()
