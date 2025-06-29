#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPen, QBrush, QFont, QPainterPath
from PySide6.QtCore import Qt, QRectF, QPointF

class GlassmorphicWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(510, 370)
        self.setWindowTitle("PySide6 Glassmorphic Demo")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor("#03080D"))

        # Draw blurred colored circles (approximate the shader-based effect)
        # Circle 1 - Purple to Pink gradient
        grad1 = QLinearGradient(QPointF(450, 60), QPointF(290, 190))
        grad1.setColorAt(0, QColor(0x7A, 0x26, 0xD9))
        grad1.setColorAt(1, QColor(0xE4, 0x44, 0xE1))
        painter.setBrush(QBrush(grad1))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(375, 125), 100, 100)

        # Circle 2 - Solid Pink
        painter.setBrush(QColor(0xEA, 0x35, 0x7C))
        painter.drawEllipse(QPointF(100, 265), 55, 55)

        # Circle 3 - Orange-Red gradient
        grad2 = QLinearGradient(QPointF(180, 125), QPointF(230, 125))
        grad2.setColorAt(0, QColor(0xEA, 0x33, 0x4C))
        grad2.setColorAt(1, QColor(0xEC, 0x60, 0x51))
        painter.setBrush(QBrush(grad2))
        painter.drawEllipse(QPointF(205, 125), 25, 25)

        # Glass rectangle border (mock glassmorphism with gradient stroke and alpha)
        border_grad = QLinearGradient(QPointF(120, 110), QPointF(405, 290))
        border_grad.setColorAt(0, QColor(255, 255, 255, 128))
        border_grad.setColorAt(0.33, QColor(255, 255, 255, 0))
        border_grad.setColorAt(0.66, QColor(0, 255, 72, 0))
        border_grad.setColorAt(1, QColor(0, 255, 72, 128))
        pen = QPen(QBrush(border_grad), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        rect = QRectF(86, 111, 318, 178)
        painter.drawRoundedRect(rect, 20, 20)

        # Text on paths
        font = QFont("Arial", 14, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 128))

        def draw_text_path(text, y, size):
            path = QPainterPath()
            path.moveTo(100, y)
            path.lineTo(400, y)
            font.setPointSize(size)
            painter.setFont(font)
            painter.drawText(QPointF(102, y+size/2), text)

        draw_text_path("MEMBERSHIP", 140, 14)
        draw_text_path("JAMES APPLESEED", 240, 18)
        draw_text_path("PUSHING-PIXELS", 265, 13)

        # Optionally: add a glass blur effect (requires OpenGL/GLSL or Qt6's graphics effect)
        # For a real glassmorphic effect, use a QGraphicsBlurEffect on a QGraphicsView,
        # or use moderngl/vispy for a custom shader as in the original Kotlin.

        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = QMainWindow()
    widget = GlassmorphicWidget()
    win.setCentralWidget(widget)
    win.setWindowTitle("Glassmorphic Card UI - Python/PySide6")
    win.show()
    sys.exit(app.exec())