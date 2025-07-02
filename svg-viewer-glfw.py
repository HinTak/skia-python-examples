# Simple SVG code - works on the 1st/3rd but not the 2nd: (3 tigers in my hard drive)

# github.com/wieslawsoltes/Svg.Skia/raw/master/tests/Tests/__tiger.svg
# /usr/share/doc/python-wxpython4-doc/demo/data/0-tiger.svg
# /usr/share/elementary/images/tiger.svg

import skia
import glfw
import os

from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, GL_RGBA8

print(glfw._glfw)

is_headless = False
if "CI" in os.environ or "GITHUB_RUN_ID" in os.environ:
    is_headless = True
    print("Headless mode")

if is_headless:
    glfw.init_hint(glfw.COCOA_MENUBAR, glfw.FALSE)

if not glfw.init():
    raise RuntimeError('glfw.init() failed')
glfw.window_hint(glfw.STENCIL_BITS, 8)
# see https://www.glfw.org/faq#macos
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
#
if is_headless:
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(640, 480, '', None, None)
glfw.make_context_current(window)

context = skia.GrDirectContext.MakeGL()
assert context is not None

import sys, os
svg_path = sys.argv[1]
if os.path.exists(svg_path):
    svgstream = skia.Stream.MakeFromFile(svg_path)
    svg_picture = skia.SVGDOM.MakeFromStream(svgstream)

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
    svg_picture.render(canvas)

surface.flushAndSubmit()
glfw.swap_buffers(window)
import time
time.sleep(1)
