import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtOpenGL import QOpenGLWidget
import skia
import OpenGL.GL as gl

class SkiaGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.gr_context = None
        self.surface = None
        self.mouse_pos = (0, 0)
        self.setMinimumSize(400, 400)

    def initializeGL(self):
        # Set up Skia with the current OpenGL context
        interface = skia.GrGLMakeNativeInterface()
        self.gr_context = skia.GrDirectContext.MakeGL(interface)
        self._create_surface()

    def resizeGL(self, w, h):
        # Handle resizing - re-create Skia surface
        self._create_surface()

    def paintGL(self):
        if self.surface is None:
            return
        canvas = self.surface.getCanvas()
        canvas.clear(skia.ColorWHITE)
        # Example: draw a red circle where the mouse is
        paint = skia.Paint(Color=skia.ColorRED, AntiAlias=True)
        canvas.drawCircle(self.mouse_pos[0], self.mouse_pos[1], 40, paint)
        # Add your Skia API drawing calls here,
        # preserving what was in your SDL example.

        canvas.flush()
        self.gr_context.flush()
        self.swapBuffers()

    def mouseMoveEvent(self, event):
        self.mouse_pos = (event.x(), event.y())
        self.update()

    def _create_surface(self):
        # Called in initializeGL and resizeGL to (re)create the Skia surface
        w, h = self.width(), self.height()
        fb_id = self.defaultFramebufferObject()
        if w == 0 or h == 0:
            self.surface = None
            return
        backend_render_target = skia.GrBackendRenderTarget(
            w, h,
            0,  # sampleCnt
            0,  # stencilBits
            skia.GrGLFramebufferInfo(fb_id, gl.GL_RGBA8)
        )
        surface = skia.Surface.MakeFromBackendRenderTarget(
            self.gr_context,
            backend_render_target,
            skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType,
            skia.ColorSpace.MakeSRGB()
        )
        self.surface = surface

    def swapBuffers(self):
        # Qt handles buffer swapping for us; nothing needed here.
        pass

    def closeEvent(self, event):
        if self.surface:
            self.surface = None
        if self.gr_context:
            self.gr_context.abandonContext()
            self.gr_context = None
        event.accept()

class SkiaQtMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Skia + PyQt5 OpenGL Example")
        self.skia_widget = SkiaGLWidget(self)
        self.setCentralWidget(self.skia_widget)
        self.resize(640, 480)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SkiaQtMainWindow()
    win.show()
    sys.exit(app.exec_())