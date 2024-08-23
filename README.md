[![CI](https://github.com/HinTak/skia-python-examples/actions/workflows/ci.yml/badge.svg)](https://github.com/HinTak/skia-python-examples/actions/workflows/ci.yml)

On Wayland-based platforms (i.e. very new Linux systems), setting `SDL_VIDEODRIVER=x11`
may be needed for the SDL example; the equivalent for the GLUT example is `PYOPENGL_PLATFORM=glx`.

The `skparagraph-example` example generates the below as an example of multilingual paragraph layout.
Note on Linux, it is highly sensitive to locale, and you might need to unset `LANG` and `FC_LANG` if you have unusual
(non-English) settings.

![test-en](https://github.com/user-attachments/assets/9ff6dff5-a684-46e9-9a30-cd91455845cb)
