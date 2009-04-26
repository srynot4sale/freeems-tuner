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


import comms, gui, commsConnectWarning

import wx


blank = (0,0)


class realtimeDataInterface(wx.BoxSizer):

    ID_LOGGING_TOGGLE = wx.NewId()

    hum_label = ['Inlet Air Temperature',
                 'Coolant/Head Temperature',
                 'Throttle Position',
                 'Exhaust Gas Oxygen 1',
                 'Manifold Absolute Pressure',
                 'Atmospheric Absolute Pressure',
                 'Battery Reference Voltage',
                 'Manifold Air Temperature',
                 'Exhaust Gas Oxygen 2',
                 'Intercooler Absolute Pressure',
                 'Mass Air Flow',
                 'Delta MAP',
                 'Delta TPS',
                 'Revolutions Per Minute',
                 'Delta RPM',
                 'Delta Delta RPM',
                 'Load Main',
                 'Volumetric Efficiency Main',
                 'Lamda',
                 'Air Flow',
                 'Density And Fuel',
                 'Base Pulse Width',
                 'Injector Dead Time',
                 'Engine Temperature Enrichment',
                 'Transient Fuel Correction Total',
                 'Final Pulse Width',
                 'Reference Pulse Width'
                 ]
    
    abrv_label = ['IAT', 'CHT', 'TPS',
                 'EGO1', 'MAP', 'AAP',
                 'BRV', 'MAT', 'EGO2',
                 'IAP', 'MAF', 'DMAP',
                 'DTPS', 'RPM', 'DRPM',
                 'DDRPM', 'LoadMain', 'VEMain',
                 'Lamda', 'AirFlow', 'Density&&Fuel',
                 'BasePW', 'IDT', 'ETE',
                 'TFCTotal', 'FinalPW','RefPW'
                 ]

    realtime_data = [0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0]

    def __init__(self, parent):
        '''Setup UI elements'''

        wx.BoxSizer.__init__(self, wx.VERTICAL)
        self._controller = parent.controller

        # Populate real-time data for display

        # maybe a loop here
        # maybe some more control flow here
        # maybe a GOTO here ;)

        # Controls
        log_types = ['Basic']
        self.logging_type = wx.Choice(parent, -1, choices = log_types)
        self.toggle = wx.Button(parent, self.ID_LOGGING_TOGGLE, 'Start Logging')

        self.toggle.Bind(wx.EVT_BUTTON, self.toggleLogging, id=self.ID_LOGGING_TOGGLE)
        
        
        # Locating elements
        sizer6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer6.Add(self.logging_type, 10, wx.EXPAND)
        sizer6.Add(blank, 1)
        sizer6.Add(self.toggle, 10, wx.EXPAND)

        sizer5 = wx.BoxSizer(wx.VERTICAL)
        sizer5.Add(sizer6, 1)
        sizer5.Add(blank, 12)

        sizer4 = wx.BoxSizer(wx.VERTICAL)
        sizer4.Add(blank, 1)
        for data in self.realtime_data:
            text = wx.StaticText(parent, -1, str(data), style = wx.ALIGN_RIGHT)
            sizer4.Add(text, 40, wx.EXPAND)
            sizer4.Add(blank, 1)
            
        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(blank, 1)
        for label in self.abrv_label:
            text = wx.StaticText(parent, -1, label, style = wx.ALIGN_RIGHT)
            sizer3.Add(text, 40, wx.EXPAND)
            sizer3.Add(blank, 1)

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(blank, 1)
        for label in self.hum_label:
            text = wx.StaticText(parent, -1, label, style = wx.ALIGN_LEFT)
            sizer2.Add(text, 40, wx.EXPAND)
            sizer2.Add(blank, 1)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer2, 15, wx.EXPAND)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer3, 8, wx.EXPAND)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer4, 3, wx.EXPAND)
        sizer1.Add(blank, 19)
        sizer1.Add(sizer5, 20, wx.EXPAND)
        sizer1.Add(blank, 1)

        self.Add(blank, 1)
        self.Add(sizer1, 10, wx.EXPAND)
        self.Add(blank, 1)


    def toggleLogging(self, event):
        '''
        Send packet to toggle logging
        '''
        # Check connected
        if not commsConnectWarning.confirmConnected(gui.frame):
            return

        protocol = comms.getConnection().getProtocol()
        packet = protocol.getRequestPacket('SetAsyncDatalogType')
        packet.startBasic()

        data = {'packet': packet}
        self._controller.action('comms.sendRequest', data)
