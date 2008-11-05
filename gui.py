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
import wx.grid as grid
import os
import __main__ as main
import comms
import protocols
import logging
import datetime

logger = logging.getLogger('gui')


# Create event id's
ID_NEW = wx.ID_NEW
ID_OPEN = wx.ID_OPEN
ID_EXIT = wx.ID_EXIT
ID_UNDO = wx.ID_UNDO
ID_REDO = wx.ID_REDO
ID_ABOUT = wx.ID_ABOUT
ID_HELP = wx.NewId()
ID_TOGGLE_MAXIMIZE = wx.NewId()
ID_COMMS_CONNECT = wx.NewId()
ID_COMMS_DISCONNECT = wx.NewId()


# Instance of the parent frame
frame = None


class Frame(wx.Frame):
    """Frame with standard menu items."""

    revision = main.__revision__
    menus = {}

    def __init__(self, parent=None, id=-1, title=main.__title__,
                 pos=wx.DefaultPosition, size=(800,600), 
                 style=wx.DEFAULT_FRAME_STYLE):
        """Create a Frame instance."""
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.CreateStatusBar()
        self.SetStatusText('Version %s' % self.revision)
        self.__createMenus()

        self.iconized = False

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ICONIZE, self.OnIconize)

        # Handle incoming comms when the UI is idle
        self.Bind(wx.EVT_IDLE, self.CommsRecieve)

        self.BuildWindow()


    def BuildWindow(self):

        self.window = window = wx.Panel(parent=self, id=-1)
        
        window.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
       
        ctrl_h = wx.BoxSizer(wx.HORIZONTAL)

        self.requests = commsUtilityRequests(window)
        self.button = commsUtilityFirmwareResetButton(window)

        ctrl_h.Add((0,0), 1)
        ctrl_h.Add(self.requests, 10, wx.EXPAND)
        ctrl_h.Add((0,0), 20)
        ctrl_h.Add(self.button, 10, wx.EXPAND)
        ctrl_h.Add((0,0), 1)

        self.comms = commsDiagnostics(window)

        sizer.Add(self.comms, 20, wx.EXPAND)
        sizer.Add((0,0), 1)
        sizer.Add(ctrl_h, 5, wx.EXPAND)

        window.SetSizer(sizer)
        window.Layout()


    def OnIconize(self, event):
        """Event handler for Iconize."""
        self.iconized = event.Iconized()


    def OnClose(self, event):
        """Event handler for closing."""
        self.Destroy()


    def __createMenus(self):
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

        # Comms
        m = self.menus['comms'] = wx.Menu()
        m.Append(ID_COMMS_CONNECT, '&Connect', 'Connect To Comms Port')
        m.Append(ID_COMMS_DISCONNECT, '&Disconnect', 'Disconnect From Comms Port')

        # Help
        m = self.menus['help'] = wx.Menu()
        m.Append(ID_HELP, '&Help\tF1', 'Help!')
        m.AppendSeparator()
        m.Append(ID_ABOUT, '&About...', 'About this program')

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
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnToggleMaximize, id=ID_TOGGLE_MAXIMIZE)
        self.Bind(wx.EVT_MENU, self.CommsConnect, id=ID_COMMS_CONNECT)
        self.Bind(wx.EVT_MENU, self.CommsDisconnect, id=ID_COMMS_DISCONNECT)

        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COMMS_CONNECT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COMMS_DISCONNECT)
        

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
        title = 'About '+main.__name__
        text  = 'Written by Aaron Barnes\n'
        text += 'More info at http://www.diyefi.org/\n\n'
        text += 'Version: '+main.__revision__+'\n\n'
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


    def CommsConnect(self, event):
        '''Connect comms'''
        if self.CommsIsConnected():
            return

        try:
            comms.getConnection().connect()

        except comms.CannotconnectException, msg:
            logger.error(msg)


    def CommsDisconnect(self, event):
        '''Disconnect comms'''
        if not self.CommsIsConnected():
            return

        comms.getConnection().disconnect()


    def CommsRecieve(self, event):
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
            else:
                event.Enable(False)
        except AttributeError:
            # This menu option is not supported in the current context.
            event.Enable(False)


    def OnActivate(self, event):
        """
        Event Handler for losing the focus of the Frame. Should close
        Autocomplete listbox, if shown.
        """
        if not event.GetActive():
            # If autocomplete active, cancel it.  Otherwise, the
            # autocomplete list will stay visible on top of the
            # z-order after switching to another application
            win = wx.Window.FindFocus()
            if hasattr(win, 'AutoCompActive') and win.AutoCompActive():
                win.AutoCompCancel()
        event.Skip()


    def LoadSettings(self, config):
        """Called be derived classes to load settings specific to the Frame"""
        pos  = wx.Point(config.ReadInt('Window/PosX', -1),
                        config.ReadInt('Window/PosY', -1))
                        
        size = wx.Size(config.ReadInt('Window/Width', -1),
                       config.ReadInt('Window/Height', -1))

        self.SetSize(size)
        self.Move(pos)


    def SaveSettings(self, config):
        """Called by derived classes to save Frame settings to a wx.Config object"""

        # TODO: track position/size so we can save it even if the
        # frame is maximized or iconized.
        if not self.iconized and not self.IsMaximized():
            w, h = self.GetSize()
            config.WriteInt('Window/Width', w)
            config.WriteInt('Window/Height', h)
            
            px, py = self.GetPosition()
            config.WriteInt('Window/PosX', px)
            config.WriteInt('Window/PosY', py)


