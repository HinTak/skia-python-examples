////////////////////////////////////////////////////////////////////////////////
//
// Polar of a Cardioid
// Matthew Arcus, mla, 2020
//
// Given an implicit curve f(z) = 0, the polar curve for a point w is
// polar(z) = p.x + p.y where p = grad(f,z)*(w-z)
//
// The intersection of the polar with the curve itself gives the points
// on the curve whose tangents pass through p.
//
// Here we have a cardioid, drawn as a tangent envelope, and the polar of
// the pointer position, drawn as an implicit curve - the tangents through the
// pointer position meet the curve at its intersections with the polar.
//
// NEW FEATURE: (press 'g' to hide): a graph showing the distance of the
// pointer position from tangent(t), where tangent(t) is the line between
// (cos(t),sin(t)) and (cos(2t),sin(2t)) - zeros of this function are where
// a line passes through the point. The vertical lines are at -PI and +PI
// and there is a bogus zero at t = 0 in the middle (the two points
// coincide).
//
////////////////////////////////////////////////////////////////////////////////

const float PI = 3.1415927;

float line(vec2 p, vec2 a, vec2 b) {
  vec2 pa = p - a;
  vec2 ba = b - a;
  float h = dot(pa, ba) / dot(ba, ba);
  float d = length(pa - ba * h);
  return d;
}

const int N = 108;
float card0(vec2 z) {
  // Draw the envelope
  float d = 1e8;
  float k = 2.0*PI/float(N);
  float t = 2.0;
  for (int i = 0; i < N; i++) {
    float theta = float(i)*k;
    vec2 p = vec2(cos(theta),sin(theta));
    vec2 q = vec2(cos(t*theta),sin(t*theta));
    d = min(d,line(z,p,q));
  }
  return d;
}

// Maybe use dual numbers here?
// I did the diff for card by hand, but it got tedious for the polar,
// so it's numeric all the way (it's more generic anyway).
// Some macrology instead of higher order functions.
#define GRAD(F,Z,EPS)                      \
  (vec2(F(Z+vec2(EPS,0))-F(Z-vec2(EPS,0)), \
        F(Z+vec2(0,EPS))-F(Z-vec2(0,EPS)))/(2.0*EPS))

float card(vec2 p) {
  // Implicit function for cardioid
  float a = 1.0/3.0; // Line up with the unit circle
  p.x += a;
  float x = p.x, y = p.y;
  float t = x*x+y*y;
  return t*t - 4.0*a*x*t - 4.0*a*a*y*y;
}

vec2 cardgrad(vec2 z) {
#define F(Z) (card(Z))
  return GRAD(F,z,0.01);
#undef F
}

float carddist(vec2 z) {
  float d = card(z);
  vec2 ds = cardgrad(z);
  d /= length(ds);
  return d;
}

float polar(vec2 z, vec2 w) {
  float eps = 0.01;
  vec2 e = vec2(eps,0);
  return dot(vec2(1),cardgrad(z)*(w-z));
}

vec2 polargrad(vec2 z, vec2 w) {
#define F(Z) (polar(Z,w))
  return GRAD(F,z,0.01);
#undef F
}

float polardist(vec2 z, vec2 w) {
  float d = polar(z,w);
  vec2 ds = polargrad(z,w);
  return d/length(ds);
}

float line(vec3 p, vec3 l) {
  return abs(dot(p,l)/(p.z*length(l.xy)));
}

float graph(vec2 z, vec2 w) {
  // Draw curve, y = f(x), ie. f(x)-y = 0
  float t = PI*z.x;
  float y = 6.0*z.y;
  vec3 p0 = vec3(cos(t),sin(t),1);
  vec3 p1 = vec3(cos(2.0*t),sin(2.0*t),1);
  vec3 l = vec3(sin(t)-sin(2.0*t),
                cos(2.0*t)-cos(t),
                cos(t)*sin(2.0*t)-sin(t)*cos(2.0*t));
  return dot(vec3(w,1),l) - y;
}

vec2 graphgrad(vec2 z, vec2 w) {
#define F(Z) (graph(Z,w))
  return GRAD(F,z,0.01);
#undef F
}

float graphdist(vec2 z, vec2 w) {
  return graph(z,w)/length(graphgrad(z,w));
}

bool key(int code) {
  return texelFetch(iChannel3, ivec2(code,2),0).x != 0.0;
}

const int CHAR_G = 71;

void mainImage(out vec4 fragColor, vec2 fragCoord) {
  int AA = 2;
  vec3 col = vec3(0);
  vec2 w;
  if (iMouse.x > 0.0) w = (2.0*iMouse.xy-iResolution.xy)/iResolution.y;
  else w = cos(0.5*iTime-vec2(0,0.4*PI));
  for (int i = 0; i < AA; i++) {
    for (int j = 0; j < AA; j++) {
      vec2 z = (2.0*(fragCoord+vec2(i,j)/float(AA))-iResolution.xy)/iResolution.y;
      float ldist = graphdist(z,w);
      float lmin = 0.002, lmax = max(0.003,fwidth(z.x));
      float pmin = 0.015, pmax = max(0.02,2.0*fwidth(z.x));
      vec3 c = vec3(0.75);
      c.rg += 0.25*cos(2.0*PI*8.0*polardist(z,w));
      c.b += 0.25*cos(2.0*PI*8.0*carddist(z));
      c = mix(c,vec3(0.1),1.0-smoothstep(lmin,lmax,abs(card0(z))));
      c = mix(c,vec3(0,0,1),1.0-smoothstep(lmin,lmax,abs(carddist(z))));
      c = mix(c,vec3(1,0,0),1.0-smoothstep(lmin,lmax,abs(polardist(z,w))));
      if (!key(CHAR_G)) {
          c *= 0.8;
          c = mix(c,vec3(1),1.0-smoothstep(lmin,lmax,abs(ldist)));
          c = mix(c,vec3(1),1.0-smoothstep(lmin,lmax,line(z,vec2(-1,0),vec2(1,0))));
          c = mix(c,vec3(1),1.0-smoothstep(lmin,lmax,line(z,vec2(-1,0),vec2(-1,1))));
          c = mix(c,vec3(1),1.0-smoothstep(lmin,lmax,line(z,vec2(1,0),vec2(1,1))));
      }
      c = mix(c,vec3(0),1.0-smoothstep(pmin,pmax,distance(z,w)));
      col += c;
    }
  }
  col /= float(AA*AA);
  col = pow(col,vec3(0.4545));
  fragColor = vec4(col,1);
}
