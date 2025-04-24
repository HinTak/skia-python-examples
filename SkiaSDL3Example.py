#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Skia + SDL3 example
#
#  Copyright 2025 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#
#  Based on Google's own Skia + SDL C++ example, chrome/m92:example/SkiaSDLExample.cpp

#  Ported to PySDL3, 2025

#  Notable difference (improvement!) with the c++ version:
#     - The instructional text "Click and drag to create rects.  Press esc to quit."
#       is drawn so that its top left corner is the top left corner of the window.
#       The original draws its *bottom* left corner somewhat arbitrarily at 100,100.
#     - The rotating star is drawn at the centre, even if the window
#       is resized. The original is at a fixed position relative to the bottom left corner.

from sdl3 import *
from ctypes import byref, c_int
from OpenGL.GL import glViewport, glClearColor, glClearStencil, glClear, GL_COLOR_BUFFER_BIT, GL_STENCIL_BUFFER_BIT, GL_RGBA8
import sys
if not sys.platform.startswith("win"):
    from OpenGL.GLES2.EXT.texture_storage import GL_BGRA8_EXT
from skia import *

class ApplicationState:
    def __init__(self, width, height):
        self.fQuit = False
        self.window_width = width
        self.window_height = height
        self.fRects = []

def handle_error():
    error = SDL_GetError()
    print(error)
    SDL_ClearError()


def handle_events(state, canvas):
    event = SDL_Event()
    while(SDL_PollEvent(byref(event))):
        if event.type == SDL_EVENT_MOUSE_MOTION:
            if event.motion.state == True:
                rect = state.fRects.pop()
                rect.fRight = event.motion.x
                rect.fBottom = event.motion.y
                state.fRects.append(rect)
        if event.type == SDL_EVENT_MOUSE_BUTTON_DOWN:
            if event.button.down == True:
                state.fRects.append(Rect.MakeLTRB(event.button.x,
                                                    event.button.y,
                                                    event.button.x,
                                                    event.button.y))
        if (event.type == SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED or event.type == SDL_EVENT_WINDOW_RESIZED):
            # Not interested in event.window.windowID
            #
            # SDL_EVENT_WINDOW_RESIZED
            #     window has been resized to data1 x data2; this event is always preceded by SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED
            # SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED
            #     window size has changed, either as a result of an API call or through the system or user changing the window size;
            #     this event is followed by SDL_EVENT_WINDOW_RESIZED if the size was changed by an external event, i.e. the user or the window manager
            if (event.window.type == SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED or
                event.window.type == SDL_EVENT_WINDOW_RESIZED):
                state.window_width = event.window.data1
                state.window_height = event.window.data2
        if event.type ==  SDL_EVENT_KEY_DOWN:
            if event.key.key == SDLK_ESCAPE:
                state.fQuit = True
        if event.type == SDL_EVENT_QUIT:
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

    if (not SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS)):
        handle_error()
        return 1

    num_displays = c_int(0)
    displays = SDL_GetDisplays(byref(num_displays))
    if (not displays or num_displays.value < 1):
        handle_error()
        return 1

    # Just use the first available display
    instance_id = displays[0]
    dm = SDL_GetDesktopDisplayMode(instance_id) 
    if (dm == None):
        handle_error()
        return 1

    # SDL2's SDL_CreateWindow() takes also SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED
    # for positioning. This is not particularly interesting, but can be done so in SDL3 with
    # SDL_CreateWindowWithProperties():
    #
    #     props = SDL_CreateProperties()
    #     SDL_SetStringProperty(props, SDL_PROP_WINDOW_CREATE_TITLE_STRING, ... )
    #     SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_X_NUMBER, SDL_WINDOWPOS_CENTERED)
    #     SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_Y_NUMBER, SDL_WINDOWPOS_CENTERED)
    #     SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_WIDTH_NUMBER, ...)
    #     SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_HEIGHT_NUMBER, ...)
    #     SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_FLAGS_NUMBER, ...)
    #     window = SDL_CreateWindowWithProperties(props)
    #
    # The fewer-arg SDL3 SDL_CreateWindow() works just as well for main window; the centering may be useful
    # for popup or modal windows.
    window = SDL_CreateWindow(b"SDL Window", dm.contents.w, dm.contents.h, windowFlags)

    if not window:
        handle_error()
        return 1

    glContext = SDL_GL_CreateContext(window)
    if not glContext:
        handle_error()
        return 1

    success =  SDL_GL_MakeCurrent(window, glContext)
    if not success:
        handle_error()
        return success

    windowFormat = SDL_GetWindowPixelFormat(window)
    contextType = c_int(0)
    SDL_GL_GetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, byref(contextType))
    
    dw = c_int(0)
    dh = c_int(0)
    ##SDL_GetWindowSizeInPixels(window, byref(dw), byref(dh)) # was SDL_GL_GetDrawableSize in SDL2
    #
    # SDL3 Note:
    #     Despite what the SDL3 migration said, SDL3's "SDL_GetWindowSizeInPixels()" cannot be used in
    #     place of SDL2's "SDL_GL_GetDrawableSize()".
    #     Rather, SDL2's "SDL_GL_GetDrawableSize()" always returns size of initial full desktop,
    #     whereas "SDL_GetWindowSizeInPixels()" is smaller, minus window manager estate and
    #     windows menu bar. So in SDL2, the canvas.scale(...) below was no-ops.
    dw.value = dm.contents.w
    dh.value = dm.contents.h

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
        if not sys.platform.startswith("win") and SDL_GL_CONTEXT_PROFILE_ES == contextType.value:
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
    canvas.scale(dw.value/dm.contents.w, dh.value/dm.contents.h)
    
    state = ApplicationState(dw.value, dh.value)

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
        canvas.translate(0, dh.value - state.window_height)
        canvas.drawString(helpMessage, 0, font.getSize(), font, paint)
        for rect in state.fRects:
            paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            canvas.drawRect(rect, paint)
        canvas.translate(0, -(dh.value - state.window_height))

        canvas.save()
        canvas.translate(state.window_width / 2.0, dh.value - state.window_height / 2.0)
        canvas.rotate(rotation)
        rotation+=1
        canvas.drawImage(image, -50.0, -50.0)
        canvas.restore()

        canvas.flush()

        SDL_GL_SwapWindow(window)

    if glContext:
        SDL_GL_DestroyContext(glContext)

    SDL_DestroyWindow(window)

    SDL_Quit();
    return 0

if __name__ == '__main__':
    import sys
    main(sys.argv)
