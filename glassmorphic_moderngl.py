import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget
import moderngl

# The GLSL fragment shader from the original Kotlin code, adapted for moderngl
GLASSMORPHIC_FRAGMENT_SHADER = """
#version 330

uniform sampler2D content;
uniform sampler2D blur;
uniform sampler2D noise;

uniform vec4 rectangle;
uniform float radius;
uniform float dropShadowSize;

in vec2 v_text;
out vec4 f_color;

// SDF for rounded rectangle
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

GLASSMORPHIC_VERTEX_SHADER = """
#version 330

in vec2 in_vert;
out vec2 v_text;

void main() {
    v_text = in_vert;
    gl_Position = vec4((in_vert - 0.5) * 2.0, 0.0, 1.0);
}
"""

class GlassmorphicOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prog = None
        self.vao = None

    def initializeGL(self):
        self.ctx = moderngl.create_context()
        # Compile shader program
        self.prog = self.ctx.program(
            vertex_shader=GLASSMORPHIC_VERTEX_SHADER,
            fragment_shader=GLASSMORPHIC_FRAGMENT_SHADER,
        )
        # Simple full-screen quad (0..1 UV)
        vertices = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,
        ], dtype='f4')
        vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'in_vert')

        # Dummy textures (white) for content, blur, noise
        tex_data = np.ones((256, 256, 3), dtype=np.uint8) * 255
        self.texture_content = self.ctx.texture((256, 256), 3, tex_data.tobytes())
        self.texture_blur = self.ctx.texture((256, 256), 3, tex_data.tobytes())
        self.texture_noise = self.ctx.texture((256, 256), 3, tex_data.tobytes())
        self.texture_content.use(location=0)
        self.texture_blur.use(location=1)
        self.texture_noise.use(location=2)

        # Set uniforms (rectangle, radius, dropShadowSize)
        self.prog['rectangle'].value = (0.33, 0.3, 0.8, 0.7)
        self.prog['radius'].value = 0.07
        self.prog['dropShadowSize'].value = 0.04

    def paintGL(self):
        self.ctx.clear(0.015, 0.03, 0.05, 1.0)
        # Update texture units
        self.texture_content.use(location=0)
        self.texture_blur.use(location=1)
        self.texture_noise.use(location=2)
        self.prog['content'].value = 0
        self.prog['blur'].value = 1
        self.prog['noise'].value = 2
        self.vao.render(moderngl.TRIANGLE_STRIP)

    def resizeGL(self, w, h):
        self.ctx.viewport = (0, 0, w, h)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glassmorphic Shader - moderngl, PySide6")
        self.setGeometry(100, 100, 800, 600)
        self.gl_widget = GlassmorphicOpenGLWidget(self)
        self.setCentralWidget(self.gl_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())