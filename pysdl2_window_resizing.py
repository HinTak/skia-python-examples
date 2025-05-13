import sdl2
import sdl2.ext

def main():
    sdl2.ext.init()
    window = sdl2.ext.Window("pySDL2 Window Resizing", size=(800, 600), flags=sdl2.SDL_WINDOW_RESIZABLE)
    window.show()

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
            elif event.type == sdl2.SDL_WINDOWEVENT and event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                width, height = event.window.data1, event.window.data2
                print(f"Window resized to: {width}x{height}")

    sdl2.ext.quit()

if __name__ == "__main__":
    main()
