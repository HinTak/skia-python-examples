import contextlib
import sdl3
import skia
from OpenGL import GL
import ctypes

WIDTH, HEIGHT = 640, 480
WINDOW_TITLE = b"Skia + PySDL3 Example" # SDL requires bytes for titles

@contextlib.contextmanager
def sdl_video_init():
    """Initialize and quit SDL video subsystem."""
    print("Initializing SDL Video...")
    if sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO) < 0:
        raise RuntimeError(f"SDL_Init Error: {sdl3.SDL_GetError()}")
    try:
        yield
    finally:
        print("Quitting SDL...")
        sdl3.SDL_Quit()

@contextlib.contextmanager
def sdl_gl_window(title, width, height):
    """Create and destroy an SDL window with an OpenGL context."""
    print("Setting SDL GL Attributes...")
    # Request OpenGL 3.3 Core Profile
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_MINOR_VERSION, 3)
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_CONTEXT_PROFILE_MASK, sdl3.SDL_GL_CONTEXT_PROFILE_CORE)
    # Enable double buffering
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_DOUBLEBUFFER, 1)
    # Set depth/stencil buffer sizes (stencil is important for Skia)
    # Using 0 as Skia doesn't store depth info. If you're doign 3D rendering alongside Skia, then set it to 24 (or an appropriate value).
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_DEPTH_SIZE, 0)
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_STENCIL_SIZE, 8) # Skia needs stencil bits

    print(f"Creating SDL Window ({width}x{height})...")
    window = sdl3.SDL_CreateWindow(
        title,
        width, height,
        sdl3.SDL_WINDOW_OPENGL # Flag to indicate OpenGL usage
    )
    if not window:
        raise RuntimeError(f"SDL_CreateWindow Error: {sdl3.SDL_GetError()}")

    print("Creating SDL GL Context...")
    gl_context = sdl3.SDL_GL_CreateContext(window)
    if not gl_context:
        sdl3.SDL_DestroyWindow(window)
        raise RuntimeError(f"SDL_GL_CreateContext Error: {sdl3.SDL_GetError()}")

    print("Making GL Context Current...")
    if sdl3.SDL_GL_MakeCurrent(window, gl_context) < 0:
         sdl3.SDL_GL_DestroyContext(gl_context)
         sdl3.SDL_DestroyWindow(window)
         raise RuntimeError(f"SDL_GL_MakeCurrent Error: {sdl3.SDL_GetError()}")

    # Optional: Enable VSync
    # if sdl3.SDL_GL_SetSwapInterval(1) < 0:
    #    print(f"Warning: Unable to set VSync! SDL Error: {sdl3.SDL_GetError()}")

    try:
        yield window # Pass the window object to the 'with' block
    finally:
        print("Cleaning up SDL GL Context and Window...")
        if gl_context:
            sdl3.SDL_GL_DestroyContext(gl_context)
        if window:
            sdl3.SDL_DestroyWindow(window)


