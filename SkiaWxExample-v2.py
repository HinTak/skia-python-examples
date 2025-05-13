#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Skia + wxPython example (port of SkiaSDLExample.py)
#
#  Copyright 2024 Hin-Tak Leung, ported to wxPython by Copilot
#  Distributed under the terms of the new BSD license.

import wx
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
    for i in range(kNumPoints - 1):  # skip 0
        points.append(rot.mapPoints(points[i:i+1])[0])
    concavePath.moveTo(points[0])
    for i in range(kNumPoints):
        concavePath.lineTo(points[(2 * i) % kNumPoints])
    concavePath.setFillType(PathFillType.kEvenOdd)
    assert not concavePath.isConvex()
    concavePath.close()
    return concavePath

class SkiaPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        w, h = self.GetClientSize()
        self.state = ApplicationState(w, h)
        self.rotation = 0
        self.star_image = None
        self.helpMessage = "Click and drag to create rects.  Press esc to quit."
        self.font = Font()
        self.paint = Paint()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)
        self.dragging = False
        self.last_rect = None
        self.generate_star_image()

    def generate_star_image(self):
        # Create a raster surface, draw a star, make snapshot
        info = ImageInfo.MakeN32Premul(100, 100)
        surface = Surface.MakeRaster(info)
        canvas = surface.getCanvas()
        canvas.clear(ColorTRANSPARENT)
        canvas.save()
        canvas.translate(50, 50)
        canvas.drawPath(create_star(), self.paint)
        canvas.restore()
        self.star_image = surface.makeImageSnapshot()

    def OnResize(self, event):
        w, h = self.GetClientSize()
        self.state.window_width = w
        self.state.window_height = h
        self.Refresh()
        event.Skip()

    def OnPaint(self, event):
        w, h = self.GetClientSize()
        info = ImageInfo.MakeN32Premul(w, h)
        surface = Surface.MakeRaster(info)
        canvas = surface.getCanvas()
        import random
        random.seed(0)

        # Clear background
        canvas.clear(ColorWHITE)

        # Draw help message at top left
        self.paint.setColor(ColorBLACK)
        canvas.drawString(self.helpMessage, 0, self.font.getSize(), self.font, self.paint)

        # Draw rectangles
        for rect in self.state.fRects:
            self.paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            canvas.drawRect(rect, self.paint)

        # Draw rotating star at center
        canvas.save()
        canvas.translate(w / 2, h / 2)
        canvas.rotate(self.rotation)
        self.rotation = (self.rotation + 1) % 360
        if self.star_image:
            canvas.drawImage(self.star_image, -50, -50)
        canvas.restore()

        # Flush drawing
        canvas.flush()

        # Extract pixel data safely using peekPixels
        pixmap = surface.peekPixels()
        if pixmap is not None:
            buffer = memoryview(pixmap.addr()).tobytes()  # Get raw RGBA bytes
            wx_bmp = wx.Bitmap.FromBufferRGBA(w, h, buffer)
            dc = wx.AutoBufferedPaintDC(self)
            dc.DrawBitmap(wx_bmp, 0, 0)
        else:
            # Fallback: blank
            dc = wx.AutoBufferedPaintDC(self)
            dc.Clear()

        # Schedule next frame for animation
        self.Refresh(False)

    def OnMouseDown(self, event):
        if event.LeftDown():
            x, y = event.GetPosition()
            rect = Rect.MakeLTRB(x, y, x, y)
            self.state.fRects.append(rect)
            self.last_rect = rect
            self.dragging = True

    def OnMouseUp(self, event):
        if self.dragging:
            x, y = event.GetPosition()
            if self.last_rect:
                self.state.fRects.pop()
                rect = Rect.MakeLTRB(self.last_rect.left(), self.last_rect.top(), x, y)
                self.state.fRects.append(rect)
            self.dragging = False
            self.last_rect = None

    def OnMouseMove(self, event):
        if self.dragging and event.Dragging() and event.LeftIsDown():
            x, y = event.GetPosition()
            if self.last_rect:
                self.state.fRects.pop()
                rect = Rect.MakeLTRB(self.last_rect.left(), self.last_rect.top(), x, y)
                self.state.fRects.append(rect)

    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.GetParent().Close()
        else:
            event.Skip()

class SkiaFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Skia + wxPython Example", size=(800, 600))
        self.panel = SkiaPanel(self)
        self.Show()

class SkiaApp(wx.App):
    def OnInit(self):
        self.frame = SkiaFrame()
        self.SetTopWindow(self.frame)
        return True

if __name__ == "__main__":
    app = SkiaApp(False)
    app.MainLoop()
