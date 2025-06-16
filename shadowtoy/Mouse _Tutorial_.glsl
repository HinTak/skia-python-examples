uniform vec3      iResolution;           // viewport resolution (in pixels)
uniform float     iTime;                 // shader playback time (in seconds)
uniform float     iTimeDelta;            // render time (in seconds)
uniform float     iFrameRate;            // shader frame rate
uniform int       iFrame;                // shader playback frame
uniform float     iChannelTime[4];       // channel playback time (in seconds)
uniform vec3      iChannelResolution[4]; // channel resolution (in pixels)
uniform vec4      iMouse;                // mouse pixel coords. xy: current (if MLB down), zw: click
uniform samplerXX iChannel0..3;          // input channel. XX = 2D/Cube
uniform vec4      iDate;                 // (year, month, day, time in seconds)
uniform float     iSampleRate;           // sound sample rate (i.e., 44100)

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec3 col = vec3(0.);

    //Draw a red cross where the mouse button was last down.
    if(abs(iMouse.x-fragCoord.x) < 4.) {
        col = vec3(1.,0.,0.);
    }
    if(abs(iMouse.y-fragCoord.y) < 4.) {
        col = vec3(1.,0.,0.);
    }
    
    //If the button is currently up, (iMouse.z, iMouse.w) is where the mouse
    //was when the button last went down.
    if(abs(iMouse.z-fragCoord.x) < 2.) {
        col = vec3(0.,0.,1.);
    }
    if(abs(iMouse.w-fragCoord.y) < 2.) {
        col = vec3(0.,0.,1.);
    }
    
    //If the button is currently down, (-iMouse.z, -iMouse.w) is where
    //the button was when the click occurred.
    if(abs(-iMouse.z-fragCoord.x) < 2.) {
        col = vec3(0.,1.,0.);
    }
    if(abs(-iMouse.w-fragCoord.y) < 2.) {
        col = vec3(0.,1.,0.);
    }
    
    fragColor = vec4(col, 1.0);
}
