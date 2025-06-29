import sys
import math
import numpy as np
import skia
from PIL import Image
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import QTimer, Qt

GLASSMORPHIC_SKSL = """
uniform shader content;
uniform shader blur;
uniform shader noise;
uniform vec4 rectangle;
uniform float radius;
uniform float dropShadowSize;

float roundedRectangleSDF(vec2 position, vec2 box, float radius) {
    vec2 q = abs(position) - box + vec2(radius);
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - radius;   
}
vec4 main(vec2 coord) {
    vec2 shiftRect = (rectangle.zw - rectangle.xy) / 2.0;
    vec2 shiftCoord = coord - rectangle.xy;
    float distanceToClosestEdge = roundedRectangleSDF(
        shiftCoord - shiftRect, shiftRect, radius);

    vec4 c = content.eval(coord);
    if (distanceToClosestEdge > 0.0) {
        if (distanceToClosestEdge < dropShadowSize) {
            float darkenFactor = (dropShadowSize - distanceToClosestEdge) / dropShadowSize;
            darkenFactor = pow(darkenFactor, 1.6);
            return c * (0.9 + (1.0 - darkenFactor) / 10.0);
        }
        return c;
    }
    vec4 b = blur.eval(coord);
    vec4 n = noise.eval(coord);
    float lightenFactor = min(1.0, length(coord - rectangle.xy) / (0.85 * length(rectangle.zw - rectangle.xy)));
    float noiseLuminance = dot(n.rgb, vec3(0.2126, 0.7152, 0.0722));
    lightenFactor = min(1.0, lightenFactor + noiseLuminance);
    return b + (vec4(1.0) - b) * (0.35 - 0.25 * lightenFactor);
}
"""

def pil_noise_to_skimage(size):
    arr = (np.random.rand(size, size, 3) * 255).astype(np.uint8)
    img = Image.fromarray(arr, 'RGB')
    return skia.Image.fromarray(np.array(img))

class GlassmorphicWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Glassmorphic Card - Live Skia/SkSL Demo")
        self.W, self.H = 510, 370
        self.resize(self.W, self.H)
        self.setMinimumSize(self.W, self.H)
        self.setMaximumSize(self.W, self.H)
        self.effect = skia.RuntimeEffect.MakeForShader(GLASSMORPHIC_SKSL)[0]
        self.noise_size = max(self.W, self.H)
        self.noise_image = pil_noise_to_skimage(self.noise_size)
        self.t = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS

    def animate(self):
        self.t += 1
        self.update()

    def generate_content_image(self):
        # Animate one of the circles for some visual effect
        t = self.t / 30.0
        x = 375 + math.sin(t) * 30
        y = 125 + math.cos(t/3) * 10

        surface = skia.Surface(self.W, self.H)
        canvas = surface.getCanvas()
        canvas.clear(skia.ColorSetRGB(3, 8, 13))  # dark bg

        grad1 = skia.GradientShader.MakeLinear(
            points=[skia.Point(450, 60), skia.Point(290, 190)],
            colors=[skia.ColorSetRGB(0x7A, 0x26, 0xD9), skia.ColorSetRGB(0xE4, 0x44, 0xE1)],
        )
        paint = skia.Paint(Shader=grad1)
        canvas.drawCircle(x, y, 100, paint)

        paint = skia.Paint(Color=skia.ColorSetRGB(0xEA, 0x35, 0x7C))
        canvas.drawCircle(100, 265, 55, paint)

        grad2 = skia.GradientShader.MakeLinear(
            points=[skia.Point(180, 125), skia.Point(230, 125)],
            colors=[skia.ColorSetRGB(0xEA, 0x33, 0x4C), skia.ColorSetRGB(0xEC, 0x60, 0x51)],
        )
        paint = skia.Paint(Shader=grad2)
        canvas.drawCircle(205, 125, 25, paint)
        return surface.makeImageSnapshot()

    def paintEvent(self, event):
        # Prepare all Skia surfaces and shaders
        content_image = self.generate_content_image()
        blurred_image = content_image.makeWithFilter(
            skia.ImageFilter.MakeBlur(20.0, 20.0, skia.TileMode.kDecal), None)[0]

        rect = skia.Rect.MakeLTRB(85, 110, 405, 290)
        uniforms = {
            "rectangle": [rect.left(), rect.top(), rect.right(), rect.bottom()],
            "radius": 20.0,
            "dropShadowSize": 15.0,
        }
        children = {
            "content": content_image.makeShader(skia.TileMode.kClamp, skia.TileMode.kClamp),
            "blur": blurred_image.makeShader(skia.TileMode.kClamp, skia.TileMode.kClamp),
            "noise": self.noise_image.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat),
        }
        glass_shader = self.effect.makeShaderWithChildren(uniforms, children)

        final_surface = skia.Surface(self.W, self.H)
        final_canvas = final_surface.getCanvas()
        final_canvas.clear(skia.ColorSetRGB(3, 8, 13))

        paint = skia.Paint(Shader=glass_shader)
        final_canvas.drawRect(skia.Rect.MakeWH(self.W, self.H), paint)

        border_grad = skia.GradientShader.MakeLinear(
            points=[skia.Point(120, 110), skia.Point(405, 290)],
            colors=[
                skia.Color4f(1, 1, 1, 0.5).toColor(),
                skia.Color4f(1, 1, 1, 0.0).toColor(),
                skia.Color4f(0, 1, 0.85, 0.0).toColor(),
                skia.Color4f(0, 1, 0.85, 0.5).toColor(),
            ],
            positions=[0.0, 0.33, 0.66, 1.0],
        )
        border_paint = skia.Paint(Shader=border_grad, Style=skia.Paint.kStroke_Style, StrokeWidth=2)
        final_canvas.drawRoundRect(rect, 20, 20, border_paint)

        def draw_text(text, y, size):
            font = skia.Font(skia.Typeface('Arial', skia.FontStyle.Bold()), size)
            text_paint = skia.Paint(AntiAlias=True, Color=skia.ColorSetARGB(128, 255, 255, 255))
            final_canvas.drawString(text, 102, y, font, text_paint)

        draw_text("MEMBERSHIP", 150, 14)
        draw_text("JAMES APPLESEED", 250, 18)
        draw_text("PUSHING-PIXELS", 275, 13)

        # Convert Skia image to QImage for display
        img = final_surface.makeImageSnapshot()
        arr = np.array(img)
        qimg = QImage(arr.data, self.W, self.H, QImage.Format_RGBA8888)
        painter = QPainter(self)
        painter.drawImage(0, 0, qimg)
        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = GlassmorphicWidget()
    w.show()
    sys.exit(app.exec())