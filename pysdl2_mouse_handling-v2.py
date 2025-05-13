import sdl2
import sdl2.ext

def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("PySDL2 Mouse Event Example", size=(800, 600))
    window.show()

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
            elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                print(f"Mouse Button Down at {event.button.x}, {event.button.y}")
            elif event.type == sdl2.SDL_MOUSEMOTION:
                print(f"Mouse Moved to {event.motion.x}, {event.motion.y}")
        window.refresh()

    sdl2.ext.quit()

if __name__ == "__main__":
    run()
