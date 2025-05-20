#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject
from OpenGL.GL import *
from skia import *
import random
import math

HELP_MESSAGE = "Click and drag to create rects. Press esc to quit."

class ApplicationState:
    def __init__(self, width, height):
        self.window_width = width
        self.window_height = height
        self.fRects = []
        self.drag_rect = None

def create_star():
    kNumPoints = 5
    path = Path()
    angle = 2 * math.pi / kNumPoints
    points = []
    for i in range(kNumPoints):
        theta = i * angle - math.pi / 2
        x = math.cos(theta) * 50
        y = math.sin(theta) * 50
        points.append((x, y))
    path.moveTo(*points[0])
    for i in range(kNumPoints):
        idx = (2 * i) % kNumPoints
        path.lineTo(*points[idx])
    path.setFillType(PathFillType.kEvenOdd)
    path.close()
    return path

class SkiaGLArea(Gtk.GLArea):
    def __init__(self):
        super().__init__()
        self.set_has_depth_buffer(False)
        self.set_has_stencil_buffer(True)
        self.set_required_version(3, 2)
        self.connect("realize", self.on_realize)
        self.connect("render", self.on_render)
        self.connect("resize", self.on_resize)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)
        self.set_can_focus(True)
        self.grab_focus()
        self.state = ApplicationState(800, 600)
        self.drawing = False
        self.grContext = None
        self.surface = None

    def on_realize(self, area):
        self.make_current()
        glClearColor(1,1,1,1)
        glClearStencil(0)
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        self.grContext = GrDirectContext.MakeGL()

    def on_resize(self, area, width, height):
        self.state.window_width = width
        self.state.window_height = height
        self.surface = None # force recreation

    def ensure_surface(self, width, height):
        if not self.grContext:
            self.grContext = GrDirectContext.MakeGL()
        if not self.surface or self.surface.width() != width or self.surface.height() != height:
            fb = glGetIntegerv(GL_FRAMEBUFFER_BINDING)
            info = GrGLFramebufferInfo(fb, GL_RGBA8)
            kStencilBits = 8
            kMsaaSampleCount = 0
            target = GrBackendRenderTarget(width, height, kMsaaSampleCount, kStencilBits, info)
            self.surface = Surface.MakeFromBackendRenderTarget(
                self.grContext, target, kBottomLeft_GrSurfaceOrigin, kRGBA_8888_ColorType, None, None
            )
        return self.surface

    def on_render(self, area, glctx):
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        glViewport(0, 0, width, height)
        glClearColor(1, 1, 1, 1)
        glClearStencil(0)
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        surface = self.ensure_surface(width, height)
        canvas = surface.getCanvas()
        canvas.clear(ColorWHITE)

        # Draw help text
        paint = Paint(AntiAlias=True)
        paint.setColor(ColorBLACK)
        font = Font()
        canvas.drawString(HELP_MESSAGE, 10, font.getSize() + 10, font, paint)

        # Draw rectangles
        random.seed(0)
        for rect in self.state.fRects:
            color = random.randint(0, 0xFFFFFFFF) | 0x44808080
            paint.setColor(color)
            canvas.drawRect(rect, paint)
        # Draw drag rect if present
        if self.state.drag_rect:
            paint.setColor(0x44808080)
            canvas.drawRect(self.state.drag_rect, paint)

        # Draw star in the center
        canvas.save()
        cx, cy = width // 2, height // 2
        canvas.translate(cx, cy)
        canvas.drawPath(create_star(), paint)
        canvas.restore()

        canvas.flush()
        self.grContext.flush()
        return True

    def do_button_press_event(self, event):
        if event.button == 1:
            self.drawing = True
            self.state.drag_rect = Rect.MakeLTRB(event.x, event.y, event.x, event.y)
            self.state.fRects.append(self.state.drag_rect)
            self.queue_draw()

    def do_motion_notify_event(self, event):
        if self.drawing and self.state.drag_rect:
            rect = self.state.drag_rect
            rect.fRight = event.x
            rect.fBottom = event.y
            self.queue_draw()

    def do_button_release_event(self, event):
        if event.button == 1 and self.drawing:
            self.drawing = False
            self.state.drag_rect = None
            self.queue_draw()

class SkiaGTKExample(Gtk.Window):
    def __init__(self):
        super().__init__(title="Skia + GTK3 + OpenGL Example")
        self.set_default_size(800, 600)
        self.area = SkiaGLArea()
        self.add(self.area)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", Gtk.main_quit)

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()

def main():
    win = SkiaGTKExample()
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()