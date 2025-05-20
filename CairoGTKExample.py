#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Cairo + GTK3 (PyGObject) example ported from SkiaSDLExample.py
#
#  Copyright 2025 Hin-Tak Leung
#
#  Ported to PyGTK3 by Copilot

# This is the first response from Github Copilot backed by GPT-4.1 to
#   "Can you port https://github.com/HinTak/skia-python-examples/blob/main/SkiaSDLExample.py to pygtk3 please?"
#
# It basically did a loose rewrite into GTK3 + Cairo. It mostly does
# all the equivalent things, loosely, except it does not show
# intermediate rectangles while one is dragging the mouse.

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import cairo
from collections import namedtuple
import math
import sys

RectState = namedtuple('RectState', ['left', 'top', 'right', 'bottom'])

class ApplicationState:
    def __init__(self, width=800, height=600):
        self.fQuit = False
        self.window_width = width
        self.window_height = height
        self.fRects = []
        self.dragging = False
        self.current_rect = None
        self.rotation = 0

def create_star_path(center_x, center_y, radius):
    # Create a 5-pointed star path in Cairo
    path = []
    num_points = 5
    for i in range(num_points * 2):
        angle = i * math.pi / num_points
        r = radius if i % 2 == 0 else radius * 0.5
        x = center_x + r * math.sin(angle)
        y = center_y - r * math.cos(angle)
        path.append((x, y))
    return path

class CairoGTKExample(Gtk.Window):
    def __init__(self):
        super().__init__(title="Cairo GTK Example")
        self.set_default_size(800, 600)
        self.state = ApplicationState(800, 600)

        self.drawing_area = Gtk.DrawingArea()
        self.add(self.drawing_area)

        # Connect signals
        self.connect("destroy", Gtk.main_quit)
        self.drawing_area.connect("draw", self.on_draw)
        self.drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                     Gdk.EventMask.BUTTON_RELEASE_MASK |
                                     Gdk.EventMask.POINTER_MOTION_MASK |
                                     Gdk.EventMask.KEY_PRESS_MASK |
                                     Gdk.EventMask.STRUCTURE_MASK)
        self.drawing_area.set_can_focus(True)
        self.drawing_area.grab_focus()
        self.drawing_area.connect("button-press-event", self.on_button_press)
        self.drawing_area.connect("button-release-event", self.on_button_release)
        self.drawing_area.connect("motion-notify-event", self.on_motion_notify)
        self.connect("key-press-event", self.on_key_press)
        self.drawing_area.connect("configure-event", self.on_configure)

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        self.state.window_width = width
        self.state.window_height = height

        # White background
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # Draw help message
        cr.set_source_rgb(0, 0, 0)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(18)
        cr.move_to(10, 24)
        cr.show_text("Click and drag to create rects. Press esc to quit.")

        # Draw random-colored rectangles
        import random
        random.seed(0)
        for rect in self.state.fRects:
            color = ((random.randint(0,255)/255, random.randint(0,255)/255, random.randint(0,255)/255, 0.27))
            cr.set_source_rgba(*color)
            l, t, r, b = rect.left, rect.top, rect.right, rect.bottom
            cr.rectangle(l, t, r-l, b-t)
            cr.fill()

        # Draw rotating star in the center
        cr.save()
        cx = width / 2
        cy = height / 2
        cr.translate(cx, cy)
        cr.rotate(math.radians(self.state.rotation))
        self.state.rotation = (self.state.rotation + 1) % 360
        cr.set_source_rgb(0, 0, 0)
        star_path = create_star_path(0, 0, 50)
        cr.move_to(*star_path[0])
        for pt in star_path[1:]:
            cr.line_to(*pt)
        cr.close_path()
        cr.stroke()
        cr.restore()

        # Schedule next redraw for animation
        self.drawing_area.queue_draw()

    def on_button_press(self, widget, event):
        if event.button == 1:
            self.state.dragging = True
            self.state.current_rect = RectState(event.x, event.y, event.x, event.y)

    def on_motion_notify(self, widget, event):
        if self.state.dragging and self.state.current_rect:
            self.state.current_rect = self.state.current_rect._replace(right=event.x, bottom=event.y)
            self.queue_draw()

    def on_button_release(self, widget, event):
        if event.button == 1 and self.state.dragging:
            rect = self.state.current_rect
            # Normalize rectangle
            left, right = sorted([rect.left, rect.right])
            top, bottom = sorted([rect.top, rect.bottom])
            self.state.fRects.append(RectState(left, top, right, bottom))
            self.state.dragging = False
            self.state.current_rect = None
            self.queue_draw()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()

    def on_configure(self, widget, event):
        self.queue_draw()

    def queue_draw(self):
        self.drawing_area.queue_draw()

if __name__ == "__main__":
    win = CairoGTKExample()
    win.show_all()
    Gtk.main()