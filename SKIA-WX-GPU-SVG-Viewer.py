#!/usr/bin/env python

# Simple SVG viewer with pan and zoom functionality, Copyright 2025 Hin-Tak Leung

# Adapted from SKIA-WX-GPU Example submitted by
#     Copyright 2025, Prashant Saxena https://github.com/prashant-saxena
#     to https://github.com/kyamagu/skia-python/issues/323

# python imports
import math
import ctypes
# pip imports
import wx
from wx import glcanvas
import skia
from OpenGL.GL import glViewport, GL_RGBA8


"""Enable high-res displays."""
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass  # fail on non-windows


class SkiaWxGPUCanvas(glcanvas.GLCanvas):
    """A skia based GlCanvas"""

    def __init__(self, parent, size):
        glcanvas.GLCanvas.__init__(self, parent, -1, size=size)
        self.glctx = glcanvas.GLContext(self)  # ✅ Correct GLContext
        self.size = wx.Size(size[0], size[1])
        self.glinit = False
        self.canvas = None
        self.surface = None
        self.is_dragging = False
        self.last_mouse_pos = (0.0, 0.0)
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.zoom = 1.0

        self.svg_picture = None
        self.img_size = None
        self.img_scale_enum = 0
        self.img_zoom = 1.0

        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        # Do nothing, to avoid flashing on MSW.
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None)

    def init_gl(self):
        """Initialize Skia GPU context and surface."""
        context = skia.GrDirectContext.MakeGL()
        backend_render_target = skia.GrBackendRenderTarget(
            self.size.width, self.size.height, 0, 0, skia.GrGLFramebufferInfo(
                0, GL_RGBA8)
        )
        self.surface = skia.Surface.MakeFromBackendRenderTarget(
            context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB()
        )
        self.canvas = self.surface.getCanvas()
        self.glinit = True

    def on_paint(self, event):
        """Handle drawing."""

        if not self.glinit:
            self.SetCurrent(self.glctx)
            glViewport(0, 0, self.size.width, self.size.height)
            self.init_gl()

        # This is your actual skia based drawing function
        self.on_draw()

        self.SwapBuffers()

    def on_key_down(self, event):
        keycode = event.GetKeyCode()
        if ((keycode == 43) or # '+'
            (keycode == 45)):  # '-'
            self.img_scale_enum += (44 - keycode)
            self.img_zoom = 1.2 ** self.img_scale_enum
            self.Refresh()
        event.Skip()

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

    def on_draw(self):
        """Draw on Skia canvas."""
        w, h = self.GetSize()
        if w == 0 or h == 0:
            return
        glViewport(0, 0, self.size.width, self.size.height)

        self.canvas.clear(skia.ColorWHITE)
        self.canvas.save()

        # Set up the translation and zoom (pan/zoom)
        self.canvas.translate(w / 2, h / 2)
        self.canvas.scale(self.zoom, self.zoom)
        self.canvas.translate(self.offset_x, self.offset_y)

        if self.svg_picture:
            self.canvas.scale(self.img_zoom, self.img_zoom)
            self.canvas.translate(-self.img_size.width()/2, -self.img_size.height()/2)
            self.svg_picture.render(self.canvas)
            self.canvas.translate(self.img_size.width()/2, self.img_size.height()/2)
            self.canvas.scale(1/self.img_zoom, 1/self.img_zoom)

        self.canvas.restore()
        self.surface.flushAndSubmit()

    def on_size(self, event):
        """Handle resizing of the canvas."""
        self.glinit = False
        wx.CallAfter(self.set_viewport)
        event.Skip()

    def set_viewport(self):
        # Actual drawing area (without borders) is GetClientSize
        size = self.GetClientSize()
        # On HiDPI screens, this could be 1.25, 1.5, 2.0, etc.
        scale = self.GetContentScaleFactor()
        width = int(size.width * scale)
        height = int(size.height * scale)
        self.size = wx.Size(width, height)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Skia WxPython GPU Canvas", size=(800, 600))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        open_button = wx.Button(panel, label='Open File')
        open_button.Bind(wx.EVT_BUTTON, self.on_open_file)
        sizer.Add(open_button, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

        self.canvas = SkiaWxGPUCanvas(panel, (800, 600))
        sizer.Add(self.canvas, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Show()

    def on_open_file(self, event):
        with wx.FileDialog(self, "Open SVG file", wildcard="Scalable Vector Graphics (*.svg)|*.svg|All files (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            path = fileDialog.GetPath()
            try:
                svgstream = skia.Stream.MakeFromFile(path)
                self.canvas.svg_picture = skia.SVGDOM.MakeFromStream(svgstream)
                self.canvas.img_size = self.canvas.svg_picture.containerSize()
                self.canvas.Refresh()
                self.canvas.SetFocus()
            except Exception as e:
                wx.LogError(f"Cannot open file '{path}'.\n{str(e)}")

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
