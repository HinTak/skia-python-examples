#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#
#  Based on Google's own C++ example, chrome/m128:example/external_client/src/shape_text.cpp

#  Notes:
#
#  - The first argument is processed by "FontMgr.OneFontMgr(input)",
#    a font manager which knows only one specific font.
#    You can achieve a similar effect with the platform font manager
#    ("FontMgr()") by a combination of
#    "TextStyle.setFontFamilies()" and "TextStyle.setFontStyle()".
#
#    For example, on Linux,
#    /usr/share/fonts/liberation-serif/LiberationSerif-Regular.ttf as argv[1]
#    is equivalent to 'style.setFontFamilies(["Liberation Serif"])' with "mgr = FontMgr()",
#    while /usr/share/fonts/liberation-serif/LiberationSerif-Bold.ttf as argv[1]
#    is equivalent to 'style.setFontFamilies(["Liberation Serif"])' plus
#    'style.setFontStyle(FontStyle.Bold())', with "mgr = FontMgr()", commented out below.
#
#    The C++ example creates a custom font manager "OneFontMgr" with argv[1]
#    which knows about exact one font file. We moved that c++ snipplet into skia-python m129+.
#
#    The two approaches have different strengths: The OnefontMgr is useful for
#    pixel-perfect agreement across platforms, especially for embedded (mobile/secure)
#    systems without platform fonts. The platform font manager offers a wider typeface and
#    style choices.
#
#  - This python example offers style.setDecoration* for setting underline/overline/strikthrough
#    decoration styles. This was not in the c++ example.
#
#  - There is a small upstream bug in the c++ example, about the
#    output file type/extension being inconsistent:
#    https://issues.skia.org/358798723 - we are not copying the bug.
#    I prefer png.

from skia import *

if __name__ == '__main__':
    from sys import argv
    if len(argv) < 3:
        print("Usage: %s <font.ttf> <name.png>" % (argv[0]))
        exit(1)

    input = argv[1]

    if not input:
        printf("Cannot open input file %s" % (argv[1]))
        exit(1)

    story = '''The landing port at Titan had not changed much in five years.
The ship settled down on the scarred blast shield, beside the same trio of squat square buildings, and quickly disgorged its scanty quota of cargo and a lone passenger into the flexible tube that linked the loading hatch with the main building.
As soon as the tube was disconnected, the ship screamed off through the murky atmosphere, seemingly glad to get away from Titan and head back to the more comfortable and settled parts of the Solar System.
'''

    # mgr = FontMgr()
    mgr = FontMgr.OneFontMgr(input)
    fontCollection = textlayout.FontCollection()
    fontCollection.setDefaultFontManager(mgr)

    width = 200
    surface = Surfaces.Raster(ImageInfo.MakeN32(width, 200, AlphaType.kOpaque_AlphaType))
    canvas = surface.getCanvas()
    canvas.clear(ColorWHITE)

    paint = Paint()
    paint.setAntiAlias(True)
    paint.setColor(ColorBLACK)

    style = textlayout.TextStyle()
    style.setForegroundColor(paint)
    style.setFontFamilies(["san-serif"])
    # style.setFontFamilies(["Liberation Serif"])
    # style.setFontStyle(FontStyle.Bold())
    style.setDecoration(textlayout.TextDecoration.kUnderline)
    # style.setDecoration(textlayout.TextDecoration.kOverline)
    # style.setDecoration(textlayout.TextDecoration.kLineThrough)
    # style.setDecorationStyle(textlayout.TextDecorationStyle.kDouble)
    style.setDecorationStyle(textlayout.TextDecorationStyle.kWavy)
    style.setDecorationThicknessMultiplier(3)
    style.setDecorationColor(ColorRED)
    style.setFontSize(10.5)
    paraStyle = textlayout.ParagraphStyle()
    paraStyle.setTextStyle(style)
    # available alternatives to kRight are: kLeft, kRight, kCenter, kJustify, kStart, kEnd
    paraStyle.setTextAlign(textlayout.TextAlign.kRight)

    # "unicode" is reserved in Python
    _unicode = Unicodes.ICU.Make()

    if not _unicode:
        print("Could not load unicode data")
        sys.exit(1)

    builder = textlayout.ParagraphBuilder.make(paraStyle, fontCollection, _unicode)

    builder.addText(story)

    paragraph = builder.Build()

    paragraph.layout(width - 20)
    paragraph.paint(canvas, 10, 10)

    surface.flushAndSubmit()
    image = surface.makeImageSnapshot()
    # see https://issues.skia.org/358798723
    image.save(argv[2], kPNG)
