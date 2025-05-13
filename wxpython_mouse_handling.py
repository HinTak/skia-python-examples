import wx

class MouseHandlingFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.SetTitle("wxPython Mouse Handling")
        self.SetSize((800, 600))

        # Bind mouse events
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_button_down)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_button_down)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_mouse_button_down)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)

    def on_mouse_motion(self, event):
        pos = event.GetPosition()
        print(f"Mouse moved: ({pos.x}, {pos.y})")

    def on_mouse_button_down(self, event):
        button = event.GetButton()
        print(f"Mouse button pressed: {button}")

    def on_mouse_wheel(self, event):
        wheel_delta = event.GetWheelRotation()
        print(f"Mouse wheel scrolled: {wheel_delta}")

class MyApp(wx.App):
    def OnInit(self):
        frame = MouseHandlingFrame(None)
        frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
