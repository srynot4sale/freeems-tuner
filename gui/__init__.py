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
import os
import version
import comms
import protocols
import logging
import libs.config as config
import settings

import commsTestFrame
import tab.main
import tab.debugLog


logger = logging.getLogger('gui')


# Create event id's
ID_EXIT = wx.ID_EXIT

ID_UNDO = wx.ID_UNDO
ID_REDO = wx.ID_REDO

ID_TOGGLE_MAXIMIZE = wx.NewId()
ID_TAB_POPOUT = wx.NewId()

ID_COMMS_CONNECT = wx.NewId()
ID_COMMS_DISCONNECT = wx.NewId()
ID_COMMS_TESTS = wx.NewId()

ID_ABOUT = wx.ID_ABOUT
ID_HELP = wx.NewId()
ID_DEBUG_FRAME = wx.NewId()


# Instance of the parent frame
frame = None


class Frame(wx.Frame):
    """Frame with standard menu items."""

    revision = version.__revision__
    menus = {}
    tabctrl = None
    windows = {}

    # Iconized state (minimized)
    iconized = None

    def __init__(self, parent=None, id=-1, title=version.__title__,
                 pos=wx.DefaultPosition, size=(800,600), 
                 style=wx.DEFAULT_FRAME_STYLE):
        """Create a Frame instance."""
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        settings.loadSettings()

        self.CreateStatusBar()
        self.SetStatusText('Version %s' % self.revision)
        self._createMenus()

        self.iconized = False

        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ICONIZE, self.OnIconize)

        # Handle incoming comms and settings when the UI is idle
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        self.BuildWindow()

        # Load saved location/size settings
        x = settings.get('win.main.pos.x', -1)
        y = settings.get('win.main.pos.y', -1)
        pos  = wx.Point(int(x), int(y))
        
        h = settings.get('win.main.size.h', -1)
        w = settings.get('win.main.size.w', -1)
        size = wx.Size(int(h), int(w))

        self.SetSize(size)
        self.Move(pos)


    def BuildWindow(self):
        '''Build and place widgets'''

        # Build tab bar
        self.tabctrl = tabctrl = wx.Notebook(self)

        # Build main window
        self.windows['main'] = window_main = tab.main.tab(self.tabctrl)
        self.windows['debug'] = window_debug = tab.debugLog.tab(self.tabctrl)
        tabctrl.AddPage(window_main, 'Main')
        tabctrl.AddPage(window_debug, 'Debug Log')


    def OnIdle(self, event = None):
        '''Idle UI handler'''
        # Save window settings
        settings.saveSettings()

        # Handle comms receive logic
        self.CommsReceive()


    def OnMove(self, event):
        '''Event handler for moving window'''
        if self.iconized or self.IsMaximized():
            return

        h, w = self.GetSize()
        settings.set('win.main.size.h', h)
        settings.set('win.main.size.w', w)
            
        x, y = self.GetPosition()
        settings.set('win.main.pos.x', x)
        settings.set('win.main.pos.y', y)


    def OnIconize(self, event):
        """Event handler for Iconize."""
        self.iconized = event.Iconized()


    def OnClose(self, event):
        '''Event handler for closing.'''
        try:
            # Save any unsaved settings
            settings.saveSettings()
        except Exception, msg:
            logger.error(msg)
            logger.error('Error during shutdown')

        self.Destroy()


    def _createMenus(self):
        # File
        m = self.menus['file'] = wx.Menu()
        m.Append(ID_EXIT, 'E&xit\tCtrl+Q', 'Exit Program')

        # Edit
        m = self.menus['edit'] = wx.Menu()
        m.Append(ID_UNDO, '&Undo \tCtrl+Z',
                 'Undo the last action')
        m.Append(ID_REDO, '&Redo \tCtrl+Y',
                 'Redo the last undone action')

        # View
        m = self.menus['view'] = wx.Menu()
        m.Append(ID_TOGGLE_MAXIMIZE, '&Toggle Maximize\tF11', 'Maximize/Restore Application')
        m.Append(ID_TAB_POPOUT, 'Tab Pop&out', 'Turn current tab into its own window')

        # Comms
        m = self.menus['comms'] = wx.Menu()
        m.Append(ID_COMMS_CONNECT, '&Connect', 'Connect To Comms Port')
        m.Append(ID_COMMS_DISCONNECT, '&Disconnect', 'Disconnect From Comms Port')
        m.AppendSeparator()
        m.Append(ID_COMMS_TESTS, 'Interface Protocol &Test...', 'Run interface tests on firmware')

        # Help
        m = self.menus['help'] = wx.Menu()
        m.Append(ID_HELP, '&Help\tF1', 'Help!')
        m.AppendSeparator()
        m.Append(ID_ABOUT, '&About...', 'About this program')
        m.Append(ID_DEBUG_FRAME, '&Debug Info...', 'Show system information for debugging purposes')

        b = self.menu_bar = wx.MenuBar()
        b.Append(self.menus['file'], '&File')
        b.Append(self.menus['edit'], '&Edit')
        b.Append(self.menus['view'], '&View')
        b.Append(self.menus['comms'], '&Comms')
        b.Append(self.menus['help'], '&Help')
        self.SetMenuBar(b)

        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)

        self.Bind(wx.EVT_MENU, self.OnUndo, id=ID_UNDO)
        self.Bind(wx.EVT_MENU, self.OnRedo, id=ID_REDO)

        self.Bind(wx.EVT_MENU, self.OnToggleMaximize, id=ID_TOGGLE_MAXIMIZE)

        self.Bind(wx.EVT_MENU, self.CommsConnect, id=ID_COMMS_CONNECT)
        self.Bind(wx.EVT_MENU, self.CommsDisconnect, id=ID_COMMS_DISCONNECT)
        self.Bind(wx.EVT_MENU, self.CommsTests, id=ID_COMMS_TESTS)

        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=ID_HELP)
        self.Bind(wx.EVT_MENU, self.ShowDebugFrame, id=ID_DEBUG_FRAME)

        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COMMS_CONNECT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COMMS_DISCONNECT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COMMS_TESTS)
        

    def OnToggleMaximize(self, event):
        self.Maximize(not self.IsMaximized())


    def OnExit(self, event):
        self.Close(False)


    def OnUndo(self, event):
        win = wx.Window.FindFocus()
        win.Undo()


    def OnRedo(self, event):
        win = wx.Window.FindFocus()
        win.Redo()


    def OnAbout(self, event):
        """Display an About window."""

        title = version.__name__
        text  = 'Version %s\n\n' % version.__revision__
        text += 'Written by Aaron Barnes\n'
        text += 'FreeEMS-Tuner is not to be used while intoxicated. Seriously.\n\n'
        text += 'More info at http://www.diyefi.org/\n\n'
        text += 'Licence information can be found in the LICENCE file'

        dialog = wx.MessageDialog(self, text, title,
                                  wx.OK | wx.ICON_INFORMATION)
        dialog.ShowModal()
        dialog.Destroy()


    def OnHelp(self, event):
        """Display a Help window."""
        title = 'Help'        
        text = "Type 'shell.help()' in the shell window."
        dialog = wx.MessageDialog(self, text, title,
                                  wx.OK | wx.ICON_INFORMATION)
        dialog.ShowModal()
        dialog.Destroy()


    def ShowDebugFrame(self, event):
        '''Show debug frame'''
        debugFrame.debugFrame(self)


    def CommsConnect(self, event = None):
        '''Connect comms'''
        if self.CommsIsConnected():
            return

        try:
            comms.getConnection().connect()

        except comms.CannotconnectException, msg:
            logger.error(msg)

    
    def CommsTests(self, event):
        '''Run comms unit tests'''
        if not self.CommsIsConnected():
            return

        test_frame = commsTestFrame.commsTestFrame(self)


    def CommsDisconnect(self, event):
        '''Disconnect comms'''
        if not self.CommsIsConnected():
            return

        comms.getConnection().disconnect()


    def CommsReceive(self, event = None):
        '''Check for any packets in the buffer'''
        if not self.CommsIsConnected():
            return

        comms.getConnection().recieve()


    def CommsIsConnected(self):
        '''Check if comms is connected'''
        return comms.getConnection().isConnected()


    def OnUpdateMenu(self, event):
        """Update menu items based on current status and context."""
        win = wx.Window.FindFocus()
        id = event.GetId()
        event.Enable(True)
        try:
            if id == ID_UNDO:
                event.Enable(win.CanUndo())
            elif id == ID_REDO:
                event.Enable(win.CanRedo())
            elif id == ID_COMMS_CONNECT:
                event.Enable(not self.CommsIsConnected())
            elif id == ID_COMMS_DISCONNECT:
                event.Enable(self.CommsIsConnected())
            elif id == ID_COMMS_TESTS:
                event.Enable(self.CommsIsConnected())
            else:
                event.Enable(False)
        except AttributeError:
            # This menu option is not supported in the current context.
            event.Enable(False)


# Bring up wxpython interface
def load():
    
    app = wx.App()

    global frame
    frame = Frame()
    frame.Show()

    app.MainLoop()

    return app


#########################################################
# User-defined layout main page
# NOTE: This an example. not currently used
def layout(frame):

    # We have a 10 x 10 grid to layout in

    # frame.place() parameters:
    # - int, horizontal axis, top left of element
    # - int, vertical axis, top left of element
    # - element object
    # - non default height of element
    # - non default width of element

    # commsDiagnostics is flexible
    frame.place(0, 0, commsDiagnostics(), 5, 10) 
    
    # commsUtilityRequests is 3x3
    frame.place(6, 0, commsUtilityRequests()) 


