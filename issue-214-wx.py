# Copyright 2025, Hin-Tak Leung

import wx
from wx.glcanvas import GLCanvas, GLContext
import skia
from OpenGL.GL import glViewport, GL_RGBA8, glClear, GL_COLOR_BUFFER_BIT

path = skia.Path()
path.moveTo(184, 445)
path.lineTo(249, 445)
path.quadTo(278, 445, 298, 438)
path.quadTo(318, 431, 331, 419)
path.quadTo(344, 406, 350, 390)
path.quadTo(356, 373, 356, 354)
path.quadTo(356, 331, 347, 312)
path.quadTo(338, 292, 320, 280)
path.close()

class WxGLCanvas(GLCanvas):
    def __init__(self, parent, size):
        GLCanvas.__init__(self, parent, -1, size=size)
        self.glctx = GLContext(self)
        self.size = wx.Size(size[0], size[1])
        self.skia_surface = None
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def init_Skia(self):
        self.SetCurrent(self.glctx)
        glViewport(0, 0, self.size.width, self.size.height)

        context = skia.GrDirectContext.MakeGL()
        backend_render_target = skia.GrBackendRenderTarget(
            self.size.width, self.size.height, 0, 0, skia.GrGLFramebufferInfo(
                0, GL_RGBA8)
        )
        self.skia_surface = skia.Surface.MakeFromBackendRenderTarget(
            context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB()
        )

    def on_paint(self, event):
        if not self.skia_surface:
            self.init_Skia()
        self.draw()
        self.SwapBuffers()

    # Not a event
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)

        with self.skia_surface as canvas:
            canvas.drawCircle(100, 100, 40, skia.Paint(Color=skia.ColorGREEN, AntiAlias=True))
            paint = skia.Paint(Color=skia.ColorBLUE)
            paint.setStyle(skia.Paint.kStroke_Style)
            paint.setStrokeWidth(2)
            paint.setAntiAlias(True)
            
            canvas.drawPath(path, paint)
        self.skia_surface.flushAndSubmit()

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Skia WxPython GPU Canvas", size=(640, 480))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.wxcanvas = WxGLCanvas(panel, (640, 480))
        sizer.Add(self.wxcanvas, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Show()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
