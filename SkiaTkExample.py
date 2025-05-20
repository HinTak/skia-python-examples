import tkinter as tk
from skia import *
import math
import random

HELP_MESSAGE = "Click and drag to create rects.  Press esc to quit."

class ApplicationState:
    def __init__(self, width, height):
        self.fQuit = False
        self.window_width = width
        self.window_height = height
        self.fRects = []
        self.drag_rect = None
        self.rotation = 0
        self.animating = False

def create_star():
    kNumPoints = 5
    path = Path()
    angle = 2 * math.pi / kNumPoints
    points = []
    for i in range(kNumPoints):
        theta = i * angle - math.pi / 2
        x = math.cos(theta) * 50
        y = math.sin(theta) * 50
        points.append((x, y))
    path.moveTo(*points[0])
    for i in range(kNumPoints):
        idx = (2 * i) % kNumPoints
        path.lineTo(*points[idx])
    path.setFillType(PathFillType.kEvenOdd)
    path.close()
    return path

class SkiaTkApp:
    def __init__(self, root):
        self.root = root
        self.state = ApplicationState(800, 600)
        self.canvas = tk.Canvas(root, width=self.state.window_width, height=self.state.window_height,
                                highlightthickness=0, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        # Skia raster surface
        self.surface = Surface(self.state.window_width, self.state.window_height)
        self.skcanvas = self.surface.getCanvas()
        self.star_image = self.make_star_image()
        self.font = Font()
        # events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("<Escape>", self.quit)
        self.root.bind("<Configure>", self.on_resize)
        self.root.bind('<FocusIn>', self.on_focus_in)
        self.root.bind('<FocusOut>', self.on_focus_out)
        self.tk_image = None
        self.animation_id = None
        self.is_focused = True
        self.draw()

    def make_star_image(self):
        img_surface = Surface(100, 100)
        c = img_surface.getCanvas()
        c.clear(ColorTRANSPARENT)
        c.save()
        c.translate(50, 50)
        paint = Paint(AntiAlias=True)
        c.drawPath(create_star(), paint)
        c.restore()
        return img_surface.makeImageSnapshot()

    def on_mouse_down(self, event):
        self.state.drag_rect = Rect.MakeLTRB(event.x, event.y, event.x, event.y)
        self.state.fRects.append(self.state.drag_rect)
        self.draw()

    def on_mouse_drag(self, event):
        if self.state.drag_rect:
            self.state.drag_rect.fRight = event.x
            self.state.drag_rect.fBottom = event.y
            self.draw()

    def on_mouse_up(self, event):
        self.state.drag_rect = None
        self.draw()

    def quit(self, event=None):
        self.state.fQuit = True
        self.stop_animation()
        self.root.destroy()

    def on_resize(self, event):
        # Only handle actual size changes
        if event.width != self.state.window_width or event.height != self.state.window_height:
            self.state.window_width = event.width
            self.state.window_height = event.height
            self.surface = Surface(self.state.window_width, self.state.window_height)
            self.skcanvas = self.surface.getCanvas()
            self.draw()

    def on_focus_in(self, event):
        self.is_focused = True
        self.start_animation()

    def on_focus_out(self, event):
        self.is_focused = False
        self.stop_animation()

    def start_animation(self):
        if self.animation_id is None and self.is_focused:
            self.animation_id = self.root.after(16, self.animate)
            self.state.animating = True

    def stop_animation(self):
        if self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self.state.animating = False

    def animate(self):
        if not self.state.fQuit and self.is_focused:
            self.state.rotation = (self.state.rotation + 1) % 360
            self.draw()
            self.animation_id = self.root.after(16, self.animate)
        else:
            self.stop_animation()

    def draw(self):
        # Clear
        self.skcanvas.clear(ColorWHITE)
        # Draw help message near top left
        paint = Paint(AntiAlias=True)
        paint.setColor(ColorBLACK)
        font = self.font
        self.skcanvas.drawString(HELP_MESSAGE, 10, font.getSize() + 10, font, paint)
        # Draw rectangles
        random.seed(0)
        for rect in self.state.fRects:
            color = random.randint(0, 0xFFFFFFFF) | 0x44808080
            paint.setColor(color)
            self.skcanvas.drawRect(rect, paint)
        # Draw rotating star in center
        self.skcanvas.save()
        cx = self.state.window_width / 2
        cy = self.state.window_height / 2
        self.skcanvas.translate(cx, cy)
        self.skcanvas.rotate(self.state.rotation)
        self.skcanvas.drawImage(self.star_image, -50, -50)
        self.skcanvas.restore()
        # Update tkinter canvas with Skia output
        self.update_tk_canvas()

    def update_tk_canvas(self):
        img = self.surface.makeImageSnapshot()
        png_bytes = img.encodeToData()
        import base64
        # Avoid creating a new PhotoImage unless necessary
        b64data = base64.b64encode(png_bytes.bytes())
        if not self.tk_image or getattr(self.tk_image, '_last_data', None) != b64data:
            self.tk_image = tk.PhotoImage(data=b64data)
            self.tk_image._last_data = b64data
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

def main():
    import sys
    root = tk.Tk()
    root.title("Skia + Tkinter Example")
    app = SkiaTkApp(root)
    app.start_animation()
    root.mainloop()

if __name__ == '__main__':
    main()