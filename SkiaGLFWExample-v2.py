#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Skia + GLFW example (ported from SDL2 version)
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#
#  This example requires:
#    - skia-python
#    - pyGLFW
#    - PyOpenGL

import glfw
from OpenGL.GL import *
import sys
import random
from skia import *

class ApplicationState:
    def __init__(self, width, height):
        self.fQuit = False
        self.window_width = width
        self.window_height = height
        self.fRects = []
        self.dragging = False
        self.last_rect = None

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

def mouse_button_callback(window, button, action, mods):
    state = glfw.get_window_user_pointer(window)
    if button == glfw.MOUSE_BUTTON_LEFT:
        x, y = glfw.get_cursor_pos(window)
        y = state.window_height - y  # invert y for Skia canvas
        if action == glfw.PRESS:
            rect = Rect.MakeLTRB(x, y, x, y)
            state.last_rect = rect
            state.fRects.append(rect)
            state.dragging = True
        elif action == glfw.RELEASE:
            state.last_rect = None
            state.dragging = False

def cursor_pos_callback(window, xpos, ypos):
    state = glfw.get_window_user_pointer(window)
    if state.dragging and state.last_rect:
        ypos = state.window_height - ypos  # invert y for Skia canvas
        rect = state.fRects.pop()
        rect.fRight = xpos
        rect.fBottom = ypos
        state.fRects.append(rect)

def key_callback(window, key, scancode, action, mods):
    state = glfw.get_window_user_pointer(window)
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        state.fQuit = True

def framebuffer_size_callback(window, width, height):
    state = glfw.get_window_user_pointer(window)
    state.window_width = width
    state.window_height = height
    glViewport(0, 0, width, height)

def main(argv):
    if not glfw.init():
        print("Failed to initialize GLFW")
        return 1

    # GLFW window hints for OpenGL context
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.DOUBLEBUFFER, 1)
    glfw.window_hint(glfw.RED_BITS, 8)
    glfw.window_hint(glfw.GREEN_BITS, 8)
    glfw.window_hint(glfw.BLUE_BITS, 8)
    glfw.window_hint(glfw.DEPTH_BITS, 0)
    glfw.window_hint(glfw.STENCIL_BITS, 8)
    glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)

    # Get monitor size for initial window size
    monitor = glfw.get_primary_monitor()
    mode = glfw.get_video_mode(monitor)
    width, height = mode.size.width, mode.size.height

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

    state = ApplicationState(width, height)
    glfw.set_window_user_pointer(window, state)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    grContext = GrDirectContext.MakeGL()
    assert grContext is not None

    fFormat = GL_RGBA8
    colorType = kRGBA_8888_ColorType

    kMsaaSampleCount = 0
    kStencilBits = 8

    info = GrGLFramebufferInfo(0, fFormat)

    font = Font()
    paint = Paint()

    cpuSurface = Surface.MakeRaster(ImageInfo.Make(width, height, colorType, kOpaque_AlphaType))
    offscreen = cpuSurface.getCanvas()
    offscreen.save()
    offscreen.translate(50.0, 50.0)
    offscreen.drawPath(create_star(), paint)
    offscreen.restore()
    image = cpuSurface.makeImageSnapshot()

    helpMessage = "Click and drag to create rects.  Press esc to quit."
    rotation = 0

    while not glfw.window_should_close(window) and not state.fQuit:
        glfw.poll_events()

        # Get framebuffer size every frame (handles resize)
        fb_width, fb_height = glfw.get_framebuffer_size(window)
        glViewport(0, 0, fb_width, fb_height)
        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        target = GrBackendRenderTarget(
            fb_width, fb_height, kMsaaSampleCount, kStencilBits, info
        )
        surface = Surface.MakeFromBackendRenderTarget(
            grContext, target,
            kBottomLeft_GrSurfaceOrigin,
            colorType, None, None
        )
        assert surface is not None
        canvas = surface.getCanvas()

        canvas.clear(ColorWHITE)
        paint.setColor(ColorBLACK)
        canvas.drawString(helpMessage, 0, font.getSize(), font, paint)
        for rect in state.fRects:
            paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            canvas.drawRect(rect, paint)

        canvas.save()
        canvas.translate(state.window_width / 2.0, state.window_height / 2.0)
        canvas.rotate(rotation)
        rotation += 1
        canvas.drawImage(image, -50.0, -50.0)
        canvas.restore()

        canvas.flush()
        glfw.swap_buffers(window)

    glfw.destroy_window(window)
    glfw.terminate()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
