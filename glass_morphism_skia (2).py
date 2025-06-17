import sys
import skia
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QImage, QPainter

WIDTH, HEIGHT = 600, 400

class GlassMorphismWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Glass Morphism Skia (No numpy/PIL)')
        self.resize(WIDTH, HEIGHT)
        self.blur_radius = 20.0
        self.opacity = 0.3
        self.drag_slider = None

        # Slider positions and sizes
        self.slider_rects = {
            'blur': QRect(50, HEIGHT-60, 200, 20),
            'alpha': QRect(350, HEIGHT-60, 200, 20),
        }

        self.slider_knobs = {
            'blur': 50 + int((self.blur_radius/50.0)*200),
            'alpha': 350 + int(self.opacity*200),
        }

    def paintEvent(self, event):
        surface = skia.Surface(WIDTH, HEIGHT)
        canvas = surface.getCanvas()

        # Draw background
        paint = skia.Paint()
        grad = skia.GradientShader.MakeLinear(
            points=[(0,0), (WIDTH,HEIGHT)],
            colors=[skia.ColorBLUE, skia.ColorWHITE, skia.ColorGREEN],
            positions=[0.0, 0.5, 1.0],
        )
        paint.setShader(grad)
        canvas.drawRect(skia.Rect.MakeWH(WIDTH, HEIGHT), paint)

        # Draw some shapes
        paint = skia.Paint(Color=skia.ColorRED)
        canvas.drawCircle(200, 130, 60, paint)
        paint.setColor(skia.ColorYELLOW)
        canvas.drawRect(skia.Rect.MakeXYWH(320, 100, 120, 120), paint)

        # Glass Morphism area (rounded rectangle)
        glass_rect = skia.Rect.MakeXYWH(140, 80, 320, 180)
        # 1. Extract background as image
        img = surface.makeImageSnapshot()
        # 2. Crop area under glass_rect
        sub_img = img.makeSubset(glass_rect.round())
        # 3. Blur with runtime effect
        blur_shader = skia.ImageFilters.Blur(
            sigmaX=self.blur_radius,
            sigmaY=self.blur_radius,
            tileMode=skia.TileMode.kClamp,
        )
        blur_paint = skia.Paint(ImageFilter=blur_shader)
        # 4. Compose: draw blurred area to a new surface
        glass_surface = skia.Surface(int(glass_rect.width()), int(glass_rect.height()))
        glass_canvas = glass_surface.getCanvas()
        glass_canvas.drawImage(sub_img, 0, 0, blur_paint)

        # 5. Overlay white with adjustable opacity
        overlay = skia.Paint(
            Color=skia.ColorWHITE,
            AlphalF=self.opacity
        )
        glass_canvas.drawRect(skia.Rect.MakeWH(glass_rect.width(), glass_rect.height()), overlay)

        # 6. Draw border
        border_paint = skia.Paint(
            Color=skia.ColorSetARGB(120, 255, 255, 255),
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=2
        )
        glass_canvas.drawRRect(
            skia.RRect.MakeRectXY(
                skia.Rect.MakeWH(glass_rect.width(), glass_rect.height()),
                30, 30
            ),
            border_paint
        )

        # 7. Draw the glass area back onto main canvas
        canvas.save()
        canvas.clipRRect(
            skia.RRect.MakeRectXY(glass_rect, 30, 30), doAntiAlias=True
        )
        canvas.drawImage(glass_surface.makeImageSnapshot(), glass_rect.left(), glass_rect.top())
        canvas.restore()

        # 8. Draw sliders
        qp = QPainter(self)
        qimg = QImage(surface.makeImageSnapshot().tobytes(), WIDTH, HEIGHT, QImage.Format_RGBA8888)
        qp.drawImage(0, 0, qimg)

        # Draw blur slider
        qp.setPen(Qt.gray)
        qp.setBrush(Qt.lightGray)
        qp.drawRect(self.slider_rects['blur'])
        qp.setBrush(Qt.blue)
        qp.drawEllipse(self.slider_knobs['blur']-10, HEIGHT-65, 20, 30)
        qp.drawText(50, HEIGHT-70, 'Blur')

        # Draw alpha slider
        qp.setBrush(Qt.lightGray)
        qp.drawRect(self.slider_rects['alpha'])
        qp.setBrush(Qt.darkGray)
        qp.drawEllipse(self.slider_knobs['alpha']-10, HEIGHT-65, 20, 30)
        qp.drawText(350, HEIGHT-70, 'Opacity')

        qp.end()

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        for name, rect in self.slider_rects.items():
            if rect.contains(x, y):
                self.drag_slider = name
                break

    def mouseMoveEvent(self, event):
        if self.drag_slider:
            x = event.x()
            rect = self.slider_rects[self.drag_slider]
            x = max(rect.left(), min(x, rect.right()))
            self.slider_knobs[self.drag_slider] = x
            if self.drag_slider == 'blur':
                self.blur_radius = 0.0 + 50.0 * ((x - rect.left())/rect.width())
            elif self.drag_slider == 'alpha':
                self.opacity = 0.0 + 1.0 * ((x - rect.left())/rect.width())
            self.update()

    def mouseReleaseEvent(self, event):
        self.drag_slider = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = GlassMorphismWidget()
    w.show()
    sys.exit(app.exec_())