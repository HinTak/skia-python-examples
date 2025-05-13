import wx

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wxPython Mouse Event Example", size=(800, 600))
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)

    def on_mouse_down(self, event):
        pos = event.GetPosition()
        print(f"Mouse Button Down at {pos.x}, {pos.y}")

    def on_mouse_motion(self, event):
        if event.Dragging():
            pos = event.GetPosition()
            print(f"Mouse Dragging to {pos.x}, {pos.y}")

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
