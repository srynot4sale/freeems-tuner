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
import logging


logger = logging.getLogger('gui.tabs.debugLog')

# Helper value for inserting spacing into sizers
blank = (0,0)

class tab(wx.Panel):
    '''Debug log tab'''

    def __init__(self, parent):
        '''Setup interface elements'''
        wx.Panel.__init__(self, parent)

        self.display = display = wx.TextCtrl(self, -1, style=wx.SUNKEN_BORDER | wx.VSCROLL | wx.TE_MULTILINE)
        display.SetEditable(False)

        # Try keep all spaces at 1/60th of the screen width or height
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(blank, 1)
        sizer2.Add(self.display, 58, wx.EXPAND)
        sizer2.Add(blank, 1)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(blank, 1)
        sizer1.Add(sizer2, 58, wx.EXPAND)
        sizer1.Add(blank, 1)

        self.SetSizer(sizer1)
        self.Layout()

        # Add a logger
        base = logging.getLogger()
        base.addHandler(self.loggingHandler(self))


    def updateDisplay(self, message):
        '''Add a new line to the display'''
        self.display.SetValue(self.display.GetValue() + str(message) + '\n')
    
    
    class loggingHandler(logging.Handler):
        '''Logging handler for printing to this display'''

        # UI elements with a updateDisplay method
        _display = None

        def __init__(self, display):
            '''Setup any defaults, important vars'''
            logging.Handler.__init__(self)

            # Save UI elements
            self._display = display

    
        def emit(self, record):
            '''Actually print the logging record'''

            #! Important, formats message nicely
            msg = self.format(record)

            self._display.updateDisplay(msg)
