from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import pyqtSlot
import sys

class MyOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot()
    def cleanupGL(self):
        # This will be called just before the GL context is destroyed
        print("OpenGL context is about to be destroyed. Clean up GPU resources here.")

    def closeEvent(self, event):
        print("Widget is about to be destroyed")
        super().closeEvent(event)

    def initializeGL(self):
        print("initializeGL: OpenGL context created.")
        # Connect the aboutToBeDestroyed signal to your cleanup slot
        self.context().aboutToBeDestroyed.connect(self.cleanupGL)

    def resizeGL(self, w, h):
        print(f"resizeGL: {w}x{h}")

    def paintGL(self):
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(MyOpenGLWidget(self))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()