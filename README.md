[![CI](https://github.com/HinTak/skia-python-examples/actions/workflows/ci.yml/badge.svg)](https://github.com/HinTak/skia-python-examples/actions/workflows/ci.yml)

[![linux testing](https://github.com/HinTak/skia-python-examples/actions/workflows/linux.yml/badge.svg)](https://github.com/HinTak/skia-python-examples/actions/workflows/linux.yml)

[![windows testing](https://github.com/HinTak/skia-python-examples/actions/workflows/windows.yml/badge.svg)](https://github.com/HinTak/skia-python-examples/actions/workflows/windows.yml)

On Wayland-based platforms (i.e. very new Linux systems), setting `SDL_VIDEODRIVER=x11`
may be needed for the SDL example; the equivalent for the GLUT example is `PYOPENGL_PLATFORM=glx` (not needed on Fedora 40 Wayland).

The `skparagraph-example` example generates the below as an example of multilingual paragraph layout.
Note on Linux, it is highly sensitive to locale, and you might need to unset `LANG` and `FC_LANG` if you have unusual
(non-English) settings.

![test-en](https://github.com/user-attachments/assets/9ff6dff5-a684-46e9-9a30-cd91455845cb)

`SkSL_ShaderMulti+SDL2.py` is a port of the animation on https://shaders.skia.org/ . Run it with a number argument (0 to 6) for the 7 examples on https://shaders.skia.org/ .

## SkSL examples

original:

![original](resources/images/example_5.png)

`SkSL_CoordinateSpaces.py`:

![CoordinateSpaces](SkSL_example_outputs/CoordinateSpaces.png)

`SkSL_EvaluatingImageShader.py` (swap red and blue):

![EvaluatingImageShader](SkSL_example_outputs/EvaluatingImageShader.png)

`SkSL_EvaluatingTwoShaders.py` (Image with Gradient):

![EvaluatingTwoShaders](SkSL_example_outputs/EvaluatingTwoShaders.png)

`SkSL_EvaluatingNestedShaders.py` (Image with same Gradient as shader too):

![EvaluatingNestedShaders](SkSL_example_outputs/EvaluatingNestedShaders.png)

`SkSL_MinifiedSkSL.py`: (this is not a separate SkSL example, but how to generate Minified SkSL with Skia's `minifier` tool
for the same result as `SkSL_PremultipliedAlpha.py` below):

![MinifiedSkSL](SkSL_example_outputs/MinifiedSkSL.png)

`SkSL_PremultipliedAlpha.py`:

![PremultipliedAlpha](SkSL_example_outputs/PremultipliedAlpha.png)

`SkSL_LinearSRGB.py`:

![LinearSRGB](SkSL_example_outputs/LinearSRGB.png)

`SkSL_Uniforms.py`:

![Uniforms](SkSL_example_outputs/Uniforms.png)

`SkSL_RawImageShaders.py`:

![RawImageShaders](SkSL_example_outputs/RawImageShaders.png)
