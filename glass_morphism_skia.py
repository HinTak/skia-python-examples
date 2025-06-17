import skia
import numpy as np

# Glassmorphism SkSL: blur + color overlay + border
sksl = """
uniform shader input_src;
uniform float2 offset;
uniform float2 size;
uniform float blur_radius;
uniform float4 glass_color;
uniform float glass_alpha;
uniform float border_thickness;
uniform float4 border_color;

half4 main(float2 p) {
    float2 norm = (p - offset) / size;
    float2 center = float2(0.5, 0.5);
    float dist = distance(norm, center);

    // Blur by sampling nearby pixels
    half4 c = half4(0);
    float count = 0.0;
    for (float x = -blur_radius; x <= blur_radius; x += 1.0) {
        for (float y = -blur_radius; y <= blur_radius; y += 1.0) {
            c += input_src.eval(p + float2(x, y));
            count += 1.0;
        }
    }
    c /= count;

    // Glass overlay
    half4 glass = mix(c, glass_color, glass_alpha);

    // Border effect
    float border = smoothstep(border_thickness, border_thickness + 1.0, min(norm.x, min(norm.y, min(1.0 - norm.x, 1.0 - norm.y))));
    glass.rgb = mix(glass.rgb, border_color.rgb, border * border_color.a);

    return glass;
}
"""

# Create an example background (gradient)
w, h = 600, 400
surface = skia.Surface(w, h)
canvas = surface.getCanvas()
gradient = skia.GradientShader.MakeLinear(
    [(0, 0), (w, h)],
    [skia.ColorBLUE, skia.ColorYELLOW, skia.ColorRED],
    [0, 0.5, 1],
    skia.TileMode.kClamp,
)
canvas.drawPaint(skia.Paint(Shader=gradient))

# Compile the runtime effect
effect = skia.RuntimeEffect.MakeForShader(sksl)

# Rectangle position and size
rect = skia.Rect.MakeXYWH(150, 100, 300, 200)

# Prepare uniforms
uniforms = {
    "offset": (rect.left(), rect.top()),
    "size": (rect.width(), rect.height()),
    "blur_radius": 8.0,
    "glass_color": (1.0, 1.0, 1.0, 0.25),  # white, alpha 0.25
    "glass_alpha": 0.5,
    "border_thickness": 0.03,
    "border_color": (1.0, 1.0, 1.0, 0.5),
}

# Input shader is the background
input_shader = surface.makeImageSnapshot().makeShader()

# Build the shader with uniforms and children
shader = effect.makeShaderWithChildren(
    uniforms,
    [input_shader],
    None
)

# Draw the glass rectangle
paint = skia.Paint(Shader=shader)
canvas.drawRect(rect, paint)

# Save result
image = surface.makeImageSnapshot()
image.save("glass_morphism_example.png", skia.kPNG)
print("Saved glass_morphism_example.png")