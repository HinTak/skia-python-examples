#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2025, Hin-Tak Leung

# SDL3 Re-write / simplication

# See https://github.com/HinTak/skia-python-examples/issues/6

from sdl3 import \
    SDLK_ESCAPE, SDL_CreateWindow, SDL_DestroyWindow, \
    SDL_EVENT_QUIT, \
    SDL_Event, SDL_GL_CONTEXT_MAJOR_VERSION, SDL_GL_CONTEXT_MINOR_VERSION, \
    SDL_GL_CONTEXT_PROFILE_CORE, SDL_GL_CONTEXT_PROFILE_MASK, \
    SDL_GL_CreateContext, SDL_GL_DEPTH_SIZE, SDL_GL_DOUBLEBUFFER, \
    SDL_GL_DestroyContext, \
    SDL_GL_GetAttribute, SDL_GL_MakeCurrent, SDL_GL_STENCIL_SIZE, \
    SDL_GL_SetAttribute, SDL_GL_SetSwapInterval, SDL_GL_SwapWindow, \
    SDL_GetError, SDL_GetWindowSizeInPixels, \
    SDL_INIT_VIDEO, SDL_Init, SDL_PollEvent, SDL_Quit, \
    SDL_WINDOW_OPENGL

import skia
from OpenGL import GL
import ctypes

width, height = 640, 480
title = b"Skia + PySDL3 Example"

def main():
    if not SDL_Init(SDL_INIT_VIDEO):
        raise RuntimeError(f"SDL_Init Error: {SDL_GetError()}")

    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)

    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 0)
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8)

    window = SDL_CreateWindow(
        title,
        width, height,
        SDL_WINDOW_OPENGL
    )
    if not window:
        raise RuntimeError(f"SDL_CreateWindow Error: {SDL_GetError()}")

    gl_context = SDL_GL_CreateContext(window)
    if not gl_context:
        SDL_DestroyWindow(window)
        raise RuntimeError(f"SDL_GL_CreateContext Error: {SDL_GetError()}")

    if not SDL_GL_MakeCurrent(window, gl_context):
         SDL_GL_DestroyContext(gl_context)
         SDL_DestroyWindow(window)
         raise RuntimeError(f"SDL_GL_MakeCurrent Error: {SDL_GetError()}")

    context = skia.GrDirectContext.MakeGL()
    if not context:
        raise RuntimeError("Failed to create Skia GrDirectContext")

    fb_width, fb_height = ctypes.c_int(), ctypes.c_int()
    SDL_GetWindowSizeInPixels(window, ctypes.byref(fb_width), ctypes.byref(fb_height))

    # Check how many stencil bits we actually got
    stencil_bits = ctypes.c_int()
    SDL_GL_GetAttribute(SDL_GL_STENCIL_SIZE,  ctypes.byref(stencil_bits))
    assert stencil_bits.value == 8

    backend_render_target = skia.GrBackendRenderTarget(
        fb_width.value,
        fb_height.value,
        0,  # sampleCnt (MSAA samples) | samples - usually 0 for direct to screen
        stencil_bits.value, # stencilBits - Use value retrieved from GL context
        # Framebuffer ID 0 means the default window framebuffer
        skia.GrGLFramebufferInfo(0, GL.GL_RGBA8) # Target format GL_RGBA8 | Use 0 for framebuffer object ID for default framebuffer
    )

    surface = skia.Surface.MakeFromBackendRenderTarget(
        context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())

    if surface is None:
        context.abandonContext()
        raise RuntimeError("Failed to create Skia Surface from BackendRenderTarget")

    running = True
    event = SDL_Event() # Create event structure once

    while running:
        while SDL_PollEvent(event):
            if event.type == SDL_EVENT_QUIT:
                print("Quit event received.")
                running = False
                break

        if not running:
            break
        
        GL.glClearColor(0.0, 0.0, 0.0, 1.0) # Black background
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
        
        with surface as canvas:
            # Example drawing: Clear with Skia color, draw circle
            canvas.clear(skia.ColorWHITE)
            paint = skia.Paint(
                Color=skia.ColorBLUE,
                StrokeWidth=2,
                Style=skia.Paint.kStroke_Style, # Make it an outline
                AntiAlias=True
            )
            canvas.drawCircle(width / 2, height / 2, 100, paint)
        
            paint.setColor(skia.ColorGREEN)
            paint.setStyle(skia.Paint.kFill_Style) # Fill style
            canvas.drawRect(skia.Rect.MakeXYWH(20, 20, 80, 80), paint)
        
        surface.flushAndSubmit()
        
        SDL_GL_SwapWindow(window)

    context.abandonContext()

    if gl_context:
        SDL_GL_DestroyContext(gl_context)
    if window:
        SDL_DestroyWindow(window)
            
    SDL_Quit()

if __name__ == '__main__':
    main()
