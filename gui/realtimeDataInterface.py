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
#                'TPS',
                'EGO',
                'MAP',
#                'AAP',
                'BRV',
#                'MAT',
#                'EGO2',
#                'IAP',
#                'MAF',
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
#                'adc0',
#                'adc1',
#                'adc2',
#                'adc3',
#                'adc4',
#                'adc5',
#                'adc6',
#                'adc7',
#                'adc8',
#                'adc9',
#                'adc10',
#                'adc11',
#                'adc12',
#                'adc13',
#                'adc14',
#                'adc15',
    ]

    # List of human readable titles
    titles = {
                'IAT':          'Inlet Air Temperature (celcius)',
                'CHT':          'Coolant / Head Temperature (celcius)',
                'TPS':          'Throttle Position Sensor (percent)',
                'EGO':          'Exhaust Gas Oxygen (lambda)',
                'MAP':          'Manifold Absolute Pressure (kPa)',
                'AAP':          'Atmospheric Absolute Pressure (kPa)',
                'BRV':          'Battery Reference Voltage (volts)',
                'MAT':          'Manifold Air Temperature (celcius)',
                'EGO2':         'Exhaust Gas Oxygen (lambda)',
                'IAP':          'Intercooler Absolute Pressure (kpa)',
                'MAF':          'Mass Air Flow',
                'DMAP':         'Delta MAP',
                'DTPS':         'Delta TPS',
                'RPM':          'RPM',
                'DRPM':         'Delta RPM (rpm/second)',
                'DDRPM':        'Delta Delta RPM (rpm/second)',
                'LoadMain':     'Load Main',
                'VEMain':       'VE Main (percent)',
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
                'sp5':          'sp5 - sequence counter',
                'adc0':         'adc0',
                'adc1':         'adc1',
                'adc2':         'adc2',
                'adc3':         'adc3',
                'adc4':         'adc4 - bat ref',
                'adc5':         'adc5',
                'adc6':         'adc6',
                'adc7':         'adc7',
                'adc8':         'adc8',
                'adc9':         'adc9',
                'adc10':         'adc10',
                'adc11':         'adc11',
                'adc12':         'adc12',
                'adc13':         'adc13',
                'adc14':         'adc14',
                'adc15':         'adc15',
    }

    # Unit conversion
    units = {
                'IAT':          'temp',
                'CHT':          'temp',
                'TPS':          'percent_tps',
                'EGO':          'lambda',
                'MAP':          'pressure',
                'AAP':          'pressure',
                'BRV':          'volts',
                'MAT':          'temp',
                'EGO2':         'lambda',
                'IAP':          'pressure',
                'RPM':          'rpm',
                'DRPM':         'rpm',
                'DDRPM':        'rpm',
                'LoadMain':     'raw',
                'VEMain':       'percent',
                'Lambda':       'lambda',
    }

    # Data log packet payload order
    _structure = [ 'IAT', 'CHT', 'TPS', 'EGO', 'MAP', 'AAP', 'BRV', 'MAT',
        'EGO2', 'IAP', 'MAF', 'DMAP', 'DTPS', 'RPM', 'DRPM', 'DDRPM',
        'LoadMain', 'VEMain', 'Lambda', 'AirFlow', 'DensityFuel', 'BasePW',
        'IDT', 'ETE', 'TFCTotal', 'FinalPW', 'RefPW', 'sp1', 'sp2', 'sp3',
        'sp4', 'sp5', 'adc0', 'adc1', 'adc2', 'adc3', 'adc4', 'adc5', 'adc6',
        'adc7', 'adc8', 'adc9', 'adc10', 'adc11', 'adc12', 'adc13', 'adc14',
        'adc15', ]

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
                'adc0':         0,
                'adc1':         0,
                'adc2':         0,
                'adc3':         0,
                'adc4':         0,
                'adc5':         0,
                'adc6':         0,
                'adc7':         0,
                'adc8':         0,
                'adc9':         0,
                'adc10':        0,
                'adc11':        0,
                'adc12':        0,
                'adc13':        0,
                'adc14':        0,
                'adc15':        0,
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
        sizer1.Add(sizer4, 10, wx.EXPAND)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer2, 20, wx.EXPAND)
        sizer1.Add(blank, 5)
        sizer1.Add(sizer5, 15, wx.EXPAND)
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
        print 'here'
        # Data store
        data = self.data

        # Units
        units = self.units

        # Basic datalog packet payloads consist of 4 bytes of data for each of the 27 variables logged
        # These 4 bytes contain two ints, and we shall average the two for display
        # Loop through playload 4 bytes at a time
        payload = packet.getPayload()
        payload_length = len(payload)

        i = 0
        for key in self._structure:
            # Decode binary and cast to float
            value = float(protocols.shortFrom8bit(payload[i:i+2]))

            # Process display
            if key in units:
                if units[key] == 'temp':
                    value = '%.2f' % ((value / 100) - 273.15)
                elif units[key] == 'percent_tps':
                    value = '%.3f' % (value / 640)
                elif units[key] == 'percent':
                    value = '%.3f' % (value / 512)
                elif units[key] == 'lambda':
                    value = '%d' % (value / 32768)
                elif units[key] == 'pressure':
                    value = '%.2f' % (value / 100)
                elif units[key] == 'volts':
                    value = '%.3f' % (value / 1000)
                elif units[key] == 'rpm':
                    value = '%.1f' % (value / 2)
            else:
                value = '%d' % value

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
        print 'display'
        display = self.display
        data = self.data
        controls = self._display_controls

        for key in display:
            controls[key].SetValue(str(data[key]))
