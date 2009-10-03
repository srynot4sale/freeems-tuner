#   Copyright 2008, 2009 Aaron Barnes
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

import comms, gui.realtimeDataInterface, libs.config


# Helper value for inserting spacing into sizers
blank = (0,0)


class tab(wx.Panel):
    '''
    Real-time data stream display tab
    '''

    # Protocol object cache
    _protocol = None

    # GUI update timer
    _timer = None

    # Interface
    interface = None


    def __init__(self, parent):
        '''
        Setup interface elements
        '''
        wx.Panel.__init__(self, parent)
        self.controller = parent.GetParent().getController()

        self.interface = gui.realtimeDataInterface.realtimeDataInterface(self)

        self.SetSizer(self.interface)
        self.Layout()

        self._setupTimer()
        self._setupComms()


    def _setupComms(self):
        '''
        Bind watcher method to comms
        '''
        # Bind to connection
        self.conn = comms.getConnection()
        self.conn.bindReceiveWatcher(self)

        # Bind to events
        self.Bind(comms.interface.EVT_RECEIVE, self.monitorPackets)


    def _setupTimer(self):
        '''
        Setup timer to update the GUI display
        '''
        self._timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.interface.updateGui, self._timer)

        # Load configured update frequency
        frequency = libs.config.get('Gui', 'realtime_update_frequency')
        self._timer.Start(int(frequency))


    def monitorPackets(self, event):
        '''
        Check for received datalogs
        '''
        if not self._protocol:
            self._protocol = self.conn.getProtocol()

        # Check
        if isinstance(event.packet, self._protocol.responses.responseBasicDatalog):
            self.interface.updateData(event.packet)
