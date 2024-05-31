import skia
import sdl2

from OpenGL.GL import glGetString, GL_VENDOR, GL_RENDERER, GL_VERSION, GL_SHADING_LANGUAGE_VERSION, GL_RGBA8, glClear, GL_COLOR_BUFFER_BIT

path = skia.Path()
path.moveTo(184, 445)
path.lineTo(249, 445)
path.quadTo(278, 445, 298, 438)
path.quadTo(318, 431, 331, 419)
path.quadTo(344, 406, 350, 390)
path.quadTo(356, 373, 356, 354)
path.quadTo(356, 331, 347, 312)
path.quadTo(338, 292, 320, 280) # <- comment out this line and shape will draw correctly with anti-aliasing
path.close()

sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING)
sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_STENCIL_SIZE, 8 )
sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 2)
sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_PROFILE_MASK,
                         sdl2.SDL_GL_CONTEXT_PROFILE_CORE)
sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, 1)
sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_DOUBLEBUFFER, 1)
sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_DEPTH_SIZE, 24)

window = sdl2.SDL_CreateWindow(
    b"OpenGL demo",
    sdl2.SDL_WINDOWPOS_UNDEFINED,
    sdl2.SDL_WINDOWPOS_UNDEFINED,
    800, 640,
    sdl2.SDL_WINDOW_OPENGL)
if not window:
    sys.stderr.write("Error: Could not create window\n")
    exit(1)
sdl_glcontext = sdl2.SDL_GL_CreateContext(window)
sdl2.SDL_GL_MakeCurrent(window, sdl_glcontext)

print(glGetString(GL_VENDOR))
print(glGetString(GL_RENDERER))
print(glGetString(GL_VERSION))
print(glGetString(GL_SHADING_LANGUAGE_VERSION))

context = skia.GrDirectContext.MakeGL()
assert context is not None

backend_render_target = skia.GrBackendRenderTarget(
    800,
    640,
    0,  # sampleCnt
    0,  # stencilBits
    skia.GrGLFramebufferInfo(0, GL_RGBA8))
surface = skia.Surface.MakeFromBackendRenderTarget(
    context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
    skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
assert surface is not None

glClear(GL_COLOR_BUFFER_BIT)

with surface as canvas:
    canvas.drawCircle(100, 100, 40, skia.Paint(Color=skia.ColorGREEN, AntiAlias=True))

    paint = skia.Paint(Color=skia.ColorBLUE)
    paint.setStyle(skia.Paint.kStroke_Style)
    paint.setStrokeWidth(2)
    paint.setAntiAlias(True)

    canvas.drawPath(path, paint)
surface.flushAndSubmit()
sdl2.SDL_GL_SwapWindow(window)
import time
time.sleep(1)
