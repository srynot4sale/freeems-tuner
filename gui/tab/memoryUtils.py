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

import gui.memoryRequestBlockIdDropMenu

logger = logging.getLogger('gui.tabs.memoryUtils')

# Helper value for inserting spacing into sizers
blank = (0,0)

class tab(wx.Panel):
    '''Memory utilities tab'''

    def __init__(self, parent):
        '''Setup interface elements'''
        wx.Panel.__init__(self, parent)

        self.memory_block_id_drop_menu = gui.memoryRequestBlockIdDropMenu.memoryRequestBlockIdDropMenu(self)

        # Try keep all spaces at 1/60th of the screen width or height
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(blank, 1)
        sizer1.Add(self.memory_block_id_drop_menu, 58, wx.EXPAND)
        sizer1.Add(blank, 1)

        self.SetSizer(sizer1)
        self.Layout()

