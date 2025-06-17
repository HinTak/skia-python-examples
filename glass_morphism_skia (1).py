import skia
import tkinter as tk
from PIL import Image, ImageTk
import io

# SkSL for glass morphism (blur + tint + opacity)
GLASS_SKSL = """
uniform shader image;
uniform shader bg;
uniform float blur_strength;
uniform float opacity;
uniform float3 tint;

half4 main(float2 coord) {
    // Simple blur by averaging neighboring pixels
    half4 sum = half4(0.0);
    float2 offsets[9] = float2[9](
        float2(-blur_strength, -blur_strength), float2(0.0, -blur_strength), float2(blur_strength, -blur_strength),
        float2(-blur_strength, 0.0),           float2(0.0, 0.0),           float2(blur_strength, 0.0),
        float2(-blur_strength, blur_strength), float2(0.0, blur_strength), float2(blur_strength, blur_strength)
    );
    for (int i = 0; i < 9; ++i)
        sum += bg.eval(coord + offsets[i]);
    sum /= 9.0;

    // Apply tint + opacity
    sum.rgb = mix(sum.rgb, tint, 0.18);
    sum.a *= opacity;
    return sum;
}
"""

# Main application class
class GlassMorphismApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Glass Morphism with Skia-Python")
        self.canvas_width = 500
        self.canvas_height = 350

        # Skia surface setup
        self.surface = skia.Surface(self.canvas_width, self.canvas_height)
        self.bg_img = self.make_background()

        # Default parameters
        self.blur_strength = 6.0
        self.opacity = 0.70
        self.tint = (0.7, 0.85, 1.0)  # Light bluish

        # Tkinter UI
        self.tk_image = None
        self.label = tk.Label(master)
        self.label.pack()

        # Sliders
        self.blur_slider = tk.Scale(master, from_=0, to=20, orient=tk.HORIZONTAL, resolution=1,
                                    label="Blur Strength", command=self.on_change)
        self.blur_slider.set(self.blur_strength)
        self.blur_slider.pack(fill=tk.X)
        self.opacity_slider = tk.Scale(master, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01,
                                       label="Opacity", command=self.on_change)
        self.opacity_slider.set(self.opacity)
        self.opacity_slider.pack(fill=tk.X)
        self.tint_slider = tk.Scale(master, from_=0, to=360, orient=tk.HORIZONTAL, resolution=1,
                                    label="Tint Hue", command=self.on_change)
        self.tint_slider.set(200)
        self.tint_slider.pack(fill=tk.X)

        self.draw_image()

    def make_background(self):
        # Create a colorful background as an Skia image
        bg_surface = skia.Surface(self.canvas_width, self.canvas_height)
        canvas = bg_surface.getCanvas()

        # Draw gradient
        shader = skia.GradientShader.MakeLinear(
            points=[(0, 0), (self.canvas_width, self.canvas_height)],
            colors=[skia.ColorBLUE, skia.ColorYELLOW, skia.ColorRED],
            positions=[0.0, 0.7, 1.0]
        )
        paint = skia.Paint(Shader=shader)
        canvas.drawPaint(paint)

        # Draw shapes for some visual interest
        paint = skia.Paint(Color=skia.ColorSetARGB(200, 255, 255, 255))
        canvas.drawCircle(self.canvas_width//2, self.canvas_height//2, 100, paint)
        paint = skia.Paint(Color=skia.ColorSetARGB(100, 0, 0, 0))
        canvas.drawRect(skia.Rect.MakeXYWH(50, 250, 400, 40), paint)

        return bg_surface.makeImageSnapshot()

    def hsl_to_rgb(self, h, s, l):
        # Simple HSL to RGB conversion, h in 0..360
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60.0) % 2 - 1))
        m = l - c/2
        if h < 60: rp, gp, bp = c, x, 0
        elif h < 120: rp, gp, bp = x, c, 0
        elif h < 180: rp, gp, bp = 0, c, x
        elif h < 240: rp, gp, bp = 0, x, c
        elif h < 300: rp, gp, bp = x, 0, c
        else: rp, gp, bp = c, 0, x
        return (rp + m, gp + m, bp + m)

    def draw_image(self):
        canvas = self.surface.getCanvas()
        canvas.clear(skia.ColorWHITE)

        # Draw background
        canvas.drawImage(self.bg_img, 0, 0)

        # Prepare SkSL runtime effect
        effect = skia.RuntimeEffect.MakeForShader(GLASS_SKSL)
        # Make 'bg' shader from the background snapshot
        bg_shader = self.bg_img.makeShader(skia.TileMode.kClamp, skia.TileMode.kClamp)

        # Glass panel rectangle
        glass_rect = skia.Rect.MakeXYWH(100, 80, 300, 150)

        # Tint color from HSL slider
        hue = self.tint_slider.get()
        tint_rgb = self.hsl_to_rgb(hue, 0.45, 0.85)

        # Uniforms for shader
        uniforms = {
            "blur_strength": float(self.blur_slider.get()),
            "opacity": float(self.opacity_slider.get()),
            "tint": tint_rgb,
        }

        # Compose the glass shader
        shader = effect.makeShaderWithChildren(
            uniforms,
            [None, bg_shader], # 'image' is unused
        )

        paint = skia.Paint(Shader=shader)
        canvas.save()
        canvas.clipRect(glass_rect, skia.ClipOp.kIntersect, doAntiAlias=True)
        canvas.drawRect(glass_rect, paint)
        canvas.restore()

        # Draw a border for the glass panel
        border_paint = skia.Paint(Style=skia.Paint.kStroke_Style,
                                  Color=skia.ColorSetARGB(180, 255, 255, 255), StrokeWidth=2)
        canvas.drawRect(glass_rect, border_paint)

        # Convert skia.Surface to PIL image for Tkinter
        img = self.surface.makeImageSnapshot()
        img_bytes = img.encodeToData().tobytes()
        pil_img = Image.open(io.BytesIO(img_bytes))
        self.tk_image = ImageTk.PhotoImage(pil_img)
        self.label.configure(image=self.tk_image)
        self.label.image = self.tk_image

    def on_change(self, event=None):
        self.draw_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = GlassMorphismApp(root)
    root.mainloop()