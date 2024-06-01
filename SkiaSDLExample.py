#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Skia + SDL example
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#
#  Based on Google's own Skia + SDL C++ example, chrome/m92:example/SkiaSDLExample.cpp

from sdl2 import *
from sdl2.video import *
from ctypes import byref, c_int
from OpenGL.GL import glViewport, glClearColor, glClearStencil, glClear, GL_COLOR_BUFFER_BIT, GL_STENCIL_BUFFER_BIT, GL_RGBA8
from OpenGL.GLES2.EXT.texture_storage import GL_BGRA8_EXT
from skia import *

from sdl2.ext import get_events

class ApplicationState:
    def __init__(self):
        self.fQuit = False
        self.fRects = []

def handle_error():
    error = SDL_GetError()
    print(error)
    SDL_ClearError()

def handle_events(state, canvas):
    for event in get_events():
        if event.type == SDL_MOUSEMOTION:
            if event.motion.state == SDL_PRESSED:
                rect = state.fRects.pop()
                rect.fRight = event.motion.x
                rect.fBottom = event.motion.y
                state.fRects.append(rect)
        if event.type == SDL_MOUSEBUTTONDOWN:
            if event.button.state == SDL_PRESSED:
                state.fRects.append(Rect.MakeLTRB(event.button.x,
                                                    event.button.y,
                                                    event.button.x,
                                                    event.button.y))
        if event.type ==  SDL_KEYDOWN:
            if event.key.keysym.sym == SDLK_ESCAPE:
                state.fQuit = True
        if event.type == SDL_QUIT:
                state.fQuit = True

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
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 0)

    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

    windowFlags = SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE

    kStencilBits = 8
    SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 0);
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, kStencilBits)

    SDL_GL_SetAttribute(SDL_GL_ACCELERATED_VISUAL, 1)

    kMsaaSampleCount = 0

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) != 0):
        handle_error()
        return 1

    dm = SDL_DisplayMode() 
    if (SDL_GetDesktopDisplayMode(0, byref(dm)) != 0):
        handle_error()
        return 1

    window = SDL_CreateWindow(b"SDL Window", SDL_WINDOWPOS_CENTERED,
                              SDL_WINDOWPOS_CENTERED, dm.w, dm.h, windowFlags)

    if not window:
        handle_error()
        return 1

    glContext = SDL_GL_CreateContext(window)
    if not glContext:
        handle_error()
        return 1

    success =  SDL_GL_MakeCurrent(window, glContext)
    if success != 0:
        handle_error()
        return success

    windowFormat = SDL_GetWindowPixelFormat(window)
    contextType = c_int(0)
    SDL_GL_GetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, byref(contextType))
    
    dw = c_int(0)
    dh = c_int(0)
    SDL_GL_GetDrawableSize(window, byref(dw), byref(dh))

    glViewport(0, 0, dw.value, dh.value)
    glClearColor(1, 1, 1, 1)
    glClearStencil(0)
    glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    grContext = GrDirectContext.MakeGL()
    assert grContext is not None

    ##// Wrap the frame buffer object attached to the screen in a Skia render target so Skia can
    ##// render to it
    ##GrGLint buffer;
    ##GR_GL_GetIntegerv(interface.get(), GR_GL_FRAMEBUFFER_BINDING, &buffer);
    ## glGetIntegerv

    ## TODO: the windowFormat is never any of these?
    if SDL_PIXELFORMAT_RGBA8888 == windowFormat:
        fFormat = GL_RGBA8
        colorType = kRGBA_8888_ColorType
    else:
        colorType = kBGRA_8888_ColorType
        if SDL_GL_CONTEXT_PROFILE_ES == contextType:
            fFormat = GL_BGRA8_EXT
        else:
            fFormat = GL_RGBA8

    info = GrGLFramebufferInfo(0, fFormat)

    target = GrBackendRenderTarget(dw.value, dh.value, kMsaaSampleCount, kStencilBits, info)

    props = SurfaceProps(SurfaceProps.kUseDeviceIndependentFonts_Flag, PixelGeometry.kUnknown_PixelGeometry)

    surface = Surface.MakeFromBackendRenderTarget(grContext, target,
                                                 kBottomLeft_GrSurfaceOrigin,
                                                 colorType, None, props)
    assert surface is not None
    canvas = surface.getCanvas()
    canvas.scale(dw.value/dm.w, dh.value/dm.h)
    
    state = ApplicationState()

    helpMessage = "Click and drag to create rects.  Press esc to quit."

    paint = Paint()

    cpuSurface = Surface.MakeRaster(canvas.imageInfo())

    offscreen = cpuSurface.getCanvas()
    offscreen.save()
    offscreen.translate(50.0, 50.0)
    offscreen.drawPath(create_star(), paint)
    offscreen.restore()

    image = cpuSurface.makeImageSnapshot()

    rotation = 0
    font = Font()
    import random
    while not state.fQuit:
        random.seed(0)
        canvas.clear(ColorWHITE)
        handle_events(state, canvas)

        paint.setColor(ColorBLACK)
        canvas.translate(0, 2 * font.getSize())
        canvas.drawString(helpMessage, 100, 100, font, paint)
        canvas.translate(0,-2 * font.getSize())
        for rect in state.fRects:
            paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            canvas.drawRect(rect, paint)

        canvas.save()
        canvas.translate(dm.w / 2.0, dm.h / 2.0)
        canvas.rotate(rotation)
        rotation+=1
        canvas.drawImage(image, -50.0, -50.0)
        canvas.restore()

        canvas.flush()

        SDL_GL_SwapWindow(window)

    if glContext:
        SDL_GL_DeleteContext(glContext)

    SDL_DestroyWindow(window)

    SDL_Quit();
    return 0

if __name__ == '__main__':
    import sys
    main(sys.argv)
