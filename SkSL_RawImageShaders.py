#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#

# Based on chrome/m131:docs/examples/SkSL_RawImageShaders.cpp
#     - We check effect being non-NULL here, unlike the c++ example.

from skia import RuntimeEffect, RuntimeShaderBuilder, Paint, Rect, ColorSpace, cms, ImageInfo, kRGBA_F16_ColorType, kPremul_AlphaType, Surfaces, BlendMode, SamplingOptions

def make_image(effect, info):
    surface = Surfaces.Raster(info)
    canvas = surface.getCanvas()
    shader = effect.makeShader(None)
    if (shader is None):
        return None
    paint = Paint()
    paint.setShader(shader)
    paint.setBlendMode(BlendMode.kSrc);
    canvas.drawPaint(paint)
    return surface.makeImageSnapshot()

def draw(canvas):
    imageInfo = ImageInfo.MakeN32Premul(128, 128)
    imageShader = RuntimeEffect.MakeForShader("""
    vec4 main(vec2 p) {
      p = (p / 128) * 2 - 1;
      float len2 = dot(p, p);
      vec3 v = (len2 > 1) ? vec3(0, 0, 1) : vec3(p, sqrt(1 - len2));
      return (v * 0.5 + 0.5).xyz1;
    }""").effect
    normalImage = make_image(imageShader, imageInfo)

    litEffect = RuntimeEffect.MakeForShader("""
    uniform shader normals;
    vec4 main(vec2 p) {
      vec3 n = normalize(normals.eval(p).xyz * 2 - 1);
      vec3 l = normalize(vec3(-1, -1, 0.5));
      return saturate(dot(n, l)).xxx1;
    }""").effect
    builder = RuntimeShaderBuilder(litEffect)
    
    paint = Paint()

    builder.setChild("normals", normalImage.makeShader(SamplingOptions()))
    paint.setShader(builder.makeShader())
    canvas.drawRect(Rect(0,0,128,128), paint)

    rec2020 = ColorSpace.MakeRGB(cms.NamedTransferFn.kSRGB, cms.NamedGamut.kRec2020)
    info = ImageInfo.Make(128, 128, kRGBA_F16_ColorType, kPremul_AlphaType, rec2020)
    surface = Surfaces.Raster(info)

    surface.getCanvas().drawPaint(paint)
    canvas.drawImage(surface.makeImageSnapshot(), 128, 0)

    builder.setChild("normals", normalImage.makeRawShader(SamplingOptions()))
    paint.setShader(builder.makeShader())
    surface.getCanvas().drawPaint(paint)
    canvas.drawImage(surface.makeImageSnapshot(), 256, 0)
    
if __name__ == '__main__':
    import os, sys
    from skia import Surface, kPNG
    surface = Surface(384, 128)
    with surface as canvas:
        draw(canvas)
    surface.flushAndSubmit()
    image = surface.makeImageSnapshot()
    image.save(os.path.splitext(os.path.basename(sys.argv[0]))[0].split('_')[-1] + '.png', kPNG)
