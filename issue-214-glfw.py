import skia
import glfw

from OpenGL.GL import glGetString, GL_VENDOR, GL_RENDERER, GL_VERSION, GL_SHADING_LANGUAGE_VERSION, \
    glClear, GL_COLOR_BUFFER_BIT, \
    GL_RGBA8

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

print(glfw._glfw)

if not glfw.init():
    raise RuntimeError('glfw.init() failed')
glfw.window_hint(glfw.STENCIL_BITS, 8)
# see https://www.glfw.org/faq#macos
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
window = glfw.create_window(640, 480, '', None, None)
glfw.make_context_current(window)

print(glGetString(GL_VENDOR))
print(glGetString(GL_RENDERER))
print(glGetString(GL_VERSION))
print(glGetString(GL_SHADING_LANGUAGE_VERSION))

context = skia.GrDirectContext.MakeGL()
assert context is not None

(fb_width, fb_height) = glfw.get_framebuffer_size(window)
backend_render_target = skia.GrBackendRenderTarget(
    fb_width,
    fb_height,
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
glfw.swap_buffers(window)
import time
time.sleep(1)
