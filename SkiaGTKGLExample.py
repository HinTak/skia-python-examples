#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject, GLib
from OpenGL.GL import *
import sys

from skia import *

class ApplicationState:
    def __init__(self, width, height):
        self.fQuit = False
        self.window_width = width
        self.window_height = height
        self.fRects = []

def create_star():
    kNumPoints = 5
    concavePath = Path()
    points = [Point(0, -50)]
    rot = Matrix()
    rot.setRotate(360.0 / kNumPoints)
    for i in range(kNumPoints - 1): # skip 0
        points.append(rot.mapPoints(points[i:i+1])[0])
    concavePath.moveTo(points[0])
    for i in range(kNumPoints):
        concavePath.lineTo(points[(2 * i) % kNumPoints])
    concavePath.setFillType(PathFillType.kEvenOdd)
    assert not concavePath.isConvex()
    concavePath.close()
    return concavePath

class SkiaGLArea(Gtk.GLArea):
    def __init__(self):
        super().__init__()
        self.set_has_depth_buffer(False)
        self.set_has_stencil_buffer(True)
        self.set_auto_render(True)
        self.set_required_version(3, 0)
        self.connect("realize", self.on_realize)
        self.connect("render", self.on_render)
        self.connect("resize", self.on_resize)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.KEY_PRESS_MASK)
        self.set_can_focus(True)
        self.grab_focus()
        self.state = ApplicationState(800, 600)
        self.rotation = 0
        self.star_image = None
        self.helpMessage = "Click and drag to create rects.  Press esc to quit."
        self.drag_rect = None

    def on_realize(self, area):
        self.make_current()
        glClearColor(1, 1, 1, 1)
        glClearStencil(0)
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        self.grContext = GrDirectContext.MakeGL()
        self.star_image = self.make_offscreen_star()
        GLib.timeout_add(16, self.queue_draw)  # ~60fps

    def on_resize(self, area, width, height):
        self.state.window_width = width
        self.state.window_height = height

    def make_offscreen_star(self):
        # Draw star to an image so we can rotate/translate it efficiently
        surface = Surface.MakeRasterN32Premul(100, 100)
        canvas = surface.getCanvas()
        paint = Paint()
        canvas.save()
        canvas.translate(50, 50)
        canvas.drawPath(create_star(), paint)
        canvas.restore()
        return surface.makeImageSnapshot()

    def on_render(self, area, glctx):
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        glViewport(0, 0, width, height)
        glClearColor(1, 1, 1, 1)
        glClearStencil(0)
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        # Setup Skia backend target for this frame
        fb = glGetIntegerv(GL_FRAMEBUFFER_BINDING)
        info = GrGLFramebufferInfo(fb, GL_RGBA8)
        kStencilBits = 8
        kMsaaSampleCount = 0
        target = GrBackendRenderTarget(width, height, kMsaaSampleCount, kStencilBits, info)
        surface = Surface.MakeFromBackendRenderTarget(
            self.grContext, target, kBottomLeft_GrSurfaceOrigin, kRGBA_8888_ColorType, None, None
        )
        canvas = surface.getCanvas()
        canvas.clear(ColorWHITE)
        font = Font()
        paint = Paint()

        # Draw help message in the top left
        paint.setColor(ColorBLACK)
        canvas.drawString(self.helpMessage, 0, font.getSize(), font, paint)

        # Draw rectangles
        import random
        random.seed(0)
        for rect in self.state.fRects:
            paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            canvas.drawRect(rect, paint)
        if self.drag_rect:
            paint.setColor(0x44808080)
            canvas.drawRect(self.drag_rect, paint)

        # Draw rotating star in the center
        canvas.save()
        canvas.translate(width / 2.0, height / 2.0)
        canvas.rotate(self.rotation)
        self.rotation = (self.rotation + 1) % 360
        canvas.drawImage(self.star_image, -50.0, -50.0)
        canvas.restore()

        canvas.flush()
        self.grContext.flush()
        return True

    def do_button_press_event(self, event):
        if event.button == 1:
            self.drag_start = (event.x, event.y)
            self.drag_rect = Rect.MakeLTRB(event.x, event.y, event.x, event.y)
            self.queue_draw()

    def do_motion_notify_event(self, event):
        if self.drag_rect:
            x0, y0 = self.drag_start
            self.drag_rect = Rect.MakeLTRB(x0, y0, event.x, event.y)
            self.queue_draw()

    def do_button_release_event(self, event):
        if event.button == 1 and self.drag_rect:
            self.state.fRects.append(self.drag_rect)
            self.drag_rect = None
            self.queue_draw()

    def do_key_press_event(self, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()

    def queue_draw(self, *args):
        super().queue_draw()
        return True  # GLib.timeout_add expects a bool

class SkiaGTKGLWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Skia + GTK3 + OpenGL")
        self.set_default_size(800, 600)
        self.area = SkiaGLArea()
        self.add(self.area)
        self.connect("destroy", Gtk.main_quit)

if __name__ == "__main__":
    win = SkiaGTKGLWindow()
    win.show_all()
    Gtk.main()