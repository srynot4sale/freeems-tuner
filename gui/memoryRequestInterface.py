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
import libs.data as data
import gui
import commsConnectWarning


logger = logging.getLogger('gui.memoryRequestInterface')


blank = (0,0)


class memoryRequestInterface(wx.BoxSizer):

    _p_text = None
    _p_input = None
    _p_options = []
    _p_ids = []

    _b_text =  None
    _b_input = None
    _b_options = []
    _b_ids = []

    _send = None

    ID_SEND_REQUEST = wx.NewId()


    def __init__(self, parent):
        '''Setup UI elements'''

        wx.BoxSizer.__init__(self, wx.VERTICAL)

        # Get payload id's
        options = protocols.getProtocol().getMemoryRequestPayloadIdList()
        for id in options.keys():
            self._p_options.append('%s (%d)' % (options[id], id))
            self._p_ids.append(id)

        self._p_text = wx.StaticText(parent, -1, 'Payload ID', style = wx.ALIGN_CENTER)
        self._p_input = wx.Choice(parent, -1, choices = self._p_options)

        # Get block id's
        try:
            locations = data.loadProtocolDataFile('location_ids')['FreeEMSLocationIDs']
            location_keys = []
            for key in locations.keys():
                location_keys.append(int(key))

            location_keys.sort()
            
            options = {}
            for location in location_keys:
                self._b_options.append('%s (%d)' % (locations[str(location)], location))
                self._b_ids.append(location)

        except KeyError, e:
            # Data file appears to be formed incorrectly
            logger.error('Data location ids data file appears to be formed incorrectly: %s' % e)
            self._b_options = []
            self._b_ids = []

        self._b_text = wx.StaticText(parent, -1, 'Block ID', style = wx.ALIGN_CENTER)
        self._b_input = wx.Choice(parent, -1, choices = self._b_options)
        
        # Magic button
        self._send = wx.Button(parent, self.ID_SEND_REQUEST, 'Send Request')

        self._send.Bind(wx.EVT_BUTTON, self.sendRequest, id = self.ID_SEND_REQUEST)

        # Locating elements
        sizer4 = wx.BoxSizer(wx.VERTICAL)
        sizer4.Add(blank, 5)
        sizer4.Add(self._send, 5, wx.EXPAND)

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(self._b_text, 4, wx.EXPAND)
        sizer3.Add(blank, 1)
        sizer3.Add(self._b_input, 5, wx.EXPAND)
        
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(self._p_text, 4, wx.EXPAND)
        sizer2.Add(blank, 1)
        sizer2.Add(self._p_input, 5, wx.EXPAND)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer2, 23, wx.EXPAND)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer3, 23, wx.EXPAND)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer4, 10, wx.EXPAND)
        sizer1.Add(blank, 1)

        self.Add(blank, 5)
        self.Add(sizer1, 10, wx.EXPAND)
        self.Add(blank, 45)
        

    def sendRequest(self, event):
        '''Send memory request'''
        
        # Check connected
        if not commsConnectWarning.confirmConnected(gui.frame):
            return

        payload_id = self._p_input.GetSelection()
        block_id = self._b_input.GetSelection()

        # Correct small bug where selection will be -1 if input has not
        # been in focus
        if payload_id < 0:
            payload_id = 0
        if block_id < 0:
            block_id = 0

        payload_id = self._p_ids[payload_id]
        block_id = self._b_ids[block_id]

        protocols.getProtocol().sendMemoryRequest(payload_id, block_id)
