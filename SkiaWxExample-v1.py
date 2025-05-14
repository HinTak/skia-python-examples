#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Skia + wxPython example (ported from SkiaSDLExample.py)
#
# Copyright 2025 Hin-Tak Leung, wxPython port by Copilot
# Distributed under the terms of the new BSD license.

#     Known issue: Seems to have a buffer aliasing problem.

import wx
import random
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
    concavePath.close()
    return concavePath

class SkiaPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(800, 600))
        self.state = ApplicationState(800, 600)
        self.helpMessage = "Click and drag to create rects.  Press esc to quit."
        self.rotation = 0

        self.font = Font()
        self.paint = Paint()

        # Create offscreen star image
        info = ImageInfo.MakeN32Premul(100, 100)
        cpuSurface = Surface.MakeRaster(info)
        offscreen = cpuSurface.getCanvas()
        offscreen.save()
        offscreen.translate(50.0, 50.0)
        offscreen.drawPath(create_star(), self.paint)
        offscreen.restore()
        self.image = cpuSurface.makeImageSnapshot()

        self.dragging = False

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnChar)

        self.SetFocus()

        # Start a timer for animation
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(16)  # about 60fps

    def OnTimer(self, event):
        self.rotation += 1
        self.Refresh(False)

    def OnChar(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            wx.GetApp().ExitMainLoop()
        else:
            event.Skip()

    def OnResize(self, event):
        sz = self.GetClientSize()
        self.state.window_width = sz.width
        self.state.window_height = sz.height
        self.Refresh(False)

    def OnLeftDown(self, event):
        x, y = event.GetPosition()
        rect = Rect.MakeLTRB(x, y, x, y)
        self.state.fRects.append(rect)
        self.dragging = True
        self.CaptureMouse()

    def OnLeftUp(self, event):
        self.dragging = False
        if self.HasCapture():
            self.ReleaseMouse()

    def OnMouseMove(self, event):
        if self.dragging and event.Dragging() and event.LeftIsDown() and self.state.fRects:
            x, y = event.GetPosition()
            rect = self.state.fRects.pop()
            rect.fRight = x
            rect.fBottom = y
            self.state.fRects.append(rect)
            self.Refresh(False)

    def OnPaint(self, event):
        width, height = self.GetClientSize().width, self.GetClientSize().height
        info = ImageInfo.MakeN32Premul(width, height)
        surface = Surface.MakeRaster(info)
        canvas = surface.getCanvas()

        # Clear background
        canvas.clear(ColorWHITE)

        # Draw help message at top left
        self.paint.setColor(ColorBLACK)
        canvas.drawString(self.helpMessage, 0, self.font.getSize(), self.font, self.paint)

        # Draw rectangles
        random.seed(0)
        for rect in self.state.fRects:
            color = random.randint(0, 0xFFFFFFFF) | 0x44808080
            self.paint.setColor(color)
            canvas.drawRect(rect, self.paint)

        # Draw rotating star image at center
        canvas.save()
        canvas.translate(width / 2.0, height / 2.0)
        canvas.rotate(self.rotation)
        canvas.drawImage(self.image, -50.0, -50.0)
        canvas.restore()

        # Flush and blit to wx.PaintDC
        canvas.flush()
        image = surface.makeImageSnapshot()
        buf = image.tobytes()
        bmp = wx.Bitmap.FromBufferRGBA(width, height, buf)
        dc = wx.PaintDC(self)
        dc.DrawBitmap(bmp, 0, 0)

class SkiaFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Skia + wxPython Example")
        self.panel = SkiaPanel(self)
        self.SetClientSize((800, 600))
        self.Centre()

class SkiaApp(wx.App):
    def OnInit(self):
        frame = SkiaFrame()
        frame.Show()
        return True

if __name__ == '__main__':
    app = SkiaApp(False)
    app.MainLoop()
