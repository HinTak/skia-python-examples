# Requires at least skia-python m138.

from skia import *
from math import sin

W = 800
H = 400
surface = Surface(W, H)
#canvas = surface.getCanvas();
#canvas.clear(ColorWHITE);

myPath = Path()
myPath.moveTo(60, 200)
x = 60
while (x <= 740):
    y = 200 + 60 * sin(2 * 3.14159 * (x-60) / 350)
    myPath.lineTo(x, y)
    x += 10

pathPaint = Paint()
pathPaint.setAntiAlias(True)
pathPaint.setStyle(Paint.kStroke_Style)
pathPaint.setColor(ColorBLUE)
pathPaint.setStrokeWidth(2)
font = Font(Typeface(""), 72)

with surface as canvas:
    canvas.clear(ColorWHITE)
    canvas.drawPath(myPath, pathPaint)


    paint = Paint()
    paint.setAntiAlias(True)
    paint.setColor(ColorRED)

    m = Matrix.I()

    canvas.drawTextOnPath("Morphing Text On Path!", myPath, m, font, paint)

    canvas.flush()

surface.flushAndSubmit()
img = surface.makeImageSnapshot()
img.save("morphed_text.png")
