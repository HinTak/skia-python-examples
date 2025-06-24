import wx

class FileDialogDemo(wx.Frame):
    def __init__(self, *args, **kw):
        super(FileDialogDemo, self).__init__(*args, **kw)
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(400, 300))
        open_button = wx.Button(panel, label='Open File')
        open_button.Bind(wx.EVT_BUTTON, self.on_open_file)
        
        vbox.Add(self.text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(open_button, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)
        
        panel.SetSizer(vbox)
        self.SetTitle("wxPython File Dialog Demo")
        self.Centre()
        self.SetSize((500, 400))

    def on_open_file(self, event):
        with wx.FileDialog(self, "Open Text file", wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            path = fileDialog.GetPath()
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text.SetValue(content)
            except Exception as e:
                wx.LogError(f"Cannot open file '{path}'.\n{str(e)}")

if __name__ == '__main__':
    app = wx.App(False)
    frame = FileDialogDemo(None)
    frame.Show()
    app.MainLoop()