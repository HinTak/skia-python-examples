#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#

# Based on chrome/m131:docs/examples/SkSL_LinearSRGB.cpp
#     - We check effect being non-NULL here, unlike the c++ example.

from skia import RuntimeEffect, RuntimeShaderBuilder, Paint, Rect, V3

def draw(canvas):
    litEffect = RuntimeEffect.MakeForShader("""
    layout(color) uniform vec3 surfaceColor;
    uniform int doLinearLighting;

    vec3 normal_at(vec2 p) {
      p = (p / 128) * 2 - 1;
      float len2 = dot(p, p);
      vec3 n = (len2 > 1) ? vec3(0, 0, 1) : vec3(p, sqrt(1 - len2));
      return normalize(n);
    }

    vec4 main(vec2 p) {
      vec3 n = normal_at(p);
      vec3 l = normalize(vec3(-1, -1, 0.5));
      vec3 C = surfaceColor;

      if (doLinearLighting != 0) { C = toLinearSrgb(C); }
      C *= saturate(dot(n, l));
      if (doLinearLighting != 0) { C = fromLinearSrgb(C); }

      return C.rgb1;
      }
""")
    if (litEffect.effect is None):
        raise RuntimeError(litEffect.errorText)
    builder = RuntimeShaderBuilder(litEffect.effect)
    builder.setUniform("surfaceColor", V3(0.8, 0.8, 0.8))
    paint = Paint()
    
    builder.setUniform("doLinearLighting", 0)
    paint.setShader(builder.makeShader())
    canvas.drawRect(Rect(0,0,128,128), paint)

    builder.setUniform("doLinearLighting", 1)
    paint.setShader(builder.makeShader())
    canvas.translate(128, 0)
    canvas.drawRect(Rect(0,0,128,128), paint)

if __name__ == '__main__':
    from skia import Surface, kPNG
    surface = Surface(256, 128)
    with surface as canvas:
        draw(canvas)
    surface.flushAndSubmit()
    image = surface.makeImageSnapshot()
    image.save('./output.png', kPNG)
