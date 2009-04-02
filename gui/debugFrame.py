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


import wx, sys

import comms, version, libs.data


class debugFrame(wx.Frame):
    '''
    Debug info fFrame
    '''

    display = None

    def __init__(self, parent):
        '''
        Create a frame instance.
        '''
        wx.Frame.__init__(self, parent, id=-1, title='Debug Info', pos=wx.DefaultPosition, size=(500,300))

        self.BuildWindow()
        self.Center()
        self.Show()


    def BuildWindow(self):
        '''
        Build / position window elements
        '''
        self.window = window = wx.Panel(parent=self, id=-1)

        self.display = display = self.CreateDisplay(window) 

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add((0,0), 1)
        sizer2.Add(display, 18, wx.EXPAND)
        sizer2.Add((0,0), 1)

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add((0,0), 1)
        sizer1.Add(sizer2, 18, wx.EXPAND)
        sizer1.Add((0,0), 1)

        window.SetSizer(sizer1)
        window.Layout()
       

    def CreateDisplay(self, parent):
        '''
        Create info display box'''
        display = wx.TextCtrl(parent, -1, style=wx.SUNKEN_BORDER | wx.VSCROLL | wx.HSCROLL | wx.TE_MULTILINE)
        display.SetEditable(False)

        comm = comms.getConnection()

        data  = 'System:\n'
        data += '--------------------\n'
        data += 'Platform: %s\n' % sys.platform
        data += 'Python version: %s\n' % str(sys.version).replace('\n', '')
        data += 'Python path: %s\n' % sys.path
        data += 'wxPython version: %s\n\n' % wx.__version__

        data += 'FreeEMS:\n'
        data += '--------------------\n'
        data += 'Tuner version: %s\n' % version.__revision__
        data += 'Comms plugin: %s\n' % str(comm.__class__).split('\'')[1]
        data += 'Protocol plugin: %s\n' % comm.getProtocol().getProtocolName()
        data += 'Data directory: %s\n\n' % libs.data.getPath()

        data += 'Config:\n'
        data += '--------------------\n'

        configfile = open(libs.data.getPath() + '/my_config.cached.ini', 'r')
        data += ''.join(configfile.readlines())
        configfile.close()

        display.SetValue(data)

        return display

