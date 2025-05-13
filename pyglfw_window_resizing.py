import glfw

def framebuffer_size_callback(window, width, height):
    print(f"Window resized to: {width}x{height}")
    # You may also want to update the viewport here
    # glViewport(0, 0, width, height) if using OpenGL

def main():
    if not glfw.init():
        return

    # Create a resizable window
    glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
    window = glfw.create_window(800, 600, "pyGLFW Window Resizing", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Set the framebuffer size callback
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    while not glfw.window_should_close(window):
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