# Bring up wxpython interface
def load():
    
    app = wx.App()
    frame = Frame()
    frame.Show()
    app.MainLoop()

    return app


class commsUtilityRequests(wx.BoxSizer):

    options = {}
    text = None
    input = None
    send = None

    ID_SEND_REQUEST = wx.NewId()


    def __init__(self, parent):

        wx.BoxSizer.__init__(self, wx.VERTICAL)

        self.text = wx.StaticText(parent, -1, 'Data to request', style=wx.ALIGN_CENTER)

        self.options = protocols.getProtocol().getUtilityRequestList()

        self.input = wx.Choice(parent, -1, choices=self.options)
        self.send = wx.Button(parent, self.ID_SEND_REQUEST, 'Send Request')

        self.Add((0,0), 1)
        self.Add(self.text, 3, wx.EXPAND)
        self.Add((0,0), 1)
        self.Add(self.input, 5, wx.EXPAND)
        self.Add((0,0), 1)
        self.Add(self.send, 5, wx.EXPAND)
        self.Add((0,0), 1)

        self.send.Bind(wx.EVT_BUTTON, self.sendRequest, id=self.ID_SEND_REQUEST)


    def sendRequest(self, event):
        
        selection = self.input.GetSelection()

        if selection < 0:
            selection = 0

        protocols.getProtocol().sendUtilityRequest(selection)


class commsUtilityFirmwareResetButton(wx.BoxSizer):

    options = {}
    button = None

    ID_SEND_FIRMWARE_RESET = wx.NewId()


    def __init__(self, parent):

        wx.BoxSizer.__init__(self, wx.VERTICAL)

        button_text  = 'The Big Red Button\n'
        button_text += '      (ECU Reset)'
        self.button = wx.Button(parent, self.ID_SEND_FIRMWARE_RESET, button_text)
        self.button.SetBackgroundColour(wx.RED)
        self.button.SetForegroundColour(wx.WHITE)

        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        self.button.SetFont(font)

        self.Add((0,0), 1)
        self.Add(self.button, 15, wx.EXPAND)
        self.Add((0,0), 1)

        self.button.Bind(wx.EVT_BUTTON, self.sendRequest, id=self.ID_SEND_FIRMWARE_RESET)


    def sendRequest(self, event):

        protocols.getProtocol().sendUtilityHardwareResetRequest()


class commsDiagnostics(grid.Grid):
    
    conn = None
    row = 0

    def __init__(self, parent):
        grid.Grid.__init__(self, parent)

        self.CreateGrid(1, 5)
        self.SetRowLabelSize(50)
        self.SetColLabelValue(0, 'Time')
        self.SetColSize(0, 120)
        self.SetColLabelValue(1, 'Flags')
        self.SetColSize(1, 60)
        self.SetColLabelValue(2, 'Pld Id')
        self.SetColSize(2, 70)
        self.SetColLabelValue(3, 'Payload')
        self.SetColSize(3, 150)
        self.SetColLabelValue(4, 'Raw Bytes')
        self.SetColSize(4, 300)

        self.conn = comms.getConnection()
        self.conn.bindSendWatcher(self.printSentPacket)
        self.conn.bindRecieveWatcher(self.printRecievedPacket)


    def printSentPacket(self, request):
       
        time = datetime.datetime.time(datetime.datetime.now())
        header = request.getHeaderFlags()
        payload_id = request.getPayloadId()
        payload = request.getPayload()
        raw_hex = request.getPacketHex()

        self.AppendRows()
        self.SetCellValue(self.row, 0, str(time))
        self.SetCellValue(self.row, 1, str(header))
        self.SetCellValue(self.row, 2, str(payload_id))
        self.SetCellValue(self.row, 3, str(payload))
        self.SetCellValue(self.row, 4, str(raw_hex))

        self.MakeCellVisible(self.row + 1, 1)
        self.ForceRefresh()

        self.row += 1

    
    def printRecievedPacket(self, request):

        time = datetime.datetime.time(datetime.datetime.now())
        header = 'rec'
        raw_hex = []

        for byte in request:
            hex_byte = hex(byte).upper().replace('X','x')

            if len(hex_byte) < 4:
                hex_byte = '0x0'+hex_byte[-1]

            raw_hex.append(hex_byte)

        self.AppendRows()

        self.SetCellValue(self.row, 0, str(time))
        self.SetCellValue(self.row, 1, str(header))
        self.SetCellValue(self.row, 4, str(raw_hex))
        
        self.MakeCellVisible(self.row + 1, 1)
        self.ForceRefresh()

        self.row += 1


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


