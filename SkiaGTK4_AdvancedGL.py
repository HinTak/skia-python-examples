#!/usr/bin/env python3
# Skia + Gtk4 + OpenGL (hardware accelerated, advanced GPU features) example

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib

from OpenGL import GL
import skia
import sys
import math
import random
import time

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
        self.start_time = time.time()

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
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.KEY_PRESS_MASK
        )
        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("key-press-event", self.on_key_press)

        self.state = state
        self.gr_context = None
        self.surface = None
        self.star_image = None
        self.star_width = 100
        self.star_height = 100
        self.blur_filter = skia.ImageFilters.Blur(10, 10)
        self.shader_effect = None
        self.shader_uniforms = {}
        self.create_offscreen_star()
        self.create_runtime_shader()

        GLib.timeout_add(16, self.on_tick)

    def create_offscreen_star(self):
        info = skia.ImageInfo.Make(self.star_width, self.star_height, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType)
        star_surface = skia.Surface.MakeRaster(info)
        canvas = star_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)
        paint = skia.Paint()
        canvas.save()
        canvas.translate(self.star_width/2, self.star_height/2)
        canvas.drawPath(create_star(), paint)
        canvas.restore()
        self.star_image = star_surface.makeImageSnapshot()

    def create_runtime_shader(self):
        # Skia runtime shader (SkSL) - animated radial gradient
        sksl_code = """
        uniform float2 iResolution;
        uniform float iTime;
        half4 main(float2 fragcoord) {
            float2 uv = fragcoord / iResolution;
            float angle = atan(uv.x-0.5, uv.y-0.5) + iTime;
            float radius = length(uv - 0.5);
            float v = 0.5 + 0.5 * cos(10.0 * angle + iTime) * smoothstep(0.5, 0.2, radius);
            return half4(v, v*0.7, v*0.2, 1.0);
        }
        """
        try:
            self.shader_effect = skia.RuntimeEffect.MakeForShader(sksl_code)
        except Exception as e:
            print("Shader effect error:", e)
            self.shader_effect = None

    def ensure_surface(self, width, height):
        if not self.gr_context:
            self.gr_context = skia.GrDirectContext.MakeGL()
        if not self.surface or self.surface.width() != width or self.surface.height() != height:
            fb_id = GL.glGetIntegerv(GL.GL_FRAMEBUFFER_BINDING)
            stencil = 8
            msaa = 4  # Use MSAA for smoother edges
            fb_info = skia.GrGLFramebufferInfo(fb_id, GL.GL_RGBA8)
            backend_render_target = skia.GrBackendRenderTarget(
                width, height, msaa, stencil, fb_info
            )
            props = skia.SurfaceProps(skia.SurfaceProps.kUseDeviceIndependentFonts_Flag)
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

    def on_button_press(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.state.drawing = True
            x, y = event.x, event.y
            self.state.current_rect = skia.Rect.MakeLTRB(x, y, x, y)
            self.state.fRects.append(self.state.current_rect)
            self.grab_focus()
            self.queue_render()

    def on_button_release(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.state.drawing = False
            self.state.current_rect = None

    def on_motion_notify(self, widget, event):
        if self.state.drawing and self.state.current_rect:
            rect = self.state.fRects.pop()
            rect.fRight = event.x
            rect.fBottom = event.y
            self.state.fRects.append(rect)
            self.queue_render()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
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
        # Draw animated runtime shader background if available
        if self.shader_effect:
            secs = time.time() - self.state.start_time
            uniforms = {
                "iResolution": (width, height),
                "iTime": float(secs)
            }
            shader = self.shader_effect.makeShader(
                uniforms, None, None
            )
            paint.setShader(shader)
            canvas.drawRect(skia.Rect.MakeWH(width, height), paint)
            paint.setShader(None)
        # Draw help text at top-left
        paint.setColor(skia.ColorBLACK)
        canvas.drawString(HELP_MESSAGE, 0, font.getSize(), font, paint)
        # Draw rectangles with a GPU blur filter
        random.seed(0)
        for rect in self.state.fRects:
            paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            blur_paint = skia.Paint(paint)
            blur_paint.setImageFilter(self.blur_filter)
            canvas.drawRect(rect, blur_paint)
        # Draw rotating blurred star in center, using GPU filter
        canvas.save()
        canvas.translate(self.state.window_width/2, self.state.window_height/2)
        canvas.rotate(self.state.rotation)
        if self.star_image:
            blur_paint = skia.Paint()
            blur_paint.setImageFilter(self.blur_filter)
            canvas.drawImage(self.star_image, -self.star_width/2, -self.star_height/2, blur_paint)
        canvas.restore()
        canvas.flush()
        self.gr_context.flush()
        return True  # drawing handled

class SkiaGTKApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.SkiaGTK4GLAdvancedExample")
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