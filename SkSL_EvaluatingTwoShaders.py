#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#

# Based on chrome/m131:docs/examples/SkSL_EvaluatingTwoShaders.cpp
#     - We check effect being non-NULL here, unlike the c++ example.

from skia import RuntimeEffect, Paint, ColorGRAY, \
    Image, SamplingOptions, FilterMode, RuntimeEffectChildPtr, SpanRuntimeEffectChildPtr

from skia import Point, ColorWHITE, ColorBLACK, \
    GradientShader, TileMode, VectorSkRuntimeEffectChildPtr

def makeGradientShader():
    pts = [Point( 0, 0 ), Point( 128, 0 )]
    colors = [ ColorWHITE, ColorBLACK ]
    return GradientShader.MakeLinear(pts, colors, None, TileMode.kClamp)

image = Image.open("resources/images/example_5.png")

def draw(canvas):
    sksl = \
    "uniform shader input_1;" + \
    "uniform shader input_2;" + \
    "half4 main(float2 coord) {" + \
    "  return input_1.eval(coord) * input_2.eval(coord);" + \
    "}"

    imageShader = image.makeShader(SamplingOptions(FilterMode.kLinear))

    children = VectorSkRuntimeEffectChildPtr([RuntimeEffectChildPtr(imageShader), RuntimeEffectChildPtr(makeGradientShader())])

    autoResult = RuntimeEffect.MakeForShader(sksl)

    if (autoResult.effect is None):
        raise RuntimeError(autoResult.errorText)

    myShader = autoResult.effect.makeShader(None, children)

    canvas.drawColor(ColorGRAY)
    
    p = Paint()
    p.setShader(myShader)
    canvas.drawPaint(p)

if __name__ == '__main__':
    from skia import Surface, kPNG
    surface = Surface(128, 128)
    with surface as canvas:
        draw(canvas)
    surface.flushAndSubmit()
    image = surface.makeImageSnapshot()
    image.save('./output.png', kPNG)
