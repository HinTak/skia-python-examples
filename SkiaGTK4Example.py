#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Skia + GTK4 example (ported from SDL2 version)
#
#  Copyright 2024 Hin-Tak Leung, ported to GTK4 by Copilot
#  Distributed under the terms of the new BSD license.

# References see https://lazka.github.io/pgi-docs/Gtk-4.0/classes/EventController.html

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, GdkRGBA

import cairo
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

class SkiaArea(Gtk.DrawingArea):
    def __init__(self, state):
        super().__init__()
        self.set_draw_func(self.on_draw)
        self.state = state
        self.set_focusable(True)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.KEY_PRESS_MASK |
                        Gdk.EventMask.STRUCTURE_MASK)

        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("key-press-event", self.on_key_press)
        self.connect("resize", self.on_resize)
        self.star_image = None
        self.star_surface = None
        self.star_width = 100
        self.star_height = 100
        self.create_offscreen_star()

        # Animation timer
        GLib.timeout_add(16, self.on_tick)

    def create_offscreen_star(self):
        # Create a raster skia surface for the star
        info = skia.ImageInfo.Make(self.star_width, self.star_height, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType)
        self.star_surface = skia.Surface.MakeRaster(info)
        canvas = self.star_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)
        paint = skia.Paint()
        canvas.save()
        canvas.translate(self.star_width/2, self.star_height/2)
        canvas.drawPath(create_star(), paint)
        canvas.restore()
        self.star_image = self.star_surface.makeImageSnapshot()
    
    def on_tick(self):
        self.state.rotation = (self.state.rotation + 1) % 360
        self.queue_draw()
        return not self.state.fQuit

    def on_resize(self, widget, width, height):
        self.state.window_width = width
        self.state.window_height = height

    def on_button_press(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.state.drawing = True
            x, y = event.x, event.y
            self.state.current_rect = skia.Rect.MakeLTRB(x, y, x, y)
            self.state.fRects.append(self.state.current_rect)
            self.grab_focus()
            self.queue_draw()

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
            self.queue_draw()
    
    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.state.fQuit = True
            Gtk.Application.get_default().quit()
            return True
        return False

    def on_draw(self, area, context, width, height):
        # Create Skia surface backed by Cairo context
        surface = skia.Surface.MakeRenderTarget(
            skia.GrDirectContext.MakeGL() if hasattr(skia, 'GrDirectContext') else None,
            skia.Budgeted.kNo,
            skia.ImageInfo.MakeN32Premul(width, height)
        ) if False else skia.Surface.MakeRasterDirect(
            skia.ImageInfo.MakeN32Premul(width, height),
            cairo.cairo_get_image_surface(context).get_data()
        ) if False else skia.Surface.MakeRaster(
            skia.ImageInfo.MakeN32Premul(width, height)
        )
        # We use MakeRaster for compatibility, and copy to Cairo below.

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
        if self.star_image:
            canvas.drawImage(self.star_image, -self.star_width/2, -self.star_height/2)
        canvas.restore()
        canvas.flush()

        # Copy skia surface to cairo
        skia_img = surface.makeImageSnapshot()
        skia_bytes = skia_img.tobytes()
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(
            skia_bytes,
            GdkPixbuf.Colorspace.RGB,
            True, 8,
            width,
            height,
            width * 4
        )
        Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
        context.paint()

class SkiaGTKApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.SkiaGTK4Example")
        self.state = None

    def do_activate(self):
        # Get display size for initial window
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        width = geometry.width
        height = geometry.height

        self.state = ApplicationState(width, height)
        window = Gtk.ApplicationWindow(application=self)
        window.set_default_size(width//2, height//2)
        area = SkiaArea(self.state)
        window.set_child(area)
        window.present()

def main():
    app = SkiaGTKApp()
    app.run(sys.argv)

if __name__ == '__main__':
    main()
