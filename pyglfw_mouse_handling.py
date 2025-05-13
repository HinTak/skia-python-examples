import glfw

def cursor_position_callback(window, xpos, ypos):
    print(f"Mouse moved: ({xpos}, {ypos})")

def mouse_button_callback(window, button, action, mods):
    if action == glfw.PRESS:
        print(f"Mouse button pressed: {button}")

def scroll_callback(window, xoffset, yoffset):
    print(f"Mouse wheel scrolled: {yoffset}")

def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "pyGLFW Mouse Handling", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Set mouse callbacks
    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    while not glfw.window_should_close(window):
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
