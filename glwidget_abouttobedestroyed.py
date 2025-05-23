from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtCore import pyqtSlot
import sys

class MyOpenGLWidget(QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Connect the aboutToBeDestroyed signal to your cleanup slot
        self.aboutToBeDestroyed.connect(self.cleanupGL)

    @pyqtSlot()
    def cleanupGL(self):
        # This will be called just before the GL context is destroyed
        print("OpenGL context is about to be destroyed. Clean up GPU resources here.")

    def initializeGL(self):
        print("initializeGL: OpenGL context created.")

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