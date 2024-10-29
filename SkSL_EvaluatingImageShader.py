#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#

# Based on chrome/m131:docs/examples/SkSL_EvaluatingImageShader.cpp
#     - We check effect being non-NULL here, unlike the c++ example.

from skia import RuntimeEffect, Paint, ColorGRAY, \
    Image, SamplingOptions, FilterMode, RuntimeEffectChildPtr, SpanRuntimeEffectChildPtr

image = Image.open("resources/images/example_5.png")

def draw(canvas):
    imageShader = image.makeShader(SamplingOptions(FilterMode.kLinear))

    sksl = \
    "uniform shader image;" + \
    "half4 main(float2 coord) {" + \
    "  return image.eval(coord).bgra;" + \
    "}"
   
    autoResult = RuntimeEffect.MakeForShader(sksl)

    if (autoResult.effect is None):
        raise RuntimeError(autoResult.errorText)

    children = RuntimeEffectChildPtr(imageShader)
    myShader = autoResult.effect.makeShader(None, SpanRuntimeEffectChildPtr(children, 1))

    canvas.drawColor(ColorGRAY)
    
    p = Paint()
    p.setShader(myShader)
    canvas.drawPaint(p)

if __name__ == '__main__':
    import os, sys
    from skia import Surface, kPNG
    surface = Surface(128, 128)
    with surface as canvas:
        draw(canvas)
    surface.flushAndSubmit()
    image = surface.makeImageSnapshot()
    image.save(os.path.splitext(os.path.basename(sys.argv[0]))[0].split('_')[-1] + '.png', kPNG)
