import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPen, QBrush, QFont, QImage
from PySide6.QtOpenGLWidgets import QOpenGLWidget
import moderngl
from scipy.ndimage import gaussian_filter

def create_noise_texture(size):
    # Generates a grayscale noise image.
    noise = np.random.rand(size, size).astype(np.float32)
    return (noise * 255).astype(np.uint8)

def qimage_to_gl_texture(ctx, qimg):
    # Converts QImage to an OpenGL texture for moderngl.
    qimg = qimg.convertToFormat(QImage.Format_RGBA8888)
    ptr = qimg.bits()
    arr = np.array(ptr).reshape((qimg.height(), qimg.width(), 4))
    return ctx.texture((qimg.width(), qimg.height()), 4, arr.tobytes())

class GlassmorphicOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ctx = None
        self.prog = None
        self.vao = None
        self.tex_content = None
        self.tex_blur = None
        self.tex_noise = None
        self.framebuffer_data = None

    def initializeGL(self):
        self.ctx = moderngl.create_context()
        self.setMinimumSize(510, 370)

        # Compile shaders
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                out vec2 v_text;
                void main() {
                    v_text = in_vert;
                    gl_Position = vec4((in_vert - 0.5) * 2.0, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D content;
                uniform sampler2D blur;
                uniform sampler2D noise;
                uniform vec4 rectangle;
                uniform float radius;
                uniform float dropShadowSize;
                in vec2 v_text;
                out vec4 f_color;
                float roundedRectangleSDF(vec2 position, vec2 box, float radius) {
                    vec2 q = abs(position) - box + vec2(radius);
                    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - radius;
                }
                void main() {
                    vec2 coord = v_text;
                    vec2 shiftRect = (rectangle.zw - rectangle.xy) / 2.0;
                    vec2 shiftCoord = coord - rectangle.xy;
                    float distanceToClosestEdge = roundedRectangleSDF(
                        shiftCoord - shiftRect, shiftRect, radius);
                    vec4 c = texture(content, coord);
                    if (distanceToClosestEdge > 0.0) {
                        if (distanceToClosestEdge < dropShadowSize) {
                            float darkenFactor = (dropShadowSize - distanceToClosestEdge) / dropShadowSize;
                            darkenFactor = pow(darkenFactor, 1.6);
                            f_color = c * (0.9 + (1.0 - darkenFactor) / 10.0);
                            return;
                        }
                        f_color = c;
                        return;
                    }
                    vec4 b = texture(blur, coord);
                    vec4 n = texture(noise, coord);
                    float lightenFactor = min(1.0, length(coord - rectangle.xy) / (0.85 * length(rectangle.zw - rectangle.xy)));
                    float noiseLuminance = dot(n.rgb, vec3(0.2126, 0.7152, 0.0722));
                    lightenFactor = min(1.0, lightenFactor + noiseLuminance);
                    f_color = b + (vec4(1.0) - b) * (0.35 - 0.25 * lightenFactor);
                }
            """
        )

        # Fullscreen quad
        vertices = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,
        ], dtype='f4')
        vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'in_vert')

        # Prepare textures (dummy, will be updated in paintGL)
        self.tex_content = self.ctx.texture((self.width(), self.height()), 4)
        self.tex_blur = self.ctx.texture((self.width(), self.height()), 4)
        noise_data = create_noise_texture(max(self.width(), self.height()))
        self.tex_noise = self.ctx.texture((noise_data.shape[1], noise_data.shape[0]), 1, noise_data.tobytes())
        self.tex_noise.build_mipmaps()
        self.tex_noise.repeat_x = True
        self.tex_noise.repeat_y = True

    def paintGL(self):
        # Render colored circles/gradients to an offscreen QImage (content texture)
        qimg = QImage(self.width(), self.height(), QImage.Format_RGBA8888)
        qimg.fill(QColor(3, 8, 13, 255))  # bg
        painter = QPainter(qimg)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the colored circles to QImage
        grad1 = QLinearGradient(QPointF(450, 60), QPointF(290, 190))
        grad1.setColorAt(0, QColor(0x7A, 0x26, 0xD9))
        grad1.setColorAt(1, QColor(0xE4, 0x44, 0xE1))
        painter.setBrush(QBrush(grad1))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(375, 125), 100, 100)

        painter.setBrush(QColor(0xEA, 0x35, 0x7C))
        painter.drawEllipse(QPointF(100, 265), 55, 55)

        grad2 = QLinearGradient(QPointF(180, 125), QPointF(230, 125))
        grad2.setColorAt(0, QColor(0xEA, 0x33, 0x4C))
        grad2.setColorAt(1, QColor(0xEC, 0x60, 0x51))
        painter.setBrush(QBrush(grad2))
        painter.drawEllipse(QPointF(205, 125), 25, 25)

        painter.end()

        # Convert QImage to moderngl texture for content
        self.tex_content.release()
        self.tex_content = qimage_to_gl_texture(self.ctx, qimg)
        self.tex_content.use(location=0)

        # Create a blurred version (using numpy + scipy)
        arr = np.array(qimg.bits(), dtype=np.uint8).reshape((self.height(), self.width(), 4))
        arr_blur = gaussian_filter(arr.astype(np.float32), sigma=(15, 15, 0))
        arr_blur = np.clip(arr_blur, 0, 255).astype(np.uint8)
        qimg_blur = QImage(arr_blur.data, self.width(), self.height(), QImage.Format_RGBA8888)
        self.tex_blur.release()
        self.tex_blur = qimage_to_gl_texture(self.ctx, qimg_blur)
        self.tex_blur.use(location=1)

        # Noise texture (already set up)
        self.tex_noise.use(location=2)

        # Shader uniforms (rectangle as normalized coords)
        x1, y1, x2, y2 = 85, 110, 405, 290
        nx1, ny1 = x1 / self.width(), y1 / self.height()
        nx2, ny2 = x2 / self.width(), y2 / self.height()
        self.prog['rectangle'].value = (nx1, ny1, nx2, ny2)
        self.prog['radius'].value = 20 / self.width()
        self.prog['dropShadowSize'].value = 15 / self.width()
        self.prog['content'].value = 0
        self.prog['blur'].value = 1
        self.prog['noise'].value = 2

        self.ctx.clear(0.015, 0.03, 0.05, 1.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)

        # Save the framebuffer for later use in overlay painting
        data = self.ctx.screen.read(components=4, alignment=1)
        self.framebuffer_data = np.frombuffer(data, dtype=np.uint8).reshape((self.height(), self.width(), 4))

    def paintEvent(self, event):
        # Paint the GL result, then QPainter overlays
        super().paintEvent(event)
        painter = QPainter(self)
        if self.framebuffer_data is not None:
            # Draw the GL framebuffer as a QImage
            qimg = QImage(self.framebuffer_data.data, self.width(), self.height(), QImage.Format_RGBA8888)
            painter.drawImage(0, 0, qimg)

        # Draw glassmorphic border and text overlays
        border_grad = QLinearGradient(QPointF(120, 110), QPointF(405, 290))
        border_grad.setColorAt(0, QColor(255, 255, 255, 128))
        border_grad.setColorAt(0.33, QColor(255, 255, 255, 0))
        border_grad.setColorAt(0.66, QColor(0, 255, 72, 0))
        border_grad.setColorAt(1, QColor(0, 255, 72, 128))
        pen = QPen(QBrush(border_grad), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        rect = QRectF(86, 111, 318, 178)
        painter.drawRoundedRect(rect, 20, 20)

        font = QFont("Arial", 14, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 128))
        painter.drawText(QPointF(102, 150), "MEMBERSHIP")

        font.setPointSize(18)
        painter.setFont(font)
        painter.drawText(QPointF(102, 250), "JAMES APPLESEED")

        font.setPointSize(13)
        painter.setFont(font)
        painter.drawText(QPointF(102, 275), "PUSHING-PIXELS")

        painter.end()

    def resizeGL(self, w, h):
        # Force update of noise and textures
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glassmorphic Card - Full Demo")
        self.setGeometry(100, 100, 510, 370)
        central = QWidget()
        layout = QVBoxLayout(central)
        self.gl_widget = GlassmorphicOpenGLWidget(self)
        layout.addWidget(self.gl_widget)
        self.setCentralWidget(central)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())