#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Skia + GLFW example (ported from SkiaSDLExample.py)
#
#  Copyright 2025 Hin-Tak Leung
#  Ported to GLFW by Copilot, 2025
#
#      Known problem: message at bottom instead of top
import glfw
from OpenGL.GL import *
from skia import *
import sys
import random

class ApplicationState:
    def __init__(self, width, height):
        self.fQuit = False
        self.window_width = width
        self.window_height = height
        self.fRects = []
        self.drawing = False

def create_star():
    kNumPoints = 5
    concavePath = Path()
    points = [Point(0, -50)]
    rot = Matrix()
    rot.setRotate(360.0 / kNumPoints)
    for i in range(kNumPoints - 1):
        points.append(rot.mapPoints(points[i:i+1])[0])
    concavePath.moveTo(points[0])
    for i in range(kNumPoints):
        concavePath.lineTo(points[(2 * i) % kNumPoints])
    concavePath.setFillType(PathFillType.kEvenOdd)
    concavePath.close()
    return concavePath

def main():
    global surface, canvas, grContext, target, fFormat, colorType, props
    if not glfw.init():
        print("Failed to initialize GLFW")
        return 1

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
    width, height = 800, 600
    window = glfw.create_window(width, height, "GLFW Window", None, None)
    if not window:
        print("Failed to create GLFW window")
        glfw.terminate()
        return 1

    glfw.make_context_current(window)
    glViewport(0, 0, width, height)
    glClearColor(1, 1, 1, 1)
    glClearStencil(0)
    glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    grContext = GrDirectContext.MakeGL()
    assert grContext is not None

    # Framebuffer info for Skia
    fFormat = GL_RGBA8
    colorType = kRGBA_8888_ColorType
    info = GrGLFramebufferInfo(0, fFormat)
    kStencilBits = 8
    kMsaaSampleCount = 0

    target = GrBackendRenderTarget(width, height, kMsaaSampleCount, kStencilBits, info)
    props = SurfaceProps(SurfaceProps.kUseDeviceIndependentFonts_Flag, PixelGeometry.kUnknown_PixelGeometry)
    surface = Surface.MakeFromBackendRenderTarget(grContext, target, kBottomLeft_GrSurfaceOrigin, colorType, None, props)
    assert surface is not None
    canvas = surface.getCanvas()

    state = ApplicationState(width, height)
    helpMessage = "Click and drag to create rects.  Press esc to quit."
    font = Font()
    paint = Paint()

    # Prepare the star image
    cpuSurface = Surface.MakeRaster(canvas.imageInfo())
    offscreen = cpuSurface.getCanvas()
    offscreen.save()
    offscreen.translate(50.0, 50.0)
    offscreen.drawPath(create_star(), paint)
    offscreen.restore()
    image = cpuSurface.makeImageSnapshot()

    rotation = 0

    # Event callbacks
    def on_mouse_button(window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            x, y = glfw.get_cursor_pos(window)
            #y = state.window_height - y  # Convert to bottom-left origin
            if action == glfw.PRESS:
                state.drawing = True
                state.fRects.append(Rect.MakeLTRB(x, y, x, y))
            elif action == glfw.RELEASE:
                state.drawing = False

    def on_cursor_pos(window, xpos, ypos):
        #ypos = state.window_height - ypos
        if state.drawing and state.fRects:
            rect = state.fRects.pop()
            rect.fRight = xpos
            rect.fBottom = ypos
            state.fRects.append(rect)

    def on_key(window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            state.fQuit = True

    def on_window_size(window, w, h):
        state.window_width = w
        state.window_height = h
        glViewport(0, 0, w, h)

        # Recreate Skia surface
        global surface, canvas, grContext, target, fFormat, colorType, props
        target = GrBackendRenderTarget(w, h, kMsaaSampleCount, kStencilBits, GrGLFramebufferInfo(0, fFormat))
        surface = Surface.MakeFromBackendRenderTarget(grContext, target, kBottomLeft_GrSurfaceOrigin, colorType, None, props)
        if surface is None:
            print("Failed to recreate Skia surface")
            return
        canvas = surface.getCanvas()

    glfw.set_mouse_button_callback(window, on_mouse_button)
    glfw.set_cursor_pos_callback(window, on_cursor_pos)
    glfw.set_key_callback(window, on_key)
    glfw.set_window_size_callback(window, on_window_size)

    while not glfw.window_should_close(window) and not state.fQuit:
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        canvas.clear(ColorWHITE)

        # Draw help message
        paint.setColor(ColorBLACK)
        canvas.save()
        canvas.translate(0, 0)
        canvas.drawString(helpMessage, 0, font.getSize(), font, paint)
        canvas.restore()

        # Draw rectangles
        random.seed(0)
        for rect in state.fRects:
            paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            canvas.drawRect(rect, paint)

        # Draw rotating star
        canvas.save()
        canvas.translate(state.window_width / 2.0, state.window_height / 2.0)
        canvas.rotate(rotation)
        rotation += 1
        canvas.drawImage(image, -50.0, -50.0)
        canvas.restore()

        canvas.flush()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()
    return 0

if __name__ == '__main__':
    sys.exit(main())
