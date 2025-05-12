////////////////////////////////////////////////////////////////////////////////
//
// Complex log with hex grid
//
// mla, 2020
//
// Complex log maps the strip with -PI < Im(z) < PI to the complex
// plane with a branch cut on the negative real axis (for log).
// A transformed pattern that repeats vertically with a
// period of 2PI will then appear seamless across the branch cut.
//
// See eg. https://www.shadertoy.com/view/WdSSWz for the square pattern case.
// A hexagonal grid is slightly more complicated.
//
// 'm' shows transition from x to log(x)
// 'b' shows untransformed plane
//
////////////////////////////////////////////////////////////////////////////////

// Just show the untransformed band between -PI and PI.
bool showband = false;
// Do a gradual transition from x to log(x), this disables
// the inversion as it's too confusing with it.
bool mixit = false;

// Constants for hexagonal grid
const float X = 1.732050808; // sqrt(3)
const float Y = 0.577350269; // 1/sqrt(3)
const mat2 M = 0.5*mat2(1,-X,1,X);
const mat2 Minv = mat2(1,1,-Y,Y);

void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
  showband = key(CHAR_B);
  mixit = key(CHAR_M);
  // From start point p in the grid, go A up and B/2 along to
  // arrive at point q. A and B must be of same parity for
  // this to work with K = 1.0. Now rotate grid so q is
  // vertically above p, and scale so the distance between
  // them is 2PI. K > 1 adds more triangles so all parities
  // of A and B work (as far as the grid skeleton is concerned).
  // Not sure of exact relationship between N, the number
  // of colors, and A,B,K. These all work:
  //float A = 7.0, B = 4.0, K = 2.0, N = 8.0;
  float A = 6.0, B = 1.0, K = 6.0, N = 6.0;
  //float A = 3.0, B = 5.0, K = 3.0, N = 3.0;
  //float A = 4.0, B = 3.0, K = 2.0, N = 3.0;
  //float A = 7.0, B = 3.0, K = 4.0, N = 12.0;
  //float A = 3.0, B = 5.0, K = 1.0 + floor(iTime), N = 3.0; // Test

  float scale = 1.0;
  if (showband) scale = 4.0;
    
  vec2 z = (2.0*fragCoord-iResolution.xy)/iResolution.y;
  z *= scale;

  vec2 m = vec2(-0.5);
  if (iMouse.x > 1.0) {
    m = (2.0*iMouse.xy-iResolution.xy)/iResolution.y;
    m *= scale;
  }
  if (!showband) {
    z -= m;
    if (!mixit) z /= dot(z,z);
    z += m;
    float t = 1.0;
    if (mixit) {
      t = mod(0.2*iTime,4.0);
      t = min(t,4.0-t);
        t -= 0.5;
        t = clamp(t,0.0,1.0);
    }
    z = mix(z,clog(z),smoothstep(0.0,1.0,t));
  }

  vec3 col = vec3(0);
  z /= PI;
  if (abs(z.y) < 1.0) {
    // Alignment of rotated triangular grid.
    // Rotated grid should fit between -1 < y < 1
    // with top and bottom edges coherent.
    vec2 rot = vec2(A,B/X);
    z = cmul(rot,z);
    if (!key(CHAR_T)) z.x += 0.1*iTime*length(rot);
    z *= 0.25*K;

    // Hexagonal grid.
    z *= X;
    z.x += 0.5;
    z = Minv*z; // Convert to square grid
    ivec2 index = ivec2(floor(z)); // Remember cell in grid
    z -= floor(z);
    z = M*z; // Back to triangles
    z.x -= 0.5;

    // Color from index
    col = hsv2rgb(vec3(float(index.x+index.y)/N,1,1));
    bool inlower = z.y < 0.0; // Point is in lower triangle,
    if (inlower) col *= 0.6;
    // Shade edges of triangle
    z = abs(z);
    float d = z.y;
    d = min(d,abs(dot(z-vec2(0.5,0),0.5*vec2(X,1))));
    col *= smoothstep(0.02,0.05,d);
  }
  col = pow(col,vec3(0.4545));
  fragColor = vec4(col,1);
}
