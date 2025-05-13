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