@contextlib.contextmanager
def skia_surface_sdl(window):
    """Create a Skia Surface linked to the SDL window's GL context."""
    print("Creating Skia GL Context...")
    context = skia.GrDirectContext.MakeGL()
    if not context:
        raise RuntimeError("Failed to create Skia GrDirectContext")

    # Get the actual framebuffer size in pixels (handles HiDPI)
    fb_width, fb_height = ctypes.c_int(), ctypes.c_int()
    sdl3.SDL_GetWindowSizeInPixels(window, ctypes.byref(fb_width), ctypes.byref(fb_height))
    print(f"Drawable size: {fb_width.value}x{fb_height.value}")

    # Check how many stencil bits we actually got
    stencil_bits = ctypes.c_int()
    sdl3.SDL_GL_GetAttribute(sdl3.SDL_GL_STENCIL_SIZE,  ctypes.byref(stencil_bits))
    print(f"Requested Stencil Bits: 8, Got: {stencil_bits.value}") # Should be 8

    backend_render_target = skia.GrBackendRenderTarget(
        fb_width.value,
        fb_height.value,
        0,  # sampleCnt (MSAA samples) | samples - usually 0 for direct to screen
        stencil_bits.value, # stencilBits - Use value retrieved from GL context
        # Framebuffer ID 0 means the default window framebuffer
        skia.GrGLFramebufferInfo(0, GL.GL_RGBA8) # Target format GL_RGBA8 | Use 0 for framebuffer object ID for default framebuffer
    )

    # Make sure Skia renders bottom-up to match OpenGL's usual coordinate system
    surface = skia.Surface.MakeFromBackendRenderTarget(
        context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())

    if surface is None:
        context.abandonContext()
        raise RuntimeError("Failed to create Skia Surface from BackendRenderTarget")

    print("Skia Surface created successfully.")
    try:
        yield surface
    finally:
        print("Abandoning Skia Context...")
        # See https://groups.google.com/g/skia-discuss/c/3VkpXIcbKlM/m/t3chqtUmCAAJ
        # Proper cleanup involves deleting the surface first (implicitly done by exiting 'with')
        # then abandoning or deleting the GrDirectContext. abandonContext is safer if unsure.
        context.abandonContext()


# --- Main Execution ---
def main():
    try:
        with sdl_video_init():
            with sdl_gl_window(WINDOW_TITLE, WIDTH, HEIGHT) as window:
                # Note: Skia surface context manager yields a surface that
                # itself acts as a context manager for the canvas.
                # The canvas is the object you draw *onto*.
                # The `surface` context manager manages the Skia context.
                with skia_surface_sdl(window) as surface:

                    running = True
                    event = sdl3.SDL_Event() # Create event structure once

                    while running:
                        # --- Event Handling Loop ---
                        while sdl3.SDL_PollEvent(event):
                            if event.type == sdl3.SDL_EVENT_QUIT:
                                print("Quit event received.")
                                running = False
                                break
                            # Add other event handling here (keyboard, mouse, resize etc.)
                            # if event.type == sdl3.SDL_EVENT_KEY_DOWN:
                            #     if event.key.key == sdl3.SDLK_ESCAPE:
                            #          running = False
                            #          break
                            # Handle window resize if needed (more complex: requires recreating surface)

                        if not running:
                            break

                        # --- Drawing ---
                        # These OpenGL calls are outside Skia's drawing
                        # It's good practice to clear the OpenGL buffer before Skia draws
                        GL.glClearColor(0.0, 0.0, 0.0, 1.0) # Black background
                        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)

                        # Get a Skia canvas to draw on
                        # 
                        # Alternate syntax would be:
                        # ```
                        # canvas = surface.getCanvas()
                        # ```
                        #
                        with surface as canvas:
                            # Example drawing: Clear with Skia color, draw circle
                            canvas.clear(skia.ColorWHITE)
                            paint = skia.Paint(
                                Color=skia.ColorBLUE,
                                StrokeWidth=2,
                                Style=skia.Paint.kStroke_Style, # Make it an outline
                                AntiAlias=True
                            )
                            canvas.drawCircle(WIDTH / 2, HEIGHT / 2, 100, paint)

                            paint.setColor(skia.ColorGREEN)
                            paint.setStyle(skia.Paint.kFill_Style) # Fill style
                            canvas.drawRect(skia.Rect.MakeXYWH(20, 20, 80, 80), paint)


                        # --- Finalize Frame ---
                        # Skia drawing is complete, flush it to the GL context | Ensure all Skia commands are sent to the GPU
                        surface.flushAndSubmit()

                        # Swap the front and back buffers to display the rendered frame
                        sdl3.SDL_GL_SwapWindow(window)

                    print("Exiting main loop.")

    except RuntimeError as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Application finished.")

if __name__ == '__main__':
    main()