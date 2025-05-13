import glfw

def main():
    if not glfw.init():
        return

    # Get the primary monitor
    primary_monitor = glfw.get_primary_monitor()
    video_mode = glfw.get_video_mode(primary_monitor)

    # Create a full desktop window
    window = glfw.create_window(
        video_mode.size.width,
        video_mode.size.height,
        "pyGLFW Full Desktop Window",
        primary_monitor,
        None
    )

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
