52|         # Setup event controllers for GTK4
53|         self.motion_controller = Gtk.EventControllerMotion.new(self)
54|         self.motion_controller.connect("motion", self.on_motion_notify)
55| 
56|         self.click_gesture = Gtk.GestureClick.new(self)
57|         self.click_gesture.connect("pressed", self.on_button_press)
58|         self.click_gesture.connect("released", self.on_button_release)
59| 
60|         self.key_controller = Gtk.EventControllerKey.new(self)
61|         self.key_controller.connect("key-pressed", self.on_key_press)