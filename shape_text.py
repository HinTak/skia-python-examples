#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2024 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#
#  Based on Google's own C++ example, chrome/m128:example/external_client/src/shape_text.cpp

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

    font_data = Data.MakeFromFileName(input)
    mgr = FontMgr()
    # mgr = FontMgr.New_Custom_Empty()
    face = mgr.makeFromData(font_data)

    if not face:
        print("input font %s was not parsable by Freetype" % (argv[1]))
        sys.exit(1)

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
    style.setFontSize(10.5)
    paraStyle = textlayout.ParagraphStyle()
    paraStyle.setTextStyle(style)
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
