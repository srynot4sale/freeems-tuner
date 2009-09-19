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
import gui
import gui.commsConnectWarning as commsConnectWarning
import comms
import comms.protocols as protocols


# Helper value for inserting spacing into sizers
blank = (0,0)


class tab(wx.Panel):
    '''
    Tuning tables tab

    Contains a basic grid for tuning, and buttons for syncing
    '''

    ID_LOAD_TABLE = wx.NewId()
    ID_SAVE_TABLE = wx.NewId()

    # Controller
    controller = None

    # Connection
    _conn = None

    # Protocol
    _protocol = None

    # Main grid
    grid = None

    # Expecting table data from ecu
    _expecting = False


    def __init__(self, parent):
        '''
        Setup interface elements
        '''
        wx.Panel.__init__(self, parent)

        self.controller = parent.GetParent().getController()

        self.grid = tuningGrid(self)

        # Create buttons and bind to methods
        self.loadButton = wx.Button(self, self.ID_LOAD_TABLE, 'Load Table')
        self.saveButton = wx.Button(self, self.ID_SAVE_TABLE, 'Save Table')

        self.loadButton.Bind(wx.EVT_BUTTON, self.loadTable, id=self.ID_LOAD_TABLE)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.loadButton, 4)
        sizer3.Add(blank, 4)
        sizer3.Add(self.saveButton, 4)

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(blank, 1)
        sizer2.Add(sizer3, 4, wx.EXPAND)
        sizer2.Add(blank, 1)
        sizer2.Add(self.grid, 58, wx.EXPAND)
        sizer2.Add(blank, 1)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer2, 58, wx.EXPAND)
        sizer1.Add(blank, 1)

        self.SetSizer(sizer1)
        self.Layout()

        self._setupComms()


    def loadTable(self, event):
        '''
        Send packet to toggle logging
        '''
        # Check connected
        if not commsConnectWarning.confirmConnected(gui.frame):
            return

        # Set expecting flag
        self._expecting = True

        data = {
            'type': 'RetrieveBlockFromRAM',
            'block_id': 0
        }

        self.controller.action('comms.sendMemoryRequest', data)


    def _setupComms(self):
        '''
        Bind watcher method to comms
        '''
        # Bind to connection
        self._conn = comms.getConnection()
        self._conn.bindReceiveWatcher(self)

        # Bind to events
        self.Bind(comms.interface.EVT_RECEIVE, self.monitorPackets)


    def monitorPackets(self, event):
        '''
        Check for received table dumps
        '''
        # If not expecting a table dump, ignore packets
        if not self._expecting:
            return

        if not self._protocol:
            self._protocol = self._conn.getProtocol()

        # Check
#        if isinstance(event.packet, self._protocol.responses.responseDataRequest):
            # No longer expecting
#            self._expecting = False
#            self.grid.updateData(event.packet)
