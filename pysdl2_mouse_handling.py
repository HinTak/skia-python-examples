import sdl2
import sdl2.ext

def main():
    sdl2.ext.init()
    window = sdl2.ext.Window("pySDL2 Mouse Handling", size=(800, 600))
    window.show()

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
            elif event.type == sdl2.SDL_MOUSEMOTION:
                print(f"Mouse moved: ({event.motion.x}, {event.motion.y})")
            elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                print(f"Mouse button pressed: {event.button.button}")
            elif event.type == sdl2.SDL_MOUSEWHEEL:
                print(f"Mouse wheel scrolled: {event.wheel.y}")

    sdl2.ext.quit()

if __name__ == "__main__":
    main()
