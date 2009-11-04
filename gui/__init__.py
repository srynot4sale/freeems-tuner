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


import wx, os, datetime
import version, comms, settings
import libs.config as config, libs.data as data

import debugFrame, commsTestFrame, tab.main, tab.realtimeData, tab.memoryUtils, tab.table


# Create event id's
ID_EXIT = wx.ID_EXIT

ID_UNDO = wx.ID_UNDO
ID_REDO = wx.ID_REDO

ID_TOGGLE_MAXIMIZE = wx.NewId()
ID_TAB_POPOUT = wx.NewId()

ID_COMMS_CONNECT = wx.NewId()
ID_COMMS_DISCONNECT = wx.NewId()
ID_COMMS_RECORDING_START = wx.NewId()
ID_COMMS_RECORDING_STOP = wx.NewId()
ID_COMMS_TESTS = wx.NewId()
ID_COMMS_DATA_UPDATE = wx.NewId()

ID_ABOUT = wx.ID_ABOUT
ID_HELP = wx.NewId()
ID_DEBUG_FRAME = wx.NewId()


# Instance of the parent frame
frame = None


class Frame(wx.Frame):
    """Frame with standard menu items."""

    _controller = None

    revision = version.__revision__
    menus = {}
    tabctrl = None
    windows = {}
    statusbar = None

    # Iconized state (minimized)
    iconized = None

    def __init__(self, controller):
        """Create a Frame instance."""
        wx.Frame.__init__(self, parent = None, id = -1, size = (800,600))

        self._controller = controller

        self._debug('Gui frame initialised')

        self._updateStatus()

        self._createMenus()

        self.iconized = False

        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ICONIZE, self.OnIconize)

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


    def getController(self):
        return self._controller


    def _debug(self, message, data = None):
        '''
        Send debug log message to controller
        '''
        self._controller.log(
            'gui',
            'DEBUG',
            message,
            data
        )


    def BuildWindow(self):
        '''Build and place widgets'''

        # Build tab bar
        self.tabctrl = tabctrl = wx.Notebook(self)

        # Build main window
        self.windows['main'] = window_main = tab.main.tab(self.tabctrl)
        self.windows['memory_utils'] = window_memory_utils = tab.memoryUtils.tab(self.tabctrl)
        self.windows['realtime_data'] = window_realtime_data = tab.realtimeData.tab(self.tabctrl)
        self.windows['table'] = window_table = tab.table.tab(self.tabctrl)
        tabctrl.AddPage(window_main, 'Main')
        tabctrl.AddPage(window_memory_utils, 'Memory Utils')
        tabctrl.AddPage(window_realtime_data, 'Real-Time Data')
        tabctrl.AddPage(window_table, 'Tuning Table')


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
            settings.saveSettings(self._controller)
        except Exception, msg:
            self._debug('Error during shutdown', msg)

        self._controller.shutdown()
        self.Destroy()


    def _updateStatus(self):
        '''
        Updates window title and statusbar text
        '''
        # Generate title
        title = version.__title__

        # Set title
        self.SetTitle(title)

        # Set up statusbar
        if not self.statusbar:
            self.statusbar = wx.StatusBar(self, wx.ID_ANY)

        comm = comms.getConnection()

        fields = [
            'Interface: %s' % comm.getProtocol().getProtocolName(),
            '',
            '',
            '',
            '',
            'Connection: %s' % comm.getTitle()
        ]
        self.statusbar.SetFields(fields)

        self.SetStatusBar(self.statusbar)


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
        m.Append(ID_COMMS_RECORDING_START, '&Start Recording', 'Start recording comms data')
        m.Append(ID_COMMS_RECORDING_STOP, 'S&top Recording', 'Stop recording comms data')
        m.AppendSeparator()
        #m.Append(ID_COMMS_DATA_UPDATE, '&Update Comms Data Settings...', 'Update Comms Data Settings')
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
        self.Bind(wx.EVT_MENU, self.CommsRecordingStart, id=ID_COMMS_RECORDING_START)
        self.Bind(wx.EVT_MENU, self.CommsRecordingStop, id=ID_COMMS_RECORDING_STOP)
        #self.Bind(wx.EVT_MENU, self.CommsUpdateData, id=ID_COMMS_DATA_UPDATE)
        self.Bind(wx.EVT_MENU, self.CommsTests, id=ID_COMMS_TESTS)

        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=ID_HELP)
        self.Bind(wx.EVT_MENU, self.ShowDebugFrame, id=ID_DEBUG_FRAME)
        
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COMMS_CONNECT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COMMS_DISCONNECT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COMMS_RECORDING_START)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COMMS_RECORDING_STOP)
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
            self._controller._error(msg)

    
    def CommsUpdateData(self, event):
        '''Update comms data'''
        file_dialog = wx.FileDialog(self, 'Select Data Package')#, style = wx.FD_OPEN)
        file_dialog.ShowModal()
        path = file_dialog.GetDirectory()
        path += '/'+file_dialog.GetFilename()
        
        if data.installProtocolDataFiles(path):
            dialog = wx.MessageDialog(
                    self,
                    'Comms data settings successfully updated',
                    'Update Successful',
                    wx.OK | wx.ICON_INFORMATION)

        else:
            dialog = wx.MessageDialog(
                    self,
                    'Comms data setting update failed',
                    'Update Failed', 
                    wx.OK | wx.ICON_ERROR)

        dialog.ShowModal()
        dialog.Destroy()


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


    def CommsIsConnected(self):
        '''
        Check if comms is connected
        '''
        return comms.getConnection().isConnected()


    def CommsRecordingStart(self, event):
        '''
        Start recording comms
        '''
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')

        dialog = wx.FileDialog(
                parent = self,
                message = 'Comms Log File',
                defaultDir = 'data/',
                defaultFile = 'comms' + timestamp + '.bin',
                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        dialog.ShowModal()

        comms.getConnection().startRecording(dialog.GetPath())


    def CommsRecordingStop(self, event):
        '''
        Stop recording comms
        '''
        comms.getConnection().stopRecording()


    def CommsCanStartRecording(self):
        '''
        Can the user start recording
        '''
        return self.CommsIsConnected() and not self.CommsIsRecording()


    def CommsIsRecording(self):
        '''
        Check if comms is recording
        '''
        return comms.getConnection().isRecording()


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
            elif id == ID_COMMS_RECORDING_START:
                event.Enable(self.CommsCanStartRecording())
            elif id == ID_COMMS_RECORDING_STOP:
                event.Enable(self.CommsIsRecording())
            else:
                event.Enable(False)
        except AttributeError:
            # This menu option is not supported in the current context.
            event.Enable(False)


# Bring up wxpython interface
def load(controller):

    application = wx.App()
        
    global frame
    frame = Frame(controller)
    frame.Show()

    application.MainLoop()
