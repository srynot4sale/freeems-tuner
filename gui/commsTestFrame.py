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


import wx, datetime

import comms, settings


ID_START_TESTS = wx.NewId()
ID_CLOSE = wx.NewId()


window = None


class commsTestFrame(wx.Frame):
    '''
    Comms Testing Frame
    '''

    def __init__(self, parent):
        '''
        Create a Frame instance.
        '''
        wx.Frame.__init__(self, parent, id=-1, title='Comms Test', pos=wx.DefaultPosition, size=(600,350))

        self.Bind(wx.EVT_MOVE, self.OnMove)

        self.BuildWindow()

        # Load saved location/size settings
        x = settings.get('win.commstest.pos.x', -1)
        y = settings.get('win.commstest.pos.y', -1)
        pos  = wx.Point(int(x), int(y))
        self.Move(pos)

        self.Show()

        global window
        window = self


    def BuildWindow(self):
        '''
        Biuld window gui elements
        '''

        self.window = window = wx.Panel(parent=self, id=-1)

        self.textbox = textbox = wx.TextCtrl(window, -1)
        start_button = wx.Button(window, ID_START_TESTS, 'Start Tests')
        stop_button = wx.Button(window, -1, 'Stop Tests')
        close_button = wx.Button(window, ID_CLOSE, 'Close')

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(start_button, 2)
        sizer3.Add((0,0), 1)
        sizer3.Add(stop_button, 2)
        sizer3.Add((0,0), 11)
        sizer3.Add(close_button, 2)
        
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add((0,0), 1)
        sizer2.Add(textbox, 10, wx.EXPAND)
        sizer2.Add((0,0), 1)
        sizer2.Add(sizer3, 7, wx.EXPAND)
        sizer2.Add((0,0), 1)

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add((0,0), 1)
        sizer1.Add(sizer2, 18, wx.EXPAND)
        sizer1.Add((0,0), 1)

        window.SetSizer(sizer1)
        
        # Bind events to buttons
        self.Bind(wx.EVT_BUTTON, self.exit, id=ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self.startTests, id=ID_START_TESTS)

        window.Layout()


    def OnMove(self, event):
        '''
        Event handler for moving window
        '''
        x, y = self.GetPosition()
        settings.set('win.commstest.pos.x', x)
        settings.set('win.commstest.pos.y', y)


    def exit(self, event):
        '''
        Close test window
        '''
        self.Close()


    def startTests(self, event = None):
        '''
        Run comms tests
        '''
        self.logAppend('Starting comms tests')
        self.controller.action('comms.runTest', {'window': self})
       

    def logAppend(self, message):
        '''
        Append to log
        '''
        self.textbox.AppendText(message)
