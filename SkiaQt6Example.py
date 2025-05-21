#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Skia + PyQt6 (QOpenGLWidget) example
#
#  Copyright 2024 Hin-Tak Leung (adapted to PyQt6 by Copilot)
#  Distributed under the terms of the new BSD license.
#
#  Based on SkiaSDLExample.py and Google's Skia + SDL C++ example.
#
#  This port replaces SDL2 with PyQt6, preserving Skia and OpenGL API calls,
#  and faithfully translating mouse, keyboard, and resize events.

import sys
import random
from PyQt6 import QtWidgets, QtCore, QtGui, QtOpenGL
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
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

class SkiaQOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 480)
        self.state = ApplicationState(640, 480)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.helpMessage = "Click and drag to create rects.  Press esc to quit."
        self.rotation = 0
        self.star_image = None
        self.last_mouse_rect = None
        self.font = Font()
        self.grContext = None
        self.surface = None
        self.paint = Paint()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16) # ~60 FPS

    def initializeGL(self):
        glClearColor(1, 1, 1, 1)
        glClearStencil(0)
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        # Create Skia GrDirectContext from current OpenGL context
        self.grContext = GrDirectContext.MakeGL()
        assert self.grContext is not None

        # Prepare the star image as an Skia image (offscreen raster surface)
        cpuSurface = Surface.MakeRaster(ImageInfo.MakeN32Premul(100, 100))
        offscreen = cpuSurface.getCanvas()
        offscreen.save()
        offscreen.translate(50.0, 50.0)
        offscreen.drawPath(create_star(), self.paint)
        offscreen.restore()
        self.star_image = cpuSurface.makeImageSnapshot()

    def resizeGL(self, w, h):
        self.state.window_width = w
        self.state.window_height = h
        glViewport(0, 0, w, h)
        # Re-create Skia backend surface for the new size
        kStencilBits = 8
        kMsaaSampleCount = 0
        info = GrGLFramebufferInfo(0, GL_RGBA8)
        target = GrBackendRenderTarget(w, h, kMsaaSampleCount, kStencilBits, info)
        props = SurfaceProps(SurfaceProps.kUseDeviceIndependentFonts_Flag, PixelGeometry.kUnknown_PixelGeometry)
        self.surface = Surface.MakeFromBackendRenderTarget(
            self.grContext, target, kBottomLeft_GrSurfaceOrigin,
            kRGBA_8888_ColorType, None, props
        )
        assert self.surface is not None

    def paintGL(self):
        canvas = self.surface.getCanvas()
        w, h = self.state.window_width, self.state.window_height
        canvas.clear(ColorWHITE)
        # Draw help message at top-left
        self.paint.setColor(ColorBLACK)
        canvas.drawString(self.helpMessage, 0, self.font.getSize(), self.font, self.paint)
        # Draw user rectangles
        random.seed(0)
        for rect in self.state.fRects:
            self.paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            canvas.drawRect(rect, self.paint)
        # Draw the rotating star at the center
        canvas.save()
        canvas.translate(w / 2.0, h / 2.0)
        canvas.rotate(self.rotation)
        self.rotation += 1
        canvas.drawImage(self.star_image, -50.0, -50.0)
        canvas.restore()
        canvas.flush()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.position()
            rect = Rect.MakeLTRB(pos.x(), pos.y(), pos.x(), pos.y())
            self.state.fRects.append(rect)
            self.last_mouse_rect = len(self.state.fRects) - 1

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.MouseButton.LeftButton and self.last_mouse_rect is not None:
            pos = event.position()
            rect = self.state.fRects[self.last_mouse_rect]
            rect.fRight = pos.x()
            rect.fBottom = pos.y()
            self.state.fRects[self.last_mouse_rect] = rect

    def mouseReleaseEvent(self, event):
        self.last_mouse_rect = None

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            QApplication.quit()

    def closeEvent(self, event):
        # Clean up Skia/OpenGL resources if needed
        self.surface = None
        self.grContext = None
        super().closeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Skia + PyQt6 Example")
        self.widget = SkiaQOpenGLWidget(self)
        self.setCentralWidget(self.widget)
        self.resize(800, 600)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()