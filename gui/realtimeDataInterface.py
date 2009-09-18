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


import comms, comms.protocols as protocols, gui, commsConnectWarning

import wx


blank = (0,0)


class realtimeDataInterface(wx.BoxSizer):

    ID_LOGGING_TOGGLE = wx.NewId()

    # Vars to display (and their order)
    # Comment out lines here to hide them in the interface
    display = [

                'IAT',
                'CHT',
                'TPS',
                'EGO',
                'MAP',
                'AAP',
                'BRV',
                'MAT',
                'EGO2',
                'IAP',
                'MAF',
                'DMAP',
                'DTPS',
                'RPM',
                'DRPM',
                'DDRPM',
                'LoadMain',
                'VEMain',
                'Lambda',
                'AirFlow',
                'DensityFuel',
                'BasePW',
                'IDT',
                'ETE',
                'TFCTotal',
                'FinalPW',
                'RefPW',
                'sp1',
                'sp2',
                'sp3',
                'sp4',
                'sp5',
    ]

    # List of human readable titles
    titles = {
                'IAT':          'Inlet Air Temperature',
                'CHT':          'Coolant / Head Temperature',
                'TPS':          'Throttle Position Sensor',
                'EGO':          'Exhaust Gas Oxygen',
                'MAP':          'Manifold Absolute Pressure',
                'AAP':          'Atmospheric Absolute Pressure',
                'BRV':          'Battery Reference Voltage',
                'MAT':          'Manifold Air Temperature',
                'EGO2':         'Exhaust Gas Oxygen',
                'IAP':          'Intercooler Absolute Pressure',
                'MAF':          'Mass Air Flow',
                'DMAP':         'Delta MAP',
                'DTPS':         'Delta TPS',
                'RPM':          'RPM',
                'DRPM':         'Delta RPM',
                'DDRPM':        'Delta Delta RPM',
                'LoadMain':     'Load Main',
                'VEMain':       'VE Main',
                'Lambda':       'Lambda',
                'AirFlow':      'Air Flow',
                'DensityFuel':  'Density and Fuel',
                'BasePW':       'Base PW',
                'IDT':          'IDT',
                'ETE':          'ETE',
                'TFCTotal':     'TFC Total',
                'FinalPW':      'Final PW',
                'RefPW':        'Ref PW',
                'sp1':          'sp1',
                'sp2':          'sp2',
                'sp3':          'sp3',
                'sp4':          'sp4',
                'sp5':          'sp5',
    }

    # Data log packet payload order
    _structure = [ 'IAT', 'CHT', 'TPS', 'EGO', 'MAP', 'AAP', 'BRV', 'MAT',
        'EGO2', 'IAP', 'MAF', 'DMAP', 'DTPS', 'RPM', 'DRPM', 'DDRPM',
        'LoadMain', 'VEMain', 'Lambda', 'AirFlow', 'DensityFuel', 'BasePW',
        'IDT', 'ETE', 'TFCTotal', 'FinalPW', 'RefPW', 'sp1', 'sp2', 'sp3',
        'sp4', 'sp5' ]

    # Latest data from datalog
    data = {
                'IAT':          0,
                'CHT':          0,
                'TPS':          0,
                'EGO':          0,
                'MAP':          0,
                'AAP':          0,
                'BRV':          0,
                'MAT':          0,
                'EGO2':         0,
                'IAP':          0,
                'MAF':          0,
                'DMAP':         0,
                'DTPS':         0,
                'RPM':          0,
                'DRPM':         0,
                'DDRPM':        0,
                'LoadMain':     0,
                'VEMain':       0,
                'Lambda':       0,
                'AirFlow':      0,
                'DensityFuel':  0,
                'BasePW':       0,
                'IDT':          0,
                'ETE':          0,
                'TFCTotal':     0,
                'FinalPW':      0,
                'RefPW':        0,
                'sp1':          0,
                'sp2':          0,
                'sp3':          0,
                'sp4':          0,
                'sp5':          0,
    }

    # TextCtrl objects for each variable data display
    _display_controls = {}


    def __init__(self, parent):
        '''
        Setup UI elements
        '''

        wx.BoxSizer.__init__(self, wx.VERTICAL)
        self._controller = parent.controller

        # Populate real-time data for display

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

        # Var display
        sizer4 = wx.BoxSizer(wx.VERTICAL)
        sizer4.Add(blank, 1)

        # Title display
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(blank, 1)

        # Generate display
        data = self.data
        for key in self.display:

            text = wx.StaticText(parent, -1, self.titles[key], style = wx.ALIGN_LEFT)
            sizer2.Add(text, 40, wx.EXPAND)
            sizer2.Add(blank, 1)

            text = wx.TextCtrl(parent, -1, str(data[key]), style = wx.ALIGN_RIGHT | wx.NO_BORDER)
            sizer4.Add(text, 40, wx.EXPAND)
            sizer4.Add(blank, 1)

            # Save references to controls in list
            self._display_controls[key] = text

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer2, 15, wx.EXPAND)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer4, 8, wx.EXPAND)
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
        packet = protocol.getRequestPacket('BasicDatalog')
        packet.startBasic()

        data = {'packet': packet}
        self._controller.action('comms.sendRequest', data)


    def updateData(self, packet):
        '''
        Update with data var with latest data from datalog

        Loops through packet payload decoding the variables, updates
        the self._data list, and then calls refreshDisplay()

        Packet parameter is the basicDatalog packet received.
        '''
        # Data store
        data = self.data

        # Basic datalog packet payloads consist of 4 bytes of data for each of the 27 variables logged
        # These 4 bytes contain two ints, and we shall average the two for display
        # Loop through playload 4 bytes at a time
        payload = packet.getPayload()
        payload_length = len(payload)

        i = 0
        for key in self._structure:
            value = protocols.shortFrom8bit(payload[i:i+2])

            # Update display
            data[key] = value

            # Next var
            i += 2

        self.refreshDisplay()


    def refreshDisplay(self):
        '''
        Refresh realtime data display

        This function simply loops through the self._data list, and updates
        the gui display for each variable with the latest data.

        This currently does not support unsigned and signed ints, like it should
        '''
        display = self.display
        data = self.data
        controls = self._display_controls

        for key in display:
            controls[key].SetValue(str(data[key]))
