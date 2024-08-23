#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#
#  Based on MeetWq's rust-skia example, https://gist.github.com/MeetWq/c56635fbf886c2c511c2ac1ec8e0aa48
#  (See https://github.com/kyamagu/skia-python/pull/258#issuecomment-2304137435)

#  Note:
#      On Linux, this code depends on fontconfig, and is highly sensitive to LANG and FC_LANG.
#      You may want to set LANG to "en_GB.UTF-8" or "en_US.UTF-8", and FC_LANG to "en",
#      if you have a non-English locale, particularly a zh_* one.

from skia import Surfaces, ImageInfo, AlphaType
from skia import textlayout
from skia import ColorBLACK, ColorWHITE, FontMgr, FontStyle, Paint, Unicodes, kPNG

from math import ceil

if __name__ == '__main__':
    font_collection = textlayout.FontCollection()
    font_collection.setDefaultFontManager(FontMgr())

    para_style = textlayout.ParagraphStyle()
    # SK_DISABLE_LEGACY_PARAGRAPH_UNICODE: two-arg ParagraphBuilder constructor used by rust going soon!
    builder = textlayout.ParagraphBuilder.make(para_style, font_collection, Unicodes.ICU.Make())

    paint = Paint()
    paint.setAntiAlias(True);
    paint.setColor(ColorBLACK)

    style = textlayout.TextStyle()
    style.setFontSize(30.0)
    style.setForegroundPaint(paint)
    style.setFontFamilies(["times", "georgia", "serif"])
    builder.pushStyle(style)

    style_bold = style.cloneForPlaceholder()
    style_bold.setFontStyle(FontStyle.Bold())
    builder.pushStyle(style_bold)
    builder.addText("Typography")
    builder.pop()

    builder.addText(" is the ");

    style_italic = style.cloneForPlaceholder()
    style_italic.setFontStyle(FontStyle.Italic())
    builder.pushStyle(style_italic)
    builder.addText("art and technique")
    builder.pop()

    builder.addText(" of arranging type to make written language ")

    style_underline = style.cloneForPlaceholder()
    style_underline.setDecoration(textlayout.TextDecoration.kUnderline)
    style_underline.setDecorationMode(textlayout.TextDecorationMode.kGaps) # Rust seems to default to kGaps, while kThrough is the upstream default.
    style_underline.setDecorationColor(ColorBLACK)
    style_underline.setDecorationThicknessMultiplier(1.5)
    builder.pushStyle(style_underline)
    builder.addText("legible, readable, and appealing")
    builder.pop()

    builder.addText(" when displayed. The arrangement of type involves selecting typefaces, point sizes, line lengths, line-spacing (leading), and letter-spacing (tracking), and adjusting the space between pairs of letters (kerning). The term typography is also applied to the style, arrangement, and appearance of the letters, numbers, and symbols created by the process.")

    builder.addText(" Furthermore, العربية نص جميل. द क्विक ब्राउन फ़ॉक्स jumps over the lazy 🐕.")

    paragraph = builder.Build()
    paragraph.layout(1000.0)

    width = paragraph.LongestLine
    height = paragraph.Height
    surface = Surfaces.Raster(ImageInfo.MakeN32(ceil(width), ceil(height), AlphaType.kOpaque_AlphaType))

    canvas = surface.getCanvas()
    canvas.clear(ColorWHITE)
    paragraph.paint(canvas, 0, 0) # What does rust's Point() do?

    surface.flushAndSubmit()
    image = surface.makeImageSnapshot()
    image.save("test.png", kPNG)
