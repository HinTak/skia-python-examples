import glfw
import skia
import time
import math

# Initialize GLFW and create window
if not glfw.init():
    raise RuntimeError("Failed to initialize GLFW")
glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
window = glfw.create_window(640, 480, "Skia + OpenGL Example", None, None)
if not window:
    glfw.terminate()
    raise RuntimeError("Failed to create window")
glfw.make_context_current(window)

# Create Skia GPU context (OpenGL)
context = skia.GrDirectContext.MakeGL()
surface = skia.Surface.MakeRenderTarget(
    context,
    skia.Budgeted.kNo,
    skia.ImageInfo.Make(640, 480, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType),
    0,
    skia.SurfaceProps()
)

angle = 0.0
while not glfw.window_should_close(window):
    glfw.poll_events()
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)

    # Draw rotating rectangle
    paint = skia.Paint(Color=skia.ColorBLUE)
    canvas.save()
    canvas.translate(320, 240)
    canvas.rotate(angle)
    canvas.drawRect(skia.Rect.MakeLTRB(-100, -50, 100, 50), paint)
    canvas.restore()

    surface.flushAndSubmit()
    glfw.swap_buffers(window)
    angle += 1.0
    time.sleep(1/60)

glfw.destroy_window(window)
glfw.terminate()