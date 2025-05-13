import wx

class FullDesktopFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.SetTitle("wxPython Full Desktop Window")
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.CAPTION))
        self.Maximize(True)  # Maximize the window to full desktop size

class MyApp(wx.App):
    def OnInit(self):
        frame = FullDesktopFrame(None)
        frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
