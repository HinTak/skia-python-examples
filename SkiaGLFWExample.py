import glfw
from OpenGL.GL import *
import skia
import sys
import random

class ApplicationState:
    def __init__(self, width, height):
        self.fQuit = False
        self.window_width = width
        self.window_height = height
        self.fRects = []

def create_star():
    kNumPoints = 5
    concavePath = skia.Path()
    points = [skia.Point(0, -50)]
    rot = skia.Matrix()
    rot.setRotate(360.0 / kNumPoints)
    for i in range(kNumPoints - 1):
        points.append(rot.mapPoints(points[i:i+1])[0])
    concavePath.moveTo(points[0])
    for i in range(kNumPoints):
        concavePath.lineTo(points[(2 * i) % kNumPoints])
    concavePath.setFillType(skia.PathFillType.kEvenOdd)
    assert not concavePath.isConvex()
    concavePath.close()
    return concavePath

def main():
    if not glfw.init():
        print("Could not initialize GLFW")
        return 1

    # OpenGL 3.3 Core
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)

    # Create window
    scr_width, scr_height = 800, 600
    window = glfw.create_window(scr_width, scr_height, "Skia + GLFW Example", None, None)
    if not window:
        glfw.terminate()
        print("Could not create GLFW window")
        return 1

    glfw.make_context_current(window)
    glClearColor(1, 1, 1, 1)
    glClearStencil(0)
    glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
    glViewport(0, 0, scr_width, scr_height)

    # Skia context
    grContext = skia.GrDirectContext.MakeGL()
    assert grContext is not None

    # Setup Skia render target for the window's framebuffer
    info = skia.GrGLFramebufferInfo(0, GL_RGBA8)
    kMsaaSampleCount = 0
    kStencilBits = 8
    target = skia.GrBackendRenderTarget(
        scr_width, scr_height, kMsaaSampleCount, kStencilBits, info
    )
    props = skia.SurfaceProps(skia.SurfaceProps.kUseDeviceIndependentFonts_Flag,
                             skia.PixelGeometry.kUnknown_PixelGeometry)
    surface = skia.Surface.MakeFromBackendRenderTarget(
        grContext, target,
        skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType, None, props
    )
    assert surface is not None
    canvas = surface.getCanvas()

    state = ApplicationState(scr_width, scr_height)
    helpMessage = "Click and drag to create rects.  Press esc to quit."
    paint = skia.Paint()
    font = skia.Font()

    # Star image for spinning
    cpuSurface = skia.Surface.MakeRaster(canvas.imageInfo())
    offscreen = cpuSurface.getCanvas()
    offscreen.save()
    offscreen.translate(50.0, 50.0)
    offscreen.drawPath(create_star(), paint)
    offscreen.restore()
    image = cpuSurface.makeImageSnapshot()

    drawing = False
    rect_start = (0, 0)
    rotation = 0

    def framebuffer_size_callback(window, width, height):
        state.window_width, state.window_height = width, height
        glViewport(0, 0, width, height)

    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    while not glfw.window_should_close(window) and not state.fQuit:
        random.seed(0)
        canvas.clear(skia.ColorWHITE)

        # Event handling
        glfw.poll_events()
        # Mouse input
        lmb_down = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS
        x, y = glfw.get_cursor_pos(window)
        y = state.window_height - y  # invert y so origin is top-left

        if lmb_down and not drawing:
            drawing = True
            rect_start = (x, y)
            state.fRects.append(skia.Rect.MakeLTRB(x, y, x, y))
        elif drawing and lmb_down:
            # Update last rect
            rect = state.fRects.pop()
            rect.fRight = x
            rect.fBottom = y
            state.fRects.append(rect)
        elif drawing and not lmb_down:
            drawing = False

        # Keyboard input
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            state.fQuit = True

        # Resize if needed
        width, height = glfw.get_framebuffer_size(window)
        if width != state.window_width or height != state.window_height:
            framebuffer_size_callback(window, width, height)

        # Draw help message
        paint.setColor(skia.ColorBLACK)
        canvas.drawString(helpMessage, 0, font.getSize(), font, paint)

        # Draw rectangles
        for rect in state.fRects:
            paint.setColor(random.randint(0, 0xFFFFFFFF) | 0x44808080)
            canvas.drawRect(rect, paint)

        # Draw spinning star image in center
        canvas.save()
        canvas.translate(state.window_width / 2.0, state.window_height / 2.0)
        canvas.rotate(rotation)
        rotation += 1
        canvas.drawImage(image, -50.0, -50.0)
        canvas.restore()

        canvas.flush()
        glfw.swap_buffers(window)

    glfw.destroy_window(window)
    glfw.terminate()
    return 0

if __name__ == '__main__':
    sys.exit(main())
