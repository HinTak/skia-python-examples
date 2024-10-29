#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#

# Based on chrome/m131:docs/examples/SkSL_Uniforms.cpp
#     - We check effect being non-NULL here, unlike the c++ example.

from skia import RuntimeEffect, RuntimeShaderBuilder, Paint, Rect, V4, ColorSpace, cms, ImageInfo, kRGBA_F16_ColorType, kPremul_AlphaType, Surfaces

def draw(canvas):
    rec2020 = ColorSpace.MakeRGB(cms.NamedTransferFn.kLinear, cms.NamedGamut.kRec2020)
    info = ImageInfo.Make(128, 64, kRGBA_F16_ColorType, kPremul_AlphaType, rec2020)
    surface = Surfaces.Raster(info)
    sksl = """
                  uniform vec4 not_a_color;
    layout(color) uniform vec4 color;

    vec4 main(vec2 xy) {
      vec4 c = xy.y < 32 ? not_a_color : color;
      return (c * (xy.x / 128)).rgb1;
    }"""
    
    autoResult = RuntimeEffect.MakeForShader(sksl)
    if (autoResult.effect is None):
        raise RuntimeError(autoResult.errorText)

    builder = RuntimeShaderBuilder(autoResult.effect)
    builder.setUniform("not_a_color", V4( 1, 0, 0, 1 ))
    builder.setUniform("color"      , V4( 1, 0, 0, 1 ))

    paint = Paint()

    paint.setShader(builder.makeShader())
    surface.getCanvas().drawPaint(paint)

    canvas.drawImage(surface.makeImageSnapshot(), 0, 0)

if __name__ == '__main__':
    from skia import Surface, kPNG
    surface = Surface(128, 64)
    with surface as canvas:
        draw(canvas)
    surface.flushAndSubmit()
    image = surface.makeImageSnapshot()
    image.save('./output.png', kPNG)
