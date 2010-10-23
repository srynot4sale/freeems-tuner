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
import libs.config
import xml.dom.minidom
from xml.dom.minidom import Node


# Helper value for inserting spacing into sizers
blank = (0,0)


class tab(wx.Panel):
    '''
    Tuning tables tab

    Contains a basic grid for tuning, and buttons for syncing
    '''

    ID_LOAD_FROM_FILE_TABLE = wx.NewId()
    ID_LOAD_FROM_DEVICE_TABLE = wx.NewId()
    ID_SAVE_TO_FILE_TABLE = wx.NewId()
    ID_SAVE_TO_DEVICE_TABLE = wx.NewId()

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

    # Highlight cell timer
    _timer = None


    def __init__(self, parent):
        '''
        Setup interface elements
        '''
        wx.Panel.__init__(self, parent)

        self.controller = parent.GetParent().getController()

        self.grid = tuningGrid(self)

        # Create buttons and bind to methods
        self.loadFromFileButton = wx.Button(self, self.ID_LOAD_FROM_FILE_TABLE, 'Load From File')
        self.loadFromDeviceButton = wx.Button(self, self.ID_LOAD_FROM_DEVICE_TABLE, 'Load From Device')
        self.saveToFileButton = wx.Button(self, self.ID_SAVE_TO_FILE_TABLE, 'Save To File')
        self.saveToDeviceButton = wx.Button(self, self.ID_SAVE_TO_DEVICE_TABLE, 'Save To Device')

        self.loadFromDeviceButton.Bind(wx.EVT_BUTTON, self.loadFromDevice, id=self.ID_LOAD_FROM_DEVICE_TABLE)
        self.saveToFileButton.Bind(wx.EVT_BUTTON, self.saveToFile, id=self.ID_SAVE_TO_FILE_TABLE)
        self.loadFromFileButton.Bind(wx.EVT_BUTTON, self.loadFromFile, id=self.ID_LOAD_FROM_FILE_TABLE)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.loadFromDeviceButton, 3)
        sizer3.Add(self.loadFromFileButton, 3)
        sizer3.Add(self.saveToFileButton, 3)
        sizer3.Add(self.saveToDeviceButton, 3)

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


    def _setupTimer(self):
        '''
        Setup timer to update the GUI display
        '''
        self._timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.grid.highlightCell, self._timer)

        # Use realtime update frequency
        frequency = libs.config.get('Gui', 'realtime_update_frequency')
        self._timer.Start(int(frequency))


# path needs extracting from dialog.... TODO
    def saveToFile(self, event):
        tune = open("data/tunes/tune.xml", "w")
        tune.write("<FreeEMS>\n")
        tune.write("\t<Table>\n")
        tune.write("\t\t<TableID value=\"" + str(self.grid.table_id) + "\" />\n")
        tune.write("\t\t<Cells value=\"" + str(self.grid.cells) + "\" />\n")
        tune.write("\t\t<RPMAxis value=\"" + str(self.grid.axis_rpm) + "\" />\n")
        tune.write("\t\t<RPMAxisLength value=\"" + str(self.grid.length_rpm) + "\" />\n")
        tune.write("\t\t<RPMAxisLengthMax value=\"" + str(self.grid.max_length_rpm) + "\" />\n")
        tune.write("\t\t<LoadAxis value=\"" + str(self.grid.axis_load) + "\" />\n")
        tune.write("\t\t<LoadAxisLength value=\"" + str(self.grid.length_load) + "\" />\n")
        tune.write("\t\t<LoadAxisLengthMax value=\"" + str(self.grid.max_length_load) + "\" />\n")
        tune.write("\t</Table>\n")
        tune.write("</FreeEMS>\n")
        tune.close()


    def loadFromFile(self, event):
        doc = xml.dom.minidom.parse("data/tunes/tune.xml")
        tune = doc.getElementsByTagName("Table")
        table = tune.item(0)

        self.grid.table_id = int(table.childNodes[1].attributes.item(0).value)
        self.grid.cells = eval(table.childNodes[3].attributes.item(0).value)
        self.grid.axis_rpm = eval(table.childNodes[5].attributes.item(0).value)
        self.grid.length_rpm = int(table.childNodes[7].attributes.item(0).value)
        self.grid.max_length_rpm = int(table.childNodes[9].attributes.item(0).value)
        self.grid.axis_load = eval(table.childNodes[11].attributes.item(0).value)
        self.grid.length_load = int(table.childNodes[13].attributes.item(0).value)
        self.grid.max_length_load = int(table.childNodes[15].attributes.item(0).value)

        self.grid.updateDisplay()


    def loadFromDevice(self, event):
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
        if isinstance(event.packet, self._protocol.responses.responseDataRequest):
            # No longer expecting
            self._expecting = False
            self.grid.updateData(event.packet)

            # Turn on timer
            self._setupTimer()
