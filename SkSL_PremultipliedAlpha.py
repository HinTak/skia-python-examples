#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#

# Based on chrome/m131:docs/examples/SkSL_PremultipliedAlpha.cpp
#     - We check effect being non-NULL here, unlike the c++ example.

from skia import RuntimeEffect, Paint, ColorGRAY

sksl = \
  "const half3 iColor = half3(0, 0.5, 0.75);"                 + \
  "half4 main(float2 coord) {"                                + \
  "  float alpha = 1 - (coord.y / 150);"                      + \
  "  if (coord.x < 100) {"                                    + \
  "    /* Correctly premultiplied version of color */"        + \
  "    return iColor.rgb1 * alpha;"                           + \
  "  } else {"                                                + \
  "    /* Returning an unpremultiplied color (just setting alpha) leads to over-bright colors. */" + \
  "    return half4(iColor, alpha);"                          + \
  "  }"                                                       + \
  "}"

def draw(canvas):
    autoResult = RuntimeEffect.MakeForShader(sksl)

    if (autoResult.effect is None):
        raise RuntimeError(autoResult.errorText)

    myShader = autoResult.effect.makeShader(None)

    canvas.drawColor(ColorGRAY)

    p = Paint()
    p.setShader(myShader)
    canvas.drawPaint(p)

if __name__ == '__main__':
    import os, sys
    from skia import Surface, kPNG
    surface = Surface(200, 200)
    with surface as canvas:
        draw(canvas)
    surface.flushAndSubmit()
    image = surface.makeImageSnapshot()
    image.save(os.path.splitext(os.path.basename(sys.argv[0]))[0].split('_')[-1] + '.png', kPNG)
