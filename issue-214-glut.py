import skia

from OpenGL.GLUT import glutInit, glutInitDisplayMode, GLUT_DOUBLE, GLUT_RGBA, GLUT_3_2_CORE_PROFILE, glutInitWindowSize, glutCreateWindow, \
    glutSwapBuffers, glutPostRedisplay, glutDisplayFunc, glutMainLoop, glutMainLoopEvent
from OpenGL.GL import GL_RGBA8, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, \
    glGetString, GL_VENDOR, GL_RENDERER, GL_VERSION, GL_SHADING_LANGUAGE_VERSION

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

glutInit()
# GLUT_3_2_CORE_PROFILE is mac os x specific, but FreeGLLUT/Linux doesn't mind:
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_3_2_CORE_PROFILE)
glutInitWindowSize(600, 480)
glutCreateWindow(b"OpenGL Window")

context = skia.GrDirectContext.MakeGL()

print(glGetString(GL_VENDOR))
print(glGetString(GL_RENDERER))
print(glGetString(GL_VERSION))
print(glGetString(GL_SHADING_LANGUAGE_VERSION))

backend_render_target = skia.GrBackendRenderTarget(
    600,
    480,
    0,  # sampleCnt
    0,  # stencilBits
    skia.GrGLFramebufferInfo(0, GL_RGBA8))
surface = skia.Surface.MakeFromBackendRenderTarget(
    context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
    skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
assert surface is not None

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    with surface as canvas:
        canvas.drawCircle(100, 100, 40, skia.Paint(Color=skia.ColorGREEN, AntiAlias=True))

        paint = skia.Paint(Color=skia.ColorBLUE)
        paint.setStyle(skia.Paint.kStroke_Style)
        paint.setStrokeWidth(2)
        paint.setAntiAlias(True)

        canvas.drawPath(path, paint)

    surface.flushAndSubmit()
    glutSwapBuffers()
    glutPostRedisplay()
display()
import time
time.sleep(1)
