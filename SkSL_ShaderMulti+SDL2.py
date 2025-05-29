#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2025, Hin-Tak Leung

# SDL2 + SkSL

# Multiple examples from https://shaders.skia.org/
# Requires at least skia-python v138

from sdl2 import *
import skia
from skia import Paint, Rect, Font, Typeface, ColorWHITE
from OpenGL import GL
import ctypes
import time

width, height = 512, 512
title = b"Skia + PySDL2 + SkSL Example"

# The first snipplet can be found twice within skia as:
#     skia:gm/runtimefunctions.cpp
#     skia:resources/sksl/realistic/BlueNeurons.rts
# It is not clear where the other examples are stored at the moment.
# They are merely cut-and-paste from https://shaders.skia.org/ .
SkSL_code = [ """
// Source: @notargs https://twitter.com/notargs/status/1250468645030858753
float f(vec3 p) {
    p.z -= iTime * 10.;
    float a = p.z * .1;
    p.xy *= mat2(cos(a), sin(a), -sin(a), cos(a));
    return .1 - length(cos(p.xy) + sin(p.yz));
}

half4 main(vec2 fragcoord) { 
    vec3 d = .5 - fragcoord.xy1 / iResolution.y;
    vec3 p=vec3(0);
    for (int i = 0; i < 32; i++) {
      p += f(p) * d;
    }
    return ((sin(p) + vec3(2, 5, 9)) / length(p)).xyz1;
}
""",
"""
// Source: @zozuar https://twitter.com/zozuar/status/1482754721450446850
mat2 rotate2D(float r){
    return mat2(cos(r), sin(r), -sin(r), cos(r));
}

mat3 rotate3D(float angle, vec3 axis){
    vec3 a = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float r = 1.0 - c;
    return mat3(
        a.x * a.x * r + c,
        a.y * a.x * r + a.z * s,
        a.z * a.x * r - a.y * s,
        a.x * a.y * r - a.z * s,
        a.y * a.y * r + c,
        a.z * a.y * r + a.x * s,
        a.x * a.z * r + a.y * s,
        a.y * a.z * r - a.x * s,
        a.z * a.z * r + c
    );
}

half4 main(float2 FC) {
  vec4 o = vec4(0);
  vec2 r = iResolution.xy;
  vec3 v = vec3(1,3,7), p = vec3(0);
  float t=iTime, n=0, e=0, g=0, k=t*.2;
  for (float i=0; i<100; ++i) {
    p = vec3((FC.xy-r*.5)/r.y*g,g)*rotate3D(k,cos(k+v));
    p.z += t;
    p = asin(sin(p)) - 3.;
    n = 0;
    for (float j=0; j<9.; ++j) {
      p.xz *= rotate2D(g/8.);
      p = abs(p);
      p = p.x<p.y ? n++, p.zxy : p.zyx;
      p += p-v;
    }
    g += e = max(p.x,p.z) / 1e3 - .01;
    o.rgb += .1/exp(cos(v*g*.1+n)+3.+1e4*e);
  }
  return o.xyz1;
}
""",
"""
const float cloudscale = 1.1;
const float speed = 0.03;
const float clouddark = 0.5;
const float cloudlight = 0.3;
const float cloudcover = 0.2;
const float cloudalpha = 8.0;
const float skytint = 0.5;
const vec3 skycolour1 = vec3(0.2, 0.4, 0.6);
const vec3 skycolour2 = vec3(0.4, 0.7, 1.0);

const mat2 m = mat2( 1.6,  1.2, -1.2,  1.6 );

vec2 hash( vec2 p ) {
	p = vec2(dot(p,vec2(127.1,311.7)), dot(p,vec2(269.5,183.3)));
	return -1.0 + 2.0*fract(sin(p)*43758.5453123);
}

float noise( in vec2 p ) {
    const float K1 = 0.366025404; // (sqrt(3)-1)/2;
    const float K2 = 0.211324865; // (3-sqrt(3))/6;
	vec2 i = floor(p + (p.x+p.y)*K1);	
    vec2 a = p - i + (i.x+i.y)*K2;
    vec2 o = (a.x>a.y) ? vec2(1.0,0.0) : vec2(0.0,1.0); //vec2 of = 0.5 + 0.5*vec2(sign(a.x-a.y), sign(a.y-a.x));
    vec2 b = a - o + K2;
	vec2 c = a - 1.0 + 2.0*K2;
    vec3 h = max(0.5-vec3(dot(a,a), dot(b,b), dot(c,c) ), 0.0 );
	vec3 n = h*h*h*h*vec3( dot(a,hash(i+0.0)), dot(b,hash(i+o)), dot(c,hash(i+1.0)));
    return dot(n, vec3(70.0));	
}

float fbm(vec2 n) {
	float total = 0.0, amplitude = 0.1;
	for (int i = 0; i < 7; i++) {
		total += noise(n) * amplitude;
		n = m * n;
		amplitude *= 0.4;
	}
	return total;
}

// -----------------------------------------------

half4 main(in vec2 fragCoord ) {
    vec2 p = fragCoord.xy / iResolution.xy;
	vec2 uv = p*vec2(iResolution.x/iResolution.y,1.0);    
    float time = iTime * speed;
    float q = fbm(uv * cloudscale * 0.5);
    
    //ridged noise shape
	float r = 0.0;
	uv *= cloudscale;
    uv -= q - time;
    float weight = 0.8;
    for (int i=0; i<8; i++){
		r += abs(weight*noise( uv ));
        uv = m*uv + time;
		weight *= 0.7;
    }
    
    //noise shape
	float f = 0.0;
    uv = p*vec2(iResolution.x/iResolution.y,1.0);
	uv *= cloudscale;
    uv -= q - time;
    weight = 0.7;
    for (int i=0; i<8; i++){
		f += weight*noise( uv );
        uv = m*uv + time;
		weight *= 0.6;
    }
    
    f *= r + f;
    
    //noise colour
    float c = 0.0;
    time = iTime * speed * 2.0;
    uv = p*vec2(iResolution.x/iResolution.y,1.0);
	uv *= cloudscale*2.0;
    uv -= q - time;
    weight = 0.4;
    for (int i=0; i<7; i++){
		c += weight*noise( uv );
        uv = m*uv + time;
		weight *= 0.6;
    }
    
    //noise ridge colour
    float c1 = 0.0;
    time = iTime * speed * 3.0;
    uv = p*vec2(iResolution.x/iResolution.y,1.0);
	uv *= cloudscale*3.0;
    uv -= q - time;
    weight = 0.4;
    for (int i=0; i<7; i++){
		c1 += abs(weight*noise( uv ));
        uv = m*uv + time;
		weight *= 0.6;
    }
	
    c += c1;
    
    vec3 skycolour = mix(skycolour2, skycolour1, p.y);
    vec3 cloudcolour = vec3(1.1, 1.1, 0.9) * clamp((clouddark + cloudlight*c), 0.0, 1.0);
   
    f = cloudcover + cloudalpha*f*r;
    
    vec3 result = mix(skycolour, clamp(skytint * skycolour + cloudcolour, 0.0, 1.0), clamp(f + c, 0.0, 1.0));
    
	return vec4( result, 1.0 );
}
""",
"""
// Source: @XorDev https://twitter.com/XorDev/status/1475524322785640455
vec4 main(vec2 FC) {
  vec4 o = vec4(0);
  vec2 p = vec2(0), c=p, u=FC.xy*2.-iResolution.xy;
  float a;
  for (float i=0; i<4e2; i++) {
    a = i/2e2-1.;
    p = cos(i*2.4+iTime+vec2(0,11))*sqrt(1.-a*a);
    c = u/iResolution.y+vec2(p.x,a)/(p.y+2.);
    o += (cos(i+vec4(0,2,4,0))+1.)/dot(c,c)*(1.-p.y)/3e4;
  }
  return o;
}
""",
"""
float julia(vec2 uv, vec2 c) {
    const float maxSteps = 400;
    for (float i = 0; i < maxSteps; i++) {
        uv = vec2(uv.x * uv.x - uv.y * uv.y + c.x,
                  2.0 * uv.x * uv.y + c.y);
        if (length(uv) > 2) {
            return i / maxSteps;
        }
    }
    return 1.0;
}


vec4 main( in vec2 fragCoord )
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = -1.0 + 2.0 * fragCoord / iResolution.xy;

    float aspect = iResolution.x / iResolution.y;
    uv.x *= aspect;

    uv *= pow(0.5, -1.0 + 15.0 * (0.5 + 0.5 * sin(iTime * 0.80 - (3.14159265))));
    uv += vec2(-0.51, -0.61351); // an interesting coordinate to zoom in on 
    float f = julia(vec2(0.0, 0.0), uv);
    
    // Output to screen
    return vec4((1.0 - uv) * pow(f, 0.5), f, 1.0);
}
""",
"""
// Source: @zozuar https://twitter.com/zozuar/status/1492217553103503363

vec3 hsv(float h, float s, float v){
    vec4 t = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(vec3(h) + t.xyz) * 6.0 - vec3(t.w));
    return v * mix(vec3(t.x), clamp(p - vec3(t.x), 0.0, 1.0), s);
}

vec4 main(vec2 FC) {
  float e=0,R=0,t=iTime,s;
  vec2 r = iResolution.xy;
  vec3 q=vec3(0,0,-1), p, d=vec3((FC.xy-.5*r)/r.y,.7);
  vec4 o=vec4(0);
  for(float i=0;i<100;++i) {
    o.rgb+=hsv(.1,e*.4,e/1e2)+.005;
    p=q+=d*max(e,.02)*R*.3;
    float py = (p.x == 0 && p.y == 0) ? 1 : p.y;
    p=vec3(log(R=length(p))-t,e=asin(-p.z/R)-1.,atan(p.x,py)+t/3.);
    s=1;
    for(int z=1; z<=9; ++z) {
      e+=cos(dot(sin(p*s),cos(p.zxy*s)))/s;
      s+=s;
    }
    i>50.?d/=-d:d;
  }
  return o;
}
"""]

