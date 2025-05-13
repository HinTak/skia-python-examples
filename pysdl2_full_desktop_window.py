import sdl2
import sdl2.ext

def main():
    sdl2.ext.init()

    # Create a full desktop window
    window = sdl2.ext.Window(
        "pySDL2 Full Desktop Window",
        size=(800, 600),
        flags=sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
    )
    window.show()

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False

    sdl2.ext.quit()

if __name__ == "__main__":
    main()
