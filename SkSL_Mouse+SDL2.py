#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2025, Hin-Tak Leung

# SDL2 + SkSL

# iMouse example from from https://shaders.skia.org/
# Requires at least skia-python v132.b11

from sdl2 import *
import skia
from skia import Paint, Rect, Font, Typeface, ColorWHITE
from OpenGL import GL
import ctypes

width, height = 512, 512
title = b"Skia + PySDL2 + SkSL Example"

SkSL_code = [ """
// The iMouse uniform is always present and provides information
// about the mouse position and click state.
//
// We match the behavior of iMouse in shadertoy.com. See
// https://www.shadertoy.com/view/Mss3zH for more details.
//
// The iResolution uniform is always present and provides
// the canvas size in pixels. 
half4 main(float2 fragCoord) {
  float2 pct = fragCoord/iResolution.xy;
  float d = distance(pct, iMouse.xy/iResolution.xy);
  return half4(half3(1, 0, 0)*(1-d)*(1-d), 1);
}
"""]

def draw(canvas, builder, x, y):
    builder.setUniform("iMouse", [x, y, 0.0, 0.0])
    paint = Paint()
    paint.setShader(builder.makeShader())
    canvas.drawRect(Rect(0,0,512,512), paint)

def main(builder):
    if SDL_Init(SDL_INIT_VIDEO) != 0:
        raise RuntimeError(f"SDL_Init Error: {SDL_GetError()}")

    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)

    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 0)
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8)

    window = SDL_CreateWindow(
        title,
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        width, height,
        SDL_WINDOW_OPENGL
    )
    if not window:
        raise RuntimeError(f"SDL_CreateWindow Error: {SDL_GetError()}")

    gl_context = SDL_GL_CreateContext(window)
    if not gl_context:
        SDL_DestroyWindow(window)
        raise RuntimeError(f"SDL_GL_CreateContext Error: {SDL_GetError()}")

    if SDL_GL_MakeCurrent(window, gl_context) !=0:
         SDL_GL_DeleteContext(gl_context)
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
    step = 0
    x = 0
    y = 0
    font = Font(Typeface("Roman"))
    paint = Paint()
    paint.setColor(ColorWHITE)
    helpMessage = "Click to change hightlights"

    while running:
        while SDL_PollEvent(event):
            if event.type == SDL_QUIT:
                print("Quit event received.")
                running = False
                break
            if event.type == SDL_MOUSEBUTTONDOWN:
                if event.button.state == SDL_PRESSED:
                    x = event.button.x
                    y = event.button.y

        if not running:
            break
        
        GL.glClearColor(0.0, 0.0, 0.0, 1.0) # Black background
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)

        with surface as canvas:
            draw(canvas, builder, x, y)
            canvas.drawString(helpMessage, 0, font.getSize(), font, paint)
        surface.flushAndSubmit()
        
        SDL_GL_SwapWindow(window)

    context.abandonContext()

    if gl_context:
        SDL_GL_DeleteContext(gl_context)
    if window:
        SDL_DestroyWindow(window)
            
    SDL_Quit()

if __name__ == '__main__':
    from skia import RuntimeEffect, RuntimeShaderBuilder

    Shader_Inputs = """
uniform float3 iResolution;      // Viewport resolution (pixels)
uniform float  iTime;            // Shader playback time (s)
uniform float4 iMouse;           // Mouse drag pos=.xy Click pos=.zw (pixels)
uniform float3 iImageResolution; // iImage1 resolution (pixels)
uniform shader iImage1;          // An input image.
"""
    header = """
uniform float4 iMouse;
float4 iResolution = float4(512, 512, 512, 512);
"""
    litEffect = RuntimeEffect.MakeForShader(header + SkSL_code[0])
    builder = RuntimeShaderBuilder(litEffect)
    main(builder)
