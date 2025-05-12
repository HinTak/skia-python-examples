#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2025, Hin-Tak Leung

# SDL2 + SkSL SkiaSimpleShaderViewer

# Loads a *.sksl file, as is, from the "shaders" directory of
# https://github.com/jimmckeeth/SkiaSimpleShaderViewer/ .

# Requires at least skia-python v137+

from sdl2 import *
import skia
from skia import Paint, Rect, Font, Typeface, ColorWHITE
from OpenGL import GL
import ctypes
import time

width, height = 512, 512
title = b"Python SkiaSimpleShaderViewer"

builder = None

def setBuilder(input_file):
    global builder
    from skia import RuntimeEffect, RuntimeShaderBuilder
    litEffect = RuntimeEffect.MakeForShader(input_file)
    builder = RuntimeShaderBuilder(litEffect)

def draw(canvas, timenow):
    builder.setUniform("iTime", timenow)
    paint = Paint()
    paint.setShader(builder.makeShader())
    canvas.drawRect(Rect(0,0,512,512), paint)

def main():
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
    font = Font(Typeface("Roman"))
    paintWHITE = Paint()
    paintWHITE.setColor(ColorWHITE)
    initial_time = time.time()

    while running:
        while SDL_PollEvent(event):
            if event.type == SDL_QUIT:
                print("Quit event received.")
                running = False
                break

        if not running:
            break
        
        GL.glClearColor(0.0, 0.0, 0.0, 1.0) # Black background
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
        
        with surface as canvas:
            draw(canvas, time.time() - initial_time)
        surface.flushAndSubmit()
        
        SDL_GL_SwapWindow(window)

    context.abandonContext()

    if gl_context:
        SDL_GL_DeleteContext(gl_context)
    if window:
        SDL_DestroyWindow(window)
            
    SDL_Quit()

if __name__ == '__main__':
'''
In the context of GLSL shaders for OpenGL, iDate is a built-in uniform variable often used in shaders to access the current date and time. It's a vec4 (4-element vector) containing the year, month, day, and optionally, the time of day.

iDate is a predefined variable that ShaderToy and similar environments provide to shaders. OpenGL itself doesn't automatically set it, so you'll need to use a GLSL-compatible environment (like ShaderToy) that provides this value.

The iDate uniform is a vec4 which means it contains four floating-point values. These typically represent:
Year
Month
Day
Time of day (often represented as a float between 0 and 1, representing the fraction of the day that has passed)
'''
    import sys
    with open(sys.argv[1]) as f:
        content = f.readlines();
        whole_input = "".join(content)
        #print("".join([i for i in content if 'uniform' in i]))
        setBuilder(whole_input)

    #print(builder.uniforms()) - SkData
    #print(builder.children(), len(builder.children()))
    uniforms = builder.effect().uniforms()
    print("uniforms(inputs):")
    for uniform in uniforms:
        print("\t", uniform.type, "\t", uniform.name)
    # builder.children() - childptr don't have names
    bdchildren = builder.children()
    if (len(bdchildren) > 0):
        print("builder childen: (No Type before setting)")
        for child in bdchildren:
            print("\t", child.type)
    children = builder.effect().children()
    if (len(children) > 0):
        print("childen(inputs):")
        for child in children:
            print("\t", child.type, "\t", child.name)
    if (builder.uniform("iResolution").type == skia.RuntimeEffect.UniformType.kFloat2):
        builder.setUniform("iResolution", [512, 512])
    elif (builder.uniform("iResolution").type == skia.RuntimeEffect.UniformType.kFloat3):
        builder.setUniform("iResolution", [512, 512, 512])
    else:
        print("Unknown iResolution type:", builder.uniform("iResolution").type)
        assert False

    image = skia.Image.open("8de3a3924cb95bd0e95a443fff0326c869f9d4979cd1d5b6e94e2a01f5be53e9.jpg")
    if (builder.uniform("iImage1Resolution").type == skia.RuntimeEffect.UniformType.kFloat2):
        builder.setUniform("iImage1Resolution", [512, 512])
    elif (builder.uniform("iImage1Resolution").type == skia.RuntimeEffect.UniformType.kFloat3):
        builder.setUniform("iImage1Resolution", [512, 512, 512])
    elif (builder.uniform("iImage1Resolution").type == None):
        # Does not exist, okay
        pass
    else:
        print("Unknown iResolution type:", builder.uniform("iResolution").type)
        assert False

    if (builder.child("iImage1").type == skia.RuntimeEffect.ChildType.kShader):
        builder.setChild("iImage1", image.makeShader(skia.SamplingOptions(skia.FilterMode.kLinear)))
    if (len(bdchildren) > 0):
        print("builder dchilden: (Type setted)")
        for child in bdchildren:
            print("\t", child.type)
    main()
