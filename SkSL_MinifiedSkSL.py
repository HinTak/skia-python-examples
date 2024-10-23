#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#

# Based on chrome/m131:docs/examples/SkSL_MinifiedSkSL.cpp
#     - We check effect being non-NULL here, unlike the c++ example.

from skia import RuntimeEffect, Paint, ColorGRAY

SKSL_MINIFIED_GradientShader = \
"half4 main(float2 a){float b=1.-a.y*.006666667;if(a.x<100.)return half4(float4" + \
"(0.,.5,.75,1.)*b);else return half4(half3(0.,.5,.75),half(b));}"

def draw(canvas):
    autoResult = RuntimeEffect.MakeForShader(SKSL_MINIFIED_GradientShader)

    if (autoResult.effect is None):
        raise RuntimeError(autoResult.errorText)

    myShader = autoResult.effect.makeShader(None)

    canvas.drawColor(ColorGRAY)

    p = Paint()
    p.setShader(myShader)
    canvas.drawPaint(p)

if __name__ == '__main__':
    from skia import Surface, kPNG
    surface = Surface(200, 200)
    with surface as canvas:
        draw(canvas)
    surface.flushAndSubmit()
    image = surface.makeImageSnapshot()
    image.save('./output.png', kPNG)
