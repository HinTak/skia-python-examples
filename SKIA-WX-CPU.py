#!/usr/bin/env python

# Copyright 2025, Prashant Saxena, https://github.com/prashant-saxena

# SKIA-WX-CPU Example

# See https://github.com/kyamagu/skia-python/issues/323

# python imports
import math
import ctypes
# pip imports
import wx
import skia


"""Enable high-res displays."""
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass  # fail on non-windows


class SkiaCPUCanvas(wx.Panel):
    """A cpu based skia canvas"""

    def __init__(self, parent, size):
        super().__init__(parent, size=size)
        # or else we'll have a flicker
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.is_dragging = False
        self.last_mouse_pos = (0.0, 0.0)
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.zoom = 1.0

        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_mouse_left_down(self, event):
        self.is_dragging = True
        self.last_mouse_pos = (event.GetX(), event.GetY())
        event.Skip()

    def on_mouse_left_up(self, event):
        self.is_dragging = False
        event.Skip()

    def on_mouse_move(self, event):
        if self.is_dragging:
            xpos, ypos = event.GetX(), event.GetY()
            lx, ly = self.last_mouse_pos
            dx, dy = xpos - lx, ypos - ly
            self.offset_x += dx / self.zoom
            self.offset_y += dy / self.zoom
            self.last_mouse_pos = (xpos, ypos)
            self.Refresh()
        event.Skip()

    def on_mouse_wheel(self, event):
        """Implement zoom to point"""
        x, y = event.GetX(), event.GetY()
        rotation = event.GetWheelRotation()

        if rotation > 1:
            zoom_factor = 1.1
        elif rotation < -1:
            zoom_factor = 0.9
        else:
            return

        old_zoom = self.zoom
        new_zoom = self.zoom * zoom_factor

        # Convert screen coords to centered canvas coords
        cx, cy = self.size[0] / 2, self.size[1] / 2
        dx = x - cx
        dy = y - cy

        # World coords under mouse before zoom
        world_x = (dx / old_zoom) - self.offset_x
        world_y = (dy / old_zoom) - self.offset_y

        # Apply zoom
        self.zoom = new_zoom

        # Adjust offset so world point stays under cursor
        self.offset_x = (dx / self.zoom) - world_x
        self.offset_y = (dy / self.zoom) - world_y

        self.Refresh()

    def on_paint(self, event):
        w, h = self.GetSize()
        if w == 0 or h == 0:
            return

        self.draw(w, h)

        image = self.surface.makeImageSnapshot()
        bitmap = wx.Bitmap.FromBufferRGBA(w, h, image.tobytes())

        dc = wx.PaintDC(self)
        dc.DrawBitmap(bitmap, 0, 0)

    def draw(self, w, h):
        sw, h = self.GetSize()
        if w == 0 or h == 0:
            return

        self.canvas.clear(skia.ColorWHITE)
        self.canvas.save()

        # Set up the translation and zoom (pan/zoom)
        self.canvas.translate(w / 2, h / 2)
        self.canvas.scale(self.zoom, self.zoom)
        self.canvas.translate(self.offset_x, self.offset_y)

        # Create a solid paint (Blue color, but explicitly defining RGBA)
        paint = skia.Paint(AntiAlias=True, Color=skia.Color(255, 0, 0),)

        # Draw a series of circles in a spiral pattern
        for i in range(150):
            angle = i * math.pi * 0.1
            x = math.cos(angle) * i * 3
            y = math.sin(angle) * i * 3
            # Draw solid circles
            self.canvas.drawCircle(x, y, 4 + (i % 4), paint)

        self.canvas.restore()

    def on_size(self, event):
        wx.CallAfter(self.set_size)
        event.Skip()

    def set_size(self):
        # Actual drawing area (without borders) is GetClientSize
        size = self.GetClientSize()
        # On HiDPI screens, this could be 1.25, 1.5, 2.0, etc.
        scale = self.GetContentScaleFactor()
        width = int(size.width * scale)
        height = int(size.height * scale)
        self.size = wx.Size(width, height)

        self.surface = skia.Surface.MakeRaster(skia.ImageInfo.MakeN32Premul(
            width, height).makeColorType(skia.ColorType.kRGBA_8888_ColorType))
        self.canvas = self.surface.getCanvas()

        self.Refresh()


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Skia Wx CPU Canvas", size=(800, 600))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.canvas = SkiaCPUCanvas(panel, (800, 600))
        sizer.Add(self.canvas, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
