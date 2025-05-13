#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Skia + GLFW example (based on SkiaSDLExample.py)
#
#  Copyright 2024 Hin-Tak Leung, adapted to GLFW by Copilot
#  Distributed under the terms of the new BSD license.
#
#  You need: pip install glfw skia-python PyOpenGL

import glfw
import sys
from OpenGL.GL import *
from skia import *

class ApplicationState:
    def __init__(self, width, height):
        self.fQuit = False
        self.window_width = width
        self.window_height = height
        self.fRects = []
        self.dragging = False
        self.drag_start = (0, 0)

def handle_events(state, window):
    # Poll events is done in the main loop
    pass

def mouse_button_callback(window, button, action, mods):
    state = glfw.get_window_user_pointer(window)
    if button == glfw.MOUSE_BUTTON_LEFT:
        x, y = glfw.get_cursor_pos(window)
        #y = state.window_height - y  # Convert to Skia coordinate
        if action == glfw.PRESS:
            state.fRects.append(Rect.MakeLTRB(x, y, x, y))
            state.dragging = True
            state.drag_start = (x, y)
        elif action == glfw.RELEASE:
            state.dragging = False

def cursor_pos_callback(window, xpos, ypos):
    state = glfw.get_window_user_pointer(window)
    #ypos = state.window_height - ypos  # Convert to Skia coordinate
    if state.dragging and state.fRects:
        rect = state.fRects.pop()
        rect.fRight = xpos
        rect.fBottom = ypos
        state.fRects.append(rect)

def key_callback(window, key, scancode, action, mods):
    state = glfw.get_window_user_pointer(window)
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        state.fQuit = True

def window_size_callback(window, width, height):
    state = glfw.get_window_user_pointer(window)
    state.window_width = width
    state.window_height = height
    glViewport(0, 0, width, height)

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

def main(argv):
    if not glfw.init():
        print("Could not initialize GLFW")
        return 1

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
    glfw.window_hint(glfw.DOUBLEBUFFER, glfw.TRUE)
    glfw.window_hint(glfw.RED_BITS, 8)
    glfw.window_hint(glfw.GREEN_BITS, 8)
    glfw.window_hint(glfw.BLUE_BITS, 8)
    glfw.window_hint(glfw.DEPTH_BITS, 0)
    glfw.window_hint(glfw.STENCIL_BITS, 8)

    # Use primary monitor's size
    monitor = glfw.get_primary_monitor()
    mode = glfw.get_video_mode(monitor)
    width, height = mode.size.width, mode.size.height

    window = glfw.create_window(width, height, "GLFW Window", None, None)
    if not window:
        glfw.terminate()
        print("Could not create GLFW window")
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
    glfw.set_window_size_callback(window, window_size_callback)

    grContext = GrDirectContext.MakeGL()
    assert grContext is not None

    kStencilBits = 8
    kMsaaSampleCount = 0
    fFormat = GL_RGBA8
    colorType = kRGBA_8888_ColorType

    info = GrGLFramebufferInfo(0, fFormat)
    props = SurfaceProps(SurfaceProps.kUseDeviceIndependentFonts_Flag, PixelGeometry.kUnknown_PixelGeometry)

    # Create offscreen raster surface for the star image
    cpuSurface = Surface.MakeRaster(ImageInfo.MakeN32Premul(100, 100))
    offscreen = cpuSurface.getCanvas()
    offscreen.save()
    offscreen.translate(50.0, 50.0)
    offscreen.drawPath(create_star(), Paint())
    offscreen.restore()
    image = cpuSurface.makeImageSnapshot()

    helpMessage = "Click and drag to create rects.  Press esc to quit."
    paint = Paint()
    font = Font()
    import random
    rotation = 0

    while not state.fQuit and not glfw.window_should_close(window):
        random.seed(0)
        glfw.poll_events()

        # Recreate render target and Skia surface if size changed
        width, height = state.window_width, state.window_height
        glViewport(0, 0, width, height)
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        target = GrBackendRenderTarget(width, height, kMsaaSampleCount, kStencilBits, info)
        surface = Surface.MakeFromBackendRenderTarget(grContext, target,
                                                     kBottomLeft_GrSurfaceOrigin,
                                                     colorType, None, props)
        assert surface is not None
        canvas = surface.getCanvas()
        canvas.scale(1, 1)

        canvas.clear(ColorWHITE)

        # Draw help message at the top left
        paint.setColor(ColorBLACK)
        canvas.drawString(helpMessage, 0, font.getSize(), font, paint)

        # Draw rectangles
        for rect in state.fRects:
            paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            canvas.drawRect(rect, paint)

        # Draw rotating star at the center
        canvas.save()
        canvas.translate(width / 2.0, height / 2.0)
        canvas.rotate(rotation)
        rotation += 1
        canvas.drawImage(image, -50.0, -50.0)
        canvas.restore()

        canvas.flush()

        glfw.swap_buffers(window)

    glfw.terminate()
    return 0

if __name__ == '__main__':
    import sys
    main(sys.argv)
