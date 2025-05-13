import glfw

def mouse_button_callback(window, button, action, mods):
    if action == glfw.PRESS:
        print(f"Mouse Button {button} Pressed")
    elif action == glfw.RELEASE:
        print(f"Mouse Button {button} Released")

def cursor_position_callback(window, xpos, ypos):
    print(f"Mouse Moved to {xpos}, {ypos}")

if __name__ == "__main__":
    if not glfw.init():
        raise Exception("GLFW cannot be initialized!")
    
    window = glfw.create_window(800, 600, "pyGLFW Mouse Event Example", None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window cannot be created!")
    
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    
    glfw.make_context_current(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
    
    glfw.terminate()
