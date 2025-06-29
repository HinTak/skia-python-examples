import skia
import os
import time
import random
from tkinter import Tk, Canvas, Button, filedialog, messagebox

class ShaderViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Skia Shader Viewer")
        self.canvas = Canvas(root, width=800, height=600, bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.load_button = Button(root, text="Load Shader", command=self.load_shader)
        self.load_button.pack(side="left")

        self.random_button = Button(root, text="Random Shader", command=self.random_shader)
        self.random_button.pack(side="left")

        self.export_button = Button(root, text="Export Image", command=self.export_image)
        self.export_button.pack(side="left")

        self.shader_effect = None
        self.shader_builder = None
        self.paint = skia.Paint()
        self.frame_count = 0
        self.start_time = time.time()
        self.shaders_path = self.get_shader_path()
        self.current_shader_code = None

        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.root.bind("<KeyPress>", self.on_key_press)

        self.load_shaders()
        self.run_shader()

    def get_shader_path(self):
        if os.path.exists("shaders"):
            return os.path.abspath("shaders")
        else:
            return os.path.abspath("../../shaders")

    def load_shaders(self):
        if not os.path.exists(self.shaders_path):
            messagebox.showerror("Error", "Shaders directory not found!")
            self.shaders = []
        else:
            self.shaders = [f for f in os.listdir(self.shaders_path) if f.endswith(".sksl")]
        if self.shaders:
            self.current_shader_code = self.load_shader_file(self.shaders[0])

    def load_shader_file(self, filename):
        with open(os.path.join(self.shaders_path, filename), "r") as f:
            return f.read()

    def load_shader(self):
        file_path = filedialog.askopenfilename(filetypes=[("Shader Files", "*.sksl")])
        if file_path:
            with open(file_path, "r") as f:
                self.current_shader_code = f.read()
            self.run_shader()

    def random_shader(self):
        if self.shaders:
            shader_file = random.choice(self.shaders)
            self.current_shader_code = self.load_shader_file(shader_file)
            self.run_shader()

    def run_shader(self):
        if not self.current_shader_code:
            return
        try:
            self.shader_effect = skia.RuntimeEffect.MakeForShader(self.current_shader_code)
            self.shader_builder = skia.RuntimeShaderBuilder(self.shader_effect)
            self.paint.setShader(self.shader_builder.makeShader())
            self.canvas.delete("all")
            self.draw()
        except Exception as e:
            messagebox.showerror("Shader Error", str(e))

    def draw(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if self.shader_effect and self.shader_builder:
            if "iResolution" in self.shader_effect.uniforms():
                self.shader_builder.uniform("iResolution", (width, height))
            if "iTime" in self.shader_effect.uniforms():
                self.shader_builder.uniform("iTime", time.time() - self.start_time)
            surface = skia.Surface(width, height)
            canvas = surface.getCanvas()
            canvas.drawPaint(self.paint)
            img = surface.makeImageSnapshot()
            data = img.encodeToData()
            self.photo_image = data.toTkImage()
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
        self.canvas.after(16, self.draw)

    def export_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG Files", "*.png")])
        if file_path:
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            surface = skia.Surface(width, height)
            canvas = surface.getCanvas()
            canvas.drawPaint(self.paint)
            img = surface.makeImageSnapshot()
            img.save(file_path)

    def on_resize(self, event):
        self.frame_count = 0

    def on_mouse_move(self, event):
        if self.shader_builder and "iMouse" in self.shader_effect.uniforms():
            self.shader_builder.uniform("iMouse", (event.x, event.y, 0, 1))

    def on_key_press(self, event):
        if event.char == "r":
            self.random_shader()
        elif event.char == "e":
            self.export_image()

if __name__ == "__main__":
    root = Tk()
    app = ShaderViewer(root)
    root.mainloop()