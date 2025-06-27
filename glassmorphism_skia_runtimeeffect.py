import sys
import skia
import numpy as np
from PyQt5.QtWidgets import QApplication, QSlider, QLabel, QVBoxLayout, QWidget, QColorDialog, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

GLASS_SHADER_SRC = """
uniform shader image;
uniform float2 blur_size;
uniform float opacity;
uniform float3 tint;

half4 main(float2 xy) {
    // Sample blurred background
    half4 color = image.eval(xy);
    // Apply tint and opacity
    color.rgb = mix(color.rgb, tint, 0.4);
    color.a *= opacity;
    return color;
}
"""

def np_to_qimage(arr):
    """Convert a numpy array to QImage."""
    h, w, ch = arr.shape
    if ch == 3:
        fmt = QImage.Format_RGB888
    elif ch == 4:
        fmt = QImage.Format_RGBA8888
    else:
        raise ValueError("Unsupported channel number.")
    return QImage(arr.data, w, h, arr.strides[0], fmt).copy()

def blur_surface(surface, radius):
    """Apply a gaussian blur to the surface."""
    img = surface.makeImageSnapshot()
    blur_filter = skia.ImageFilters.Blur(radius, radius)
    paint = skia.Paint(ImageFilter=blur_filter)
    blur_surface = skia.Surface(surface.width(), surface.height())
    blur_surface.getCanvas().drawImage(img, 0, 0, skia.SamplingOptions(), paint)
    return blur_surface.makeImageSnapshot()

class GlassMorphismWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glass Morphism Skia Example")
        self.resize(480, 340)

        # Load a sample background image (replace with your own if desired)
        self.bg_arr = np.random.randint(0, 255, (320, 480, 4), np.uint8)
        self.bg_img = skia.Image.fromarray(self.bg_arr)

        self.blur_radius = 8.0
        self.opacity = 0.6
        self.tint = [0.8, 0.9, 1.0]  # Light blue tint

        # UI
        self.image_label = QLabel()
        self.slider_blur = QSlider(Qt.Horizontal)
        self.slider_blur.setMinimum(1)
        self.slider_blur.setMaximum(32)
        self.slider_blur.setValue(int(self.blur_radius))
        self.slider_blur.valueChanged.connect(self.update_image)

        self.slider_opacity = QSlider(Qt.Horizontal)
        self.slider_opacity.setMinimum(10)
        self.slider_opacity.setMaximum(100)
        self.slider_opacity.setValue(int(self.opacity * 100))
        self.slider_opacity.valueChanged.connect(self.update_image)

        self.btn_tint = QPushButton("Pick Tint Color")
        self.btn_tint.clicked.connect(self.pick_tint)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(QLabel("Blur Radius"))
        layout.addWidget(self.slider_blur)
        layout.addWidget(QLabel("Opacity"))
        layout.addWidget(self.slider_opacity)
        layout.addWidget(self.btn_tint)
        self.setLayout(layout)

        self.update_image()

    def pick_tint(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.tint = [color.redF(), color.greenF(), color.blueF()]
            self.update_image()

    def update_image(self):
        self.blur_radius = float(self.slider_blur.value())
        self.opacity = self.slider_opacity.value() / 100.0

        # Prepare surfaces
        surface = skia.Surface(480, 320)
        canvas = surface.getCanvas()
        # Draw background image
        canvas.drawImage(self.bg_img, 0, 0)

        # Draw glass morphism rectangle
        rect = skia.Rect.MakeXYWH(100, 80, 280, 160)
        # Blur the background under the glass
        blur_img = blur_surface(surface, self.blur_radius)

        # Create runtime effect for glass
        effect = skia.RuntimeEffect.MakeForShader(GLASS_SHADER_SRC)
        builder = skia.RuntimeShaderBuilder(effect)
        builder.setChild('image', blur_img.makeShader())
        builder.setUniform('blur_size', (self.blur_radius, self.blur_radius))
        builder.setUniform('opacity', self.opacity)
        builder.setUniform('tint', tuple(self.tint))
        shader = builder.makeShader()
        #shader = effect.makeShader(
        #    uniforms={
        #        'image': blur_img.makeShader(),
        #        'blur_size': (self.blur_radius, self.blur_radius),
        #        'opacity': self.opacity,
        #        'tint': tuple(self.tint),
        #    }
        #)

        paint = skia.Paint(Shader=shader)
        canvas.drawRect(rect, paint)

        # Optional: Draw border
        border_paint = skia.Paint(
            Color=skia.Color4f(1, 1, 1, 0.3),
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=2,
        )
        canvas.drawRect(rect, border_paint)

        # Display in Qt
        img = surface.makeImageSnapshot().toarray()
        qimg = np_to_qimage(img)
        pixmap = QPixmap.fromImage(qimg)
        self.image_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = GlassMorphismWidget()
    w.show()
    sys.exit(app.exec_())