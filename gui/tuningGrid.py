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
import wx.grid as grid

import gui
import gui.commsConnectWarning as commsConnectWarning
import comms.protocols as protocols


class tuningGrid(grid.Grid):

    # Table memory location
    table_id = None

    # Max axis lengths
    max_length_rpm = 0
    max_length_load = 0

    # Max table lengths
    max_length_table = 0

    # Axis lengths
    length_rpm = 0
    length_load = 0

    # Axis values
    axis_rpm = []
    axis_load = []

    # Cell values
    cells = []

    # Current cursor location
    selected_rpm = None
    selected_load = None

    # Currently highlighted cell coords
    _highlighted = None


    def __init__(self, parent):
        '''
        Setup gui
        '''
        grid.Grid.__init__(self, parent)

        self.SetDefaultCellFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        # Generate an empty, unlabeled grid
        self.CreateGrid(1, 1)
        self.SetRowLabelSize(50)

        # Set defaults
        self.SetDefaultCellFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.SetDefaultEditor(grid.GridCellFloatEditor())

        # Bind events for selecting cells and handling key presses
        self.Bind(grid.EVT_GRID_SELECT_CELL, self.onCellChange)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)


    def onCellChange(self, event):
        '''
        Record currently selected cell location
        '''
        self.selected_rpm = event.Col
        self.selected_load = event.Row
        event.Skip()


    def onKeyPress(self, event):
        '''
        Bind key presses 'j' and 'k' to update cell value up/down
        '''
        keycode = event.GetKeyCode()

        # Check if this is a key we are handling
        if keycode not in [74, 75]:
            event.Skip()
            return

        # Get selected cell
        rpm = self.selected_rpm
        load = self.selected_load

        # If no cell has been selected yet, do nothing
        if rpm == None or load == None:
            return

        value = self.cells[rpm][load]

        # Update cell values
        if keycode == 74:
            value += 0xFF
        else:
            value -= 0xFF

        if value > 0xFFFF:
            value = 0xFFFF
        elif value < 0:
            value = 0

        self.cells[rpm][load] = value
        self._updateCell(load, rpm)

        # Send update to ecu
        self.onCellUpdate(load, rpm, value)


    def onCellUpdate(self, load, rpm, value):
        '''
        Send update request to ecu with new value
        '''
        # Check connected
        if not commsConnectWarning.confirmConnected(gui.frame):
            return

        data = {
            'type': 'UpdateMainTableCell',
            'block_id': self.table_id,
            'load': load,
            'rpm': rpm,
            'value': value,
        }

        self.GetParent().controller.action('comms.updateMainTableCell', data)


    def updateData(self, packet):
        '''
        Updating tuning table data to reflect
        loaded table data
        '''
        payload = packet.getPayload()

        # Get table memory location
        self.table_id = protocols.shortFrom8bit(payload[0:2])

        # Get rpm axis max length
        self.max_length_rpm = protocols.shortFrom8bit(payload[2:4])

        # Get load axis max length
        self.max_length_load = protocols.shortFrom8bit(payload[4:6])

        # Get table max length
        self.max_length_table = protocols.shortFrom8bit(payload[6:8])

        # Get rpm axis length
        self.length_rpm = protocols.shortFrom8bit(payload[8:10])

        # Get load axis length
        self.length_load = protocols.shortFrom8bit(payload[10:12])

        # Get rpm axis
        self.axis_rpm = []
        offset = 12
        i = 0
        while i < self.max_length_rpm:
            if i < self.length_rpm:
                value = protocols.shortFrom8bit(payload[offset:offset+2])
                self.axis_rpm.append(value)

            offset += 2
            i += 1

        # Get load axis
        self.axis_load = []
        i = 0
        while i < self.max_length_load:
            if i < self.length_load:
                value = float(protocols.shortFrom8bit(payload[offset:offset+2])) / 100
                self.axis_load.append(value)

            offset += 2
            i += 1

        # Update cell values
        rpm = 0
        self.cells = []
        while rpm < self.length_rpm:
            load = 0
            self.cells.insert(rpm, [])
            while load < self.length_load:
                value = protocols.shortFrom8bit(payload[offset:offset+2])
                self.cells[rpm].append(value)
                offset += 2
                load += 1

            rpm += 1

        self.updateDisplay()


    def updateDisplay(self):
        '''
        Update tuning table grid
        '''
        # Get current size of grid
        rpm_axis_size = self.GetNumberCols()
        load_axis_size = self.GetNumberRows()

        # Update table to reflect new size
        if rpm_axis_size < self.length_rpm:
            self.AppendCols(self.length_rpm - rpm_axis_size)

        if load_axis_size < self.length_load:
            self.AppendRows(self.length_load - load_axis_size)

        # Set axis labels
        i = 0
        while i < self.length_rpm:
            self.SetColLabelValue(i, str(self.axis_rpm[i] / 2))
            self.SetColSize(i, 50)
            i += 1
        
        i = 0
        while i < self.length_load:
            self.SetRowLabelValue(i, '%.2f' % self.axis_load[i])
            i += 1

        rpm = 0
        while rpm < self.length_rpm:
            load = 0
            while load < self.length_load:
                self._updateCell(load, rpm)
                self.SetReadOnly(load, rpm)
                load += 1

            rpm += 1


    def highlightCell(self, event):
        '''
        Highlight cell engine is currently using
        '''
        # Get realtime data
        data = gui.frame.windows['realtime_data'].interface.data

        # Get current rpm
        rpm_current = float(data['RPM']) / 2

        # Get current load
        load_current = float(data['LoadMain']) / float(512)

        # Find current rpm col
        rpm = 0
        for axis in self.axis_rpm:
            # If axis is equal to current or first col
            if axis == rpm_current or rpm == 0:
                break

            # If axis is larger than current
            if axis > rpm_current:
                # Find distance to this axis
                dist_up = axis - rpm_current

                # Find distance from last axis
                dist_down = rpm_current - self.axis_rpm[rpm-1]

                # If lower axis is closer, use that one
                if dist_up > dist_down:
                    rpm -= 1

                break
            rpm += 1

        rpm = min(rpm, self.length_rpm-1)

        # Find current load row
        load = 0
        for axis in self.axis_load:
            # If axis is equal to current or first row
            if axis == load_current or load == 0:
                break

            # If axis is larger than current
            if axis > load_current:
                # Find distance to this axis
                dist_up = axis - load_current

                # Find distance from last axis
                dist_down = load_current - self.axis_load[load-1]

                # If lower axis is closer, use that one
                if dist_up > dist_down:
                    load -= 1

                break
            load += 1

        load = min(load, self.length_load-1)

        # If highlighted cell has changed
        if self._highlighted != [load, rpm]:

            # Highlight cell
            self._updateCell(load, rpm, True)

            # Reset old highlighted cell
            if self._highlighted != None:
                self._updateCell(self._highlighted[0], self._highlighted[1])

            # Update var
            self._highlighted = [load, rpm]

        # Also update statusbar
        # Bit of a dirty hack for now
        sp1 = data['sp1']
        refpw = data['RefPW']
        diff = str(int(sp1) - int(refpw))

        gui.frame.statusbar.SetStatusText('SP1: %s' % sp1, 1)
        gui.frame.statusbar.SetStatusText('Ref PW: %s' % refpw, 2)
        gui.frame.statusbar.SetStatusText('Diff: %s' % diff, 3)


    def _updateCell(self, load, rpm, highlight = False):
        '''
        Update a cell's value
        '''
        # Create value string
        raw = float(self.cells[rpm][load])
        value = '%.1f' % (raw / float(512))
        self.SetCellValue(load, rpm, value)

        # Set background color
        # If highlighting
        if highlight:
            color = wx.Color(255, 255, 255)
        else:
            # Otherwise, make gradient
            red = max(min(int(raw / 255), 255), 0)
            green = max(min(int(255 - (raw / 255)), 255), 0)
            color = wx.Color(int(red), int(green), 0)

        self.SetCellBackgroundColour(load, rpm, color)
