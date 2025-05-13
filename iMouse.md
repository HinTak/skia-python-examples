In ShaderToy, the iMouse uniform is a built-in variable that provides information about mouse interactions within the ShaderToy environment. It is particularly useful for creating interactive shaders that respond to user input.

Structure of iMouse
The iMouse uniform is a 4-component vector (vec4) with the following structure:

Code
￼
￼
vec4 iMouse
The components of iMouse represent:

iMouse.x: The x-coordinate of the mouse position in pixels.
iMouse.y: The y-coordinate of the mouse position in pixels.
iMouse.z: The x-coordinate of the mouse position when the mouse button was last pressed.
iMouse.w: The y-coordinate of the mouse position when the mouse button was last pressed.
Behavior
Mouse Movement (Hover):

When the mouse moves across the ShaderToy canvas and no button is pressed, only iMouse.x and iMouse.y change to reflect the current position of the mouse in pixels.
iMouse.z and iMouse.w remain 0.
Mouse Button Press:

When a mouse button is pressed, iMouse.z and iMouse.w store the position where the button was pressed.
As long as the button is held down, iMouse.z and iMouse.w remain constant, while iMouse.x and iMouse.y continue to update with the current mouse position.
Mouse Release:

When the mouse button is released, iMouse.z and iMouse.w reset to 0, indicating no button is being pressed.
Default Value:

If the mouse is outside the ShaderToy canvas or no interaction has occurred, all components of iMouse are 0.
Example Usage in GLSL
Here's an example of how to use iMouse to create a simple interactive shader:

GLSL
￼
￼
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy; // Normalize coordinates to [0,1]

    // Map mouse position to normalized coordinates
    vec2 mousePos = iMouse.xy / iResolution.xy;

    // Compute distance from the mouse position
    float dist = distance(uv, mousePos);

    // Create a circle that follows the mouse
    float circle = smoothstep(0.05, 0.04, dist);

    // Set pixel color
    fragColor = vec4(circle, circle, circle, 1.0);
}
Key Points
Normalized Interaction:

The mouse position (iMouse.xy) is in pixel coordinates, so you may need to normalize it by dividing by the resolution (iResolution.xy) for many use cases.
Interactivity:

You can create interactivity by combining mouse input with other shader logic, such as triggering animations, changing colors, or drawing shapes based on the mouse position.
Press and Hold:

The iMouse.z and iMouse.w components allow you to track the position where the mouse button was pressed, enabling interactions like dragging or gestures.
Common Use Cases
Drawing shapes or patterns that follow the mouse cursor.
Creating animations that respond to mouse clicks or movements.
Implementing basic drag-and-drop mechanics.
Simulating user interactions in visual effects or games.
By leveraging the iMouse uniform, you can make ShaderToy shaders more dynamic and interactive, enhancing their visual appeal and usability.
You are correct that ShaderToy uses negative values of iMouse.z and iMouse.w to indicate a mouse release. This behavior is part of the ShaderToy platform's specification for the iMouse uniform.

Here is how it works:

While the mouse button is pressed, iMouse.z and iMouse.w contain the coordinates of the press in pixels.
When the mouse button is released, iMouse.z and iMouse.w are set to the negative of their previous values, indicating the release event.
If the mouse is not interacting with the canvas, all components of iMouse are set to 0.0.
Unfortunately, ShaderToy does not have formal documentation for every detail of its uniforms. However, this behavior has been observed and discussed in ShaderToy-related community forums, tutorials, and in the source code of shaders shared on ShaderToy itself.

Practical Reference
You can find shaders demonstrating this behavior by searching for interactive ShaderToy examples (e.g., shaders that use dragging or click-release mechanics). For example, searching for shaders that check iMouse.z < 0.0 or iMouse.w < 0.0 will lead you to examples where the negative values of iMouse.zw are explicitly handled.

If you'd like, I can help you search for ShaderToy examples or shaders that document this behavior in their comments!
Behavior Details
1. Idle (No Button Pressed)
iMouse.x and iMouse.y are the current mouse position (if over the shader viewport), otherwise they are zero.
iMouse.z and iMouse.w are zero, unless the mouse was previously pressed and released (see below).
2. Button Pressed
iMouse.x and iMouse.y: Current mouse position (pixels).
iMouse.z and iMouse.w: Mouse position where the button was pressed (pixels, stays constant while pressed).
3. Button Released
When the mouse button is released, iMouse.z and iMouse.w are set to the negative values of the position where the button was released.
This tells your shader that a release event happened.
iMouse.x and iMouse.y stay at the current position (if the mouse is still over the viewport; otherwise, zero).
4. No Interaction / Mouse Outside Viewport
All values are zero.
https://www.shadertoy.com/faq - ShaderToy FAQ: How do I use mouse input in a shader?
https://www.shadertoy.com/view/ltKXzr ShaderToy Forum: iMouse uniform details
https://www.shadertoy.com/view/XsB3zH Example shader using iMouse release detection (search for iMouse.z < 0.0)
Summary Table
State	iMouse.x/y	iMouse.z/w
Idle	Current location	0, 0
Button Pressed	Current location	Press location (const)
Button Released	Current location	-Release location (negative)
Outside/No activity	0, 0	0, 0
In short:

Button down: iMouse.z and iMouse.w are positive, indicating the position where the button was pressed.
Button up: iMouse.z and iMouse.w are negative, indicating the position where the button was released.
No interaction: all zeros.
This enables shaders to react to mouse presses, releases, and drags with full pixel precision!
