#!/usr/bin/env python3
# Skia + Gtk4 + OpenGL (hardware accelerated) example

# References see https://lazka.github.io/pgi-docs/Gtk-4.0/classes/GLArea.html

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib

from OpenGL import GL
import skia
import sys
import math
import random

HELP_MESSAGE = "Click and drag to create rects. Press esc to quit."

class ApplicationState:
    def __init__(self, width, height):
        self.fQuit = False
        self.window_width = width
        self.window_height = height
        self.fRects = []
        self.drawing = False
        self.current_rect = None
        self.rotation = 0

def create_star():
    kNumPoints = 5
    concavePath = skia.Path()
    points = [skia.Point(0, -50)]
    rot = skia.Matrix()
    rot.setRotate(360.0 / kNumPoints)
    for i in range(kNumPoints - 1):
        points.append(rot.mapPoints(points[i:i+1])[0])
    concavePath.moveTo(points[0])
    for i in range(kNumPoints):
        concavePath.lineTo(points[(2 * i) % kNumPoints])
    concavePath.setFillType(skia.PathFillType.kEvenOdd)
    concavePath.close()
    return concavePath

class SkiaGLArea(Gtk.GLArea):
    def __init__(self, state):
        super().__init__()
        self.set_has_depth_buffer(False)
        self.set_has_stencil_buffer(True)
        self.set_required_version(3, 0)
        self.connect("render", self.on_render)
        self.connect("resize", self.on_resize)
        self.set_focusable(True)
        # --- Begin GTK4 event controller setup ---
        # Mouse motion events
        self.motion_controller = Gtk.EventControllerMotion.new()
        self.motion_controller.connect("motion", self.on_motion_notify)

        # Mouse press/release (click) events
        self.click_gesture = Gtk.GestureClick.new()
        self.click_gesture.connect("pressed", self.on_button_press)
        self.click_gesture.connect("released", self.on_button_release)

        # Keyboard events
        self.key_controller = Gtk.EventControllerKey.new()
        self.key_controller.connect("key-pressed", self.on_key_press)
        self.add_controller(self.motion_controller)
        self.add_controller(self.click_gesture)
        self.add_controller(self.key_controller)
        # --- End GTK4 event controller setup ---

        self.state = state
        self.gr_context = None
        self.surface = None
        self.star_image = None
        self.star_width = 100
        self.star_height = 100
        self.create_offscreen_star()

        GLib.timeout_add(16, self.on_tick)

    def create_offscreen_star(self):
        info = skia.ImageInfo.Make(self.star_width, self.star_height, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType)
        star_surface = skia.Surface.MakeRaster(info)
        canvas = star_surface.getCanvas()
        paint = skia.Paint()
        canvas.save()
        canvas.translate(self.star_width/2, self.star_height/2)
        canvas.drawPath(create_star(), paint)
        canvas.restore()
        self.star_image = star_surface.makeImageSnapshot()

    def ensure_surface(self, width, height):
        if not self.gr_context:
            self.gr_context = skia.GrDirectContext.MakeGL(skia.GrGLInterface.MakeEGL())
        if not self.surface or self.surface.width() != width or self.surface.height() != height:
            fb_id = GL.glGetIntegerv(GL.GL_FRAMEBUFFER_BINDING)
            stencil = 8
            msaa = 0
            fb_info = skia.GrGLFramebufferInfo(fb_id, GL.GL_RGBA8)
            backend_render_target = skia.GrBackendRenderTarget(
                width, height, msaa, stencil, fb_info
            )
            props = skia.SurfaceProps(skia.SurfaceProps.kUseDeviceIndependentFonts_Flag, skia.PixelGeometry.kUnknown_PixelGeometry)
            self.surface = skia.Surface.MakeFromBackendRenderTarget(
                self.gr_context,
                backend_render_target,
                skia.kBottomLeft_GrSurfaceOrigin,
                skia.ColorType.kRGBA_8888_ColorType,
                None,
                props
            )

    def on_tick(self):
        self.state.rotation = (self.state.rotation + 1) % 360
        self.queue_render()
        return not self.state.fQuit

    def on_resize(self, area, width, height):
        self.state.window_width = width
        self.state.window_height = height
        self.surface = None  # force recreate

    def on_button_press(self, gesture, n_press, x, y):
        # Only handle left mouse button (button 1)
        if gesture.get_current_button() == Gdk.BUTTON_PRIMARY:
            self.state.drawing = True
            self.state.current_rect = skia.Rect.MakeLTRB(x, y, x, y)
            self.state.fRects.append(self.state.current_rect)
            self.grab_focus()
            self.queue_render()

    def on_button_release(self, gesture, n_press, x, y):
        if gesture.get_current_button() == Gdk.BUTTON_PRIMARY:
            self.state.drawing = False
            self.state.current_rect = None

    def on_motion_notify(self, motion_controller, x, y):
        if self.state.drawing and self.state.current_rect:
            rect = self.state.fRects.pop()
            rect.fRight = x
            rect.fBottom = y
            self.state.fRects.append(rect)
            self.queue_render()

    def on_key_press(self, key_controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.state.fQuit = True
            Gtk.Application.get_default().quit()
            return True
        return False

    def on_render(self, area, gl_context):
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        self.ensure_surface(width, height)

        surface = self.surface
        canvas = surface.getCanvas()
        canvas.clear(skia.ColorWHITE)
        font = skia.Font()
        paint = skia.Paint()
        # Draw help text at top-left
        paint.setColor(skia.ColorBLACK)
        canvas.drawString(HELP_MESSAGE, 0, font.getSize(), font, paint)
        # Draw rectangles
        random.seed(0)
        for rect in self.state.fRects:
            paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            canvas.drawRect(rect, paint)
        # Draw rotating star in center
        canvas.save()
        canvas.translate(self.state.window_width/2, self.state.window_height/2)
        canvas.rotate(self.state.rotation)
        #paint.setColor(skia.ColorBLACK)
        #canvas.drawPath(create_star(), paint)
        if self.star_image:
            canvas.drawImage(self.star_image, -self.star_width/2, -self.star_height/2)
        canvas.restore()
        canvas.flush()
        self.gr_context.flush()
        return True  # drawing handled

class SkiaGTKApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.SkiaGTK4GLExample")
        self.state = None

    def do_activate(self):
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        width = geometry.width
        height = geometry.height

        self.state = ApplicationState(width, height)
        window = Gtk.ApplicationWindow(application=self)
        window.set_default_size(width//2, height//2)
        area = SkiaGLArea(self.state)
        window.set_child(area)
        window.present()

def main():
    app = SkiaGTKApp()
    app.run(sys.argv)

if __name__ == '__main__':
    main()
