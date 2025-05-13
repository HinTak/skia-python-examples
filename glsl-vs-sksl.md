GLSL (OpenGL Shading Language) and SKSL (Skia Shading Language) are both shading languages, but they are designed for different purposes and ecosystems.

1. GLSL (OpenGL Shading Language)
Purpose: GLSL is designed to write shaders for the OpenGL rendering pipeline, which is widely used in 3D graphics, gaming, and other GPU-accelerated rendering tasks.
Ecosystem: GLSL is tightly integrated with OpenGL and Vulkan graphics APIs.
Use Cases:
Vertex shaders: Transform 3D vertices into screen coordinates.
Fragment shaders: Define pixel colors and effects.
Geometry, tessellation, and compute shaders (in modern OpenGL versions).
Syntax: GLSL uses a C-like syntax and is compiled by the GPU driver at runtime.
Platform Support: GLSL is supported on platforms that implement OpenGL or Vulkan.
2. SKSL (Skia Shading Language)
Purpose: SKSL is designed for Skia, Google's 2D graphics rendering library. It is optimized for creating shaders in a 2D rendering context.
Ecosystem: SKSL is used in applications that rely on Skia for rendering, such as Flutter, Chrome, and Android.
Use Cases:
Creating custom shader effects for 2D graphics in Skia.
Used in high-performance 2D rendering pipelines like Flutter's ShaderMask widget.
Syntax: SKSL also uses a C-like syntax and is inspired by GLSL but is tailored for Skia's rendering model.
Platform Support: SKSL is used internally by Skia and is cross-platform because Skia itself is cross-platform.
Key Differences
Feature	GLSL	SKSL
Primary Use	3D graphics and GPU rendering pipelines (OpenGL/Vulkan).	2D graphics rendering (Skia library).
Target Environment	OpenGL and Vulkan APIs.	Skia rendering engine.
Shaders Supported	Vertex, Fragment, Geometry, Tessellation, Compute.	Fragment shaders (focused on 2D effects).
Platform	Platforms supporting OpenGL/Vulkan.	Platforms using Skia (Chrome, Flutter, Android).
Flexibility	Designed for complex 3D rendering pipelines.	Simplified and optimized for 2D rendering.
Integration	Requires OpenGL/Vulkan context.	Integrated into Skia's rendering pipeline.
Performance	Focused on 3D rendering performance.	Optimized for 2D graphics performance.
When to Use GLSL vs SKSL
Use GLSL if you are developing applications that use OpenGL or Vulkan for 3D rendering, such as games or complex 3D visualizations.
Use SKSL if you are working with the Skia library for 2D rendering, such as in Flutter or custom 2D graphics in apps like Chrome.
Here’s a guide on porting shaders from GLSL to SKSL, based on resources and examples:

Differences Between GLSL and SKSL
Target Environment:

GLSL shaders are written for the GPU pipeline and are designed to control specific stages such as vertex and fragment processing.
SKSL shaders are written for the Skia pipeline, which is used for 2D rendering (e.g., in Flutter, Chrome).
Shader Types:

GLSL supports multiple shader types (vertex, fragment, geometry, etc.).
SKSL focuses on fragment-like shaders for the Skia pipeline.
Syntax:

SKSL is designed to be similar to GLSL but includes features and restrictions tailored to Skia.
For example, SKSL does not support certain GLSL features like geometry shaders, as they are not relevant to Skia's pipeline.
Entry Point:

GLSL fragment shaders use void main() and may process gl_FragCoord.
SKSL shaders use vec4 main(vec2 inCoords) as the entry point, where inCoords represents the coordinates of the pixel being processed.
Color Handling:

In SKSL, output colors must be pre-multiplied by alpha.
Steps to Port GLSL to SKSL
Understand the GLSL Shader:

Identify the purpose of the GLSL shader (e.g., gradient, texture mapping, etc.).
Note the inputs and outputs, such as uniforms, varyings, and attributes.
Adjust the Entry Point:

Change void main() in GLSL to vec4 main(vec2 inCoords) in SKSL.
Replace GLSL-specific variables like gl_FragCoord with inCoords.
Handle Uniforms and Inputs:

GLSL uniforms need to be declared in SKSL as uniform variables.
For example, GLSL:
GLSL
￼
￼
uniform sampler2D texture;
Becomes SKSL:
GLSL
￼
￼
uniform shader texture;
Modify Color Outputs:

Ensure the output color is pre-multiplied by alpha in SKSL:
GLSL
￼
￼
vec4 color = texture2D(texture, uv);
return vec4(color.rgb * color.a, color.a);
Adapt Skia-Specific Features:

SKSL supports specific Skia features, such as SkRuntimeEffect, which allows custom shaders to be defined and used with Skia.
Example of GLSL to SKSL Conversion
GLSL Shader:
GLSL
￼
￼
uniform sampler2D texture;
varying vec2 uv;

void main() {
    vec4 color = texture2D(texture, uv);
    gl_FragColor = color;
}
SKSL Shader:
GLSL
￼
￼
uniform shader texture;

vec4 main(vec2 inCoords) {
    vec4 color = sample(texture, inCoords);
    return vec4(color.rgb * color.a, color.a);
}
SKSL Example in Skia
Here’s an example of using SKSL with Skia's SkRuntimeEffect:
#include "include/effects/SkRuntimeEffect.h"
#include "include/core/SkCanvas.h"
#include "include/core/SkPaint.h"

void draw(SkCanvas* canvas) {
    const char* skslCode = R"(
        uniform shader inputTexture;

        vec4 main(vec2 inCoords) {
            vec4 color = sample(inputTexture, inCoords);
            return vec4(color.rgb * color.a, color.a);
        }
    )";

    auto [effect, error] = SkRuntimeEffect::MakeForShader(SkString(skslCode));
    if (!effect) {
        SkDebugf("Error: %s\n", error.c_str());
        return;
    }

    sk_sp<SkShader> shader = effect->makeShader(/*uniforms=*/nullptr, /*children=*/{});
    SkPaint paint;
    paint.setShader(shader);

    canvas->drawPaint(paint);
}
Resources for SKSL
Skia documentation on SkSL: Overview and syntax.
shaders.skia.org: Experiment with SKSL online.
Example Skia codebases in the Skia repository.
If you have specific GLSL shaders you'd like to port or need help with a particular feature, feel free to share them!
https://github.com/google/skia/blob/main/site/docs/user/sksl.md
https://shaders.skia.org/
https://github.com/google/skia