current_index = 0
builder = None

def setBuilder():
    global current_index, builder
    input = current_index % len(SkSL_code)
    from skia import RuntimeEffect, RuntimeShaderBuilder
    header = """
uniform float iTime;
float3 iResolution = float3(512, 512, 512);
"""
    litEffect = RuntimeEffect.MakeForShader(header + SkSL_code[input])
    builder = RuntimeShaderBuilder(litEffect)

def draw(canvas, timenow):
    global builder
    builder.setUniform("iTime", timenow)
    paint = Paint()
    paint.setShader(builder.makeShader())
    canvas.drawRect(Rect(0,0,512,512), paint)

def main():
    global current_index, builder
    if SDL_Init(SDL_INIT_VIDEO) != 0:
        raise RuntimeError(f"SDL_Init Error: {SDL_GetError()}")

    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)

    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 0)
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8)

    window = SDL_CreateWindow(
        title,
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        width, height,
        SDL_WINDOW_OPENGL
    )
    if not window:
        raise RuntimeError(f"SDL_CreateWindow Error: {SDL_GetError()}")

    gl_context = SDL_GL_CreateContext(window)
    if not gl_context:
        SDL_DestroyWindow(window)
        raise RuntimeError(f"SDL_GL_CreateContext Error: {SDL_GetError()}")

    if SDL_GL_MakeCurrent(window, gl_context) !=0:
         SDL_GL_DeleteContext(gl_context)
         SDL_DestroyWindow(window)
         raise RuntimeError(f"SDL_GL_MakeCurrent Error: {SDL_GetError()}")

    context = skia.GrDirectContext.MakeGL()
    if not context:
        raise RuntimeError("Failed to create Skia GrDirectContext")

    fb_width, fb_height = ctypes.c_int(), ctypes.c_int()
    SDL_GetWindowSizeInPixels(window, ctypes.byref(fb_width), ctypes.byref(fb_height))

    # Check how many stencil bits we actually got
    stencil_bits = ctypes.c_int()
    SDL_GL_GetAttribute(SDL_GL_STENCIL_SIZE,  ctypes.byref(stencil_bits))
    assert stencil_bits.value == 8

    backend_render_target = skia.GrBackendRenderTarget(
        fb_width.value,
        fb_height.value,
        0,  # sampleCnt (MSAA samples) | samples - usually 0 for direct to screen
        stencil_bits.value, # stencilBits - Use value retrieved from GL context
        # Framebuffer ID 0 means the default window framebuffer
        skia.GrGLFramebufferInfo(0, GL.GL_RGBA8) # Target format GL_RGBA8 | Use 0 for framebuffer object ID for default framebuffer
    )

    surface = skia.Surface.MakeFromBackendRenderTarget(
        context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())

    if surface is None:
        context.abandonContext()
        raise RuntimeError("Failed to create Skia Surface from BackendRenderTarget")

    running = True
    event = SDL_Event() # Create event structure once
    step = 0
    font = Font(Typeface("Roman"))
    paintWHITE = Paint()
    paintWHITE.setColor(ColorWHITE)
    initial_time = time.time()

    while running:
        while SDL_PollEvent(event):
            if event.type == SDL_QUIT:
                print("Quit event received.")
                running = False
                break
            if event.type == SDL_MOUSEBUTTONDOWN:
                if event.button.state == SDL_PRESSED:
                    # Don't care where you clicked, just that you did!
                    current_index += 1
                    setBuilder()

        if not running:
            break
        
        GL.glClearColor(0.0, 0.0, 0.0, 1.0) # Black background
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
        
        with surface as canvas:
            draw(canvas, time.time() - initial_time)
            canvas.drawString("Click to cycle through the examples", 0, font.getSize(), font, paintWHITE)
        step += 10 # arbitrary to look dynamic
        surface.flushAndSubmit()
        
        SDL_GL_SwapWindow(window)

    context.abandonContext()

    if gl_context:
        SDL_GL_DeleteContext(gl_context)
    if window:
        SDL_DestroyWindow(window)
            
    SDL_Quit()

if __name__ == '__main__':
    setBuilder()
    main()
