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
import gui
import commsConnectWarning

logger = logging.getLogger('gui.memoryRequestBLockIdDropMenu')

class memoryRequestBlockIdDropMenu(wx.BoxSizer):

    options = {}
    text = None
    text2 = None
    input = None
    input2 = None
    send = None

    

    ID_SEND_REQUEST = wx.NewId()


    def __init__(self, parent):
        '''Setup UI elements'''
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)

        self.text = wx.StaticText(parent, -1, 'Payload ID', style=wx.ALIGN_CENTER)
        self.options = protocols.getProtocol().getMemoryRequestPayloadIdList()
        self.input = wx.Choice(parent, -1, choices=self.options)

        self.text2 = wx.StaticText(parent, -1, 'Block ID', style=wx.ALIGN_CENTER)
        self.options2 = protocols.getProtocol().getMemoryRequestBlockIdList()
        self.input2 = wx.Choice(parent, -1, choices=self.options2)
        
        self.send = wx.Button(parent, self.ID_SEND_REQUEST, 'Send Request')

        self.send.Bind(wx.EVT_BUTTON, self.sendRequest, id=self.ID_SEND_REQUEST)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add((0,0), 1)
        sizer4.Add(self.send, 18, wx.EXPAND)
        sizer4.Add((0,0), 1)

        sizer5 = wx.BoxSizer(wx.VERTICAL)
        sizer5.Add((0,0), 1)
        sizer5.Add(sizer4, 18, wx.EXPAND)
        sizer5.Add((0,0), 1)

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add((0,0), 1)
        sizer3.Add(self.text2, 3, wx.EXPAND)
        sizer3.Add((0,0), 1)
        sizer3.Add(self.input2, 5, wx.EXPAND)
        sizer3.Add((0,0), 1)
        
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add((0,0), 1)
        sizer2.Add(self.text, 3, wx.EXPAND)
        sizer2.Add((0,0), 1)
        sizer2.Add(self.input, 5, wx.EXPAND)
        sizer2.Add((0,0), 1)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add((0,0), 1)
        sizer1.Add(sizer2, 6, wx.EXPAND)
        sizer1.Add((0,0), 1)
        sizer1.Add(sizer3, 10, wx.EXPAND)
        sizer1.Add((0,0), 1)
        sizer1.Add(sizer5, 6, wx.EXPAND)
        sizer1.Add((0,0), 1)
        

        self.Add(sizer1)

        


    def sendRequest(self, event):
        '''Send utility request'''
        
        # Check connected
        if not commsConnectWarning.confirmConnected(gui.frame):
            return

        selection = self.input.GetSelection()
        selection2 = self.input2.GetSelection()

        # Correct small bug where selection will be -1 if input has not
        # been in focus
        if selection < 0:
            selection = 0
        if selection2 < 0:
            selection2 = 0

        protocols.getProtocol().sendMemoryRequest(selection, selection2)
