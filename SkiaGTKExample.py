#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from skia import *
import random
import math
import io

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

class SkiaGTKExample(Gtk.Window):
    def __init__(self):
        super().__init__(title="Skia + GTK Example")
        self.set_default_size(800, 600)
        self.state = ApplicationState(800, 600)
        self.drawing = False

        self.darea = Gtk.DrawingArea()
        self.darea.set_size_request(self.state.window_width, self.state.window_height)
        self.darea.connect("draw", self.on_draw)
        self.add(self.darea)
        self.darea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                              Gdk.EventMask.BUTTON_RELEASE_MASK |
                              Gdk.EventMask.POINTER_MOTION_MASK)
        self.darea.connect("button-press-event", self.on_button_press)
        self.darea.connect("button-release-event", self.on_button_release)
        self.darea.connect("motion-notify-event", self.on_motion_notify)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", Gtk.main_quit)

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        if (self.state.window_width != width) or (self.state.window_height != height):
            self.state.window_width = width
            self.state.window_height = height

        # Skia surface to draw into
        surface = Surface(width, height)
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

        # Export Skia surface as PNG bytes and load into GdkPixbuf for GTK
        img = surface.makeImageSnapshot()
        png_bytes = img.encodeToData()
        loader = Gdk.PixbufLoader.new_with_type('png')
        loader.write(png_bytes.bytes())
        loader.close()
        pixbuf = loader.get_pixbuf()
        Gdk.cairo_set_source_pixbuf(cr, pixbuf, 0, 0)
        cr.paint()
        return False

    def on_button_press(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.drawing = True
            self.state.drag_rect = Rect.MakeLTRB(event.x, event.y, event.x, event.y)
            self.state.fRects.append(self.state.drag_rect)
            self.darea.queue_draw()

    def on_motion_notify(self, widget, event):
        if self.drawing and self.state.drag_rect:
            rect = self.state.drag_rect
            rect.fRight = event.x
            rect.fBottom = event.y
            self.darea.queue_draw()

    def on_button_release(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.drawing = False
            self.state.drag_rect = None
            self.darea.queue_draw()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()

def main():
    win = SkiaGTKExample()
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()