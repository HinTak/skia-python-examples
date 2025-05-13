import wx

class ResizableFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.SetTitle("wxPython Window Resizing")
        self.SetSize((800, 600))

        # Bind the resize event
        self.Bind(wx.EVT_SIZE, self.on_resize)

    def on_resize(self, event):
        size = self.GetSize()
        print(f"Window resized to: {size.width}x{size.height}")
        event.Skip()  # Ensure the event propagates to the default handler

class MyApp(wx.App):
    def OnInit(self):
        frame = ResizableFrame(None)
        frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
