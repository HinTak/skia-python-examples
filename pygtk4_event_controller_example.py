import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GObject

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="PyGTK4 Event Controller Example")
        self.set_default_size(300, 100)

        button = Gtk.Button(label="Click Me")
        self.set_child(button)

        # Create a GestureClick controller and connect to the "pressed" signal
        gesture = Gtk.GestureClick.new()
        gesture.connect("pressed", self.on_button_pressed)
        button.add_controller(gesture)

    def on_button_pressed(self, gesture, n_press, x, y):
        print("Button was pressed! (with event controller)")

class MyApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.PyGTK4EventController")

    def do_activate(self):
        win = MainWindow(self)
        win.present()

if __name__ == "__main__":
    app = MyApp()
    app.run()