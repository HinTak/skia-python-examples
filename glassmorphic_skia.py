import skia
import numpy as np
from PIL import Image
import math

# ---- SkSL shader code from your original Kotlin/Compose ----
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

# ---- Helper: PIL noise image to Skia image ----
def pil_noise_to_skimage(size):
    arr = (np.random.rand(size, size, 3) * 255).astype(np.uint8)
    img = Image.fromarray(arr, 'RGB')
    return skia.Image.fromarray(np.array(img))

def create_glass_card(canvas, surface_size):
    W, H = surface_size
    # --- Draw the colored background shapes ---
    # Gradient circle 1
    grad1 = skia.GradientShader.MakeLinear(
        points=[skia.Point(450, 60), skia.Point(290, 190)],
        colors=[skia.ColorSetRGB(0x7A, 0x26, 0xD9), skia.ColorSetRGB(0xE4, 0x44, 0xE1)],
    )
    paint = skia.Paint(Shader=grad1)
    canvas.drawCircle(375, 125, 100, paint)

    # Circle 2
    paint = skia.Paint(Color=skia.ColorSetRGB(0xEA, 0x35, 0x7C))
    canvas.drawCircle(100, 265, 55, paint)

    # Gradient circle 3
    grad2 = skia.GradientShader.MakeLinear(
        points=[skia.Point(180, 125), skia.Point(230, 125)],
        colors=[skia.ColorSetRGB(0xEA, 0x33, 0x4C), skia.ColorSetRGB(0xEC, 0x60, 0x51)],
    )
    paint = skia.Paint(Shader=grad2)
    canvas.drawCircle(205, 125, 25, paint)

def main():
    W, H = 510, 370

    # --- Create background (content) image ---
    surface = skia.Surface(W, H)
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorSetRGB(3, 8, 13))  # dark bg
    create_glass_card(canvas, (W, H))
    content_image = surface.makeImageSnapshot()

    # --- Blur image for shader ---
    blurred_image = content_image.makeWithFilter(
        skia.ImageFilters.Blur(20.0, 20.0, skia.TileMode.kDecal), None)[0]

    # --- Noise image for shader ---
    noise_image = pil_noise_to_skimage(max(W, H))

    # --- Setup SkSL runtime effect ---
    effect = skia.RuntimeEffect.MakeForShader(GLASSMORPHIC_SKSL)[0]

    # --- Build RuntimeShader ---
    rect = skia.Rect.MakeLTRB(85, 110, 405, 290)
    uniforms = {
        "rectangle": [rect.left(), rect.top(), rect.right(), rect.bottom()],
        "radius": 20.0,
        "dropShadowSize": 15.0,
    }
    children = {
        "content": content_image.makeShader(skia.TileMode.kClamp, skia.TileMode.kClamp),
        "blur": blurred_image.makeShader(skia.TileMode.kClamp, skia.TileMode.kClamp),
        "noise": noise_image.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat),
    }
    glass_shader = effect.makeShaderWithChildren(uniforms, children)

    # --- Compose the final image ---
    final_surface = skia.Surface(W, H)
    final_canvas = final_surface.getCanvas()
    final_canvas.clear(skia.ColorSetRGB(3, 8, 13))
    # Draw the glass effect
    paint = skia.Paint(Shader=glass_shader)
    final_canvas.drawRect(skia.Rect.MakeWH(W, H), paint)

    # Draw the glass border
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

    # Draw the text
    def draw_text(text, y, size):
        font = skia.Font(skia.Typeface('Arial', skia.FontStyle.Bold()), size)
        text_paint = skia.Paint(AntiAlias=True, Color=skia.ColorSetARGB(128, 255, 255, 255))
        final_canvas.drawString(text, 102, y, font, text_paint)

    draw_text("MEMBERSHIP", 150, 14)
    draw_text("JAMES APPLESEED", 250, 18)
    draw_text("PUSHING-PIXELS", 275, 13)

    # --- Save or show the result ---
    img = final_surface.makeImageSnapshot()
    img.save('glassmorphic_card_skia.png', skia.kPNG)
    print("Glassmorphic card saved as glassmorphic_card_skia.png")

if __name__ == "__main__":
    main()