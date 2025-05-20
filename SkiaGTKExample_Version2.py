#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

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

class SkiaGTKExample(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Skia + GTK4 Example")
        self.set_default_size(800, 600)
        self.state = ApplicationState(800, 600)
        self.drawing = False

        self.darea = Gtk.DrawingArea()
        self.darea.set_content_width(self.state.window_width)
        self.darea.set_content_height(self.state.window_height)
        self.darea.set_draw_func(self.on_draw)
        self.set_child(self.darea)

        # GTK4 Event Controllers
        self.click_gesture = Gtk.GestureClick.new()
        self.click_gesture.connect("pressed", self.on_button_press)
        self.click_gesture.connect("released", self.on_button_release)
        self.darea.add_controller(self.click_gesture)

        self.motion_controller = Gtk.EventControllerMotion.new()
        self.motion_controller.connect("motion", self.on_motion_notify)
        self.darea.add_controller(self.motion_controller)

        self.key_controller = Gtk.EventControllerKey.new()
        self.key_controller.connect("key-pressed", self.on_key_press)
        self.add_controller(self.key_controller)

    def on_draw(self, area, cr, width, height):
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

        # Export Skia surface as PNG bytes and load into GdkPixbuf for GTK4
        img = surface.makeImageSnapshot()
        png_bytes = img.encodeToData()
        loader = Gdk.Texture.new_from_bytes(png_bytes)
        loader.draw(cr, 0, 0, width, height)
        return False

    def on_button_press(self, gesture, n_press, x, y):
        if gesture.get_current_button() == Gdk.BUTTON_PRIMARY:
            self.drawing = True
            self.state.drag_rect = Rect.MakeLTRB(x, y, x, y)
            self.state.fRects.append(self.state.drag_rect)
            self.darea.queue_draw()

    def on_motion_notify(self, motion_controller, x, y):
        if self.drawing and self.state.drag_rect:
            rect = self.state.drag_rect
            rect.fRight = x
            rect.fBottom = y
            self.darea.queue_draw()

    def on_button_release(self, gesture, n_press, x, y):
        if gesture.get_current_button() == Gdk.BUTTON_PRIMARY:
            self.drawing = False
            self.state.drag_rect = None
            self.darea.queue_draw()

    def on_key_press(self, key_controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

class SkiaGTKApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.SkiaGTKExample")

    def do_activate(self):
        win = SkiaGTKExample(self)
        win.present()

def main():
    import sys
    app = SkiaGTKApp()
    app.run(sys.argv)

if __name__ == '__main__':
    main()