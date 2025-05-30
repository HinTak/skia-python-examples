// Raindrops on glass by YeHaike, Copyright YeHaike All Rights Reserved(841660657@qq.com, NonCommercial, No Copy, No Modify)
// ShaderToy: https://www.shadertoy.com/view/DdKyR1
// Completely reimplemented

// Refer to this: https://www.shadertoy.com/view/ltffzl
// {
// Heartfelt - by Martijn Steinrucken aka BigWings - 2017
// Email:countfrolic@gmail.com Twitter:@The_ArtOfCode
// License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
// }

#define RandomSeed 4.3315
// Number Scale Of Static Raindrops On Same Screen, Range: [0.0, 1.0]
#define NumberScaleOfStaticRaindrops 0.35
#define NumberScaleOfRollingRaindrops 0.35
#define RaindropBlur 0.0
#define BackgroundBlur 2.0
#define StaticRaindropUVScale 20.0
#define RollingRaindropUVScaleLayer01 2.25
#define RollingRaindropUVScaleLayer02 2.25

//
//////////////////// 3D OpenSimplex2S noise with derivatives  ////////////////////
//////////////////// Output: vec4(dF/dx, dF/dy, dF/dz, value) ////////////////////

// Permutation polynomial hash credit Stefan Gustavson
vec4 permute(vec4 t) {
    return t * (t * 34.0 + 133.0);
}

// Gradient set is a normalized expanded rhombic dodecahedron
vec3 grad(float hash) {
    
    // Random vertex of a cube, +/- 1 each
    vec3 cube = mod(floor(hash / vec3(1.0, 2.0, 4.0)), 2.0) * 2.0 - 1.0;
    
    // Random edge of the three edges connected to that vertex
    // Also a cuboctahedral vertex
    // And corresponds to the face of its dual, the rhombic dodecahedron
    vec3 cuboct = cube;
    cuboct[int(hash / 16.0)] = 0.0;
    
    // In a funky way, pick one of the four points on the rhombic face
    float type = mod(floor(hash / 8.0), 2.0);
    vec3 rhomb = (1.0 - type) * cube + type * (cuboct + cross(cube, cuboct));
    
    // Expand it so that the new edges are the same length
    // as the existing ones
    vec3 grad = cuboct * 1.22474487139 + rhomb;
    
    // To make all gradients the same length, we only need to shorten the
    // second type of vector. We also put in the whole noise scale constant.
    // The compiler should reduce it into the existing floats. I think.
    grad *= (1.0 - 0.042942436724648037 * type) * 3.5946317686139184;
    
    return grad;
}

// BCC lattice split up into 2 cube lattices
vec4 os2NoiseWithDerivativesPart(vec3 X) {
    vec3 b = floor(X);
    vec4 i4 = vec4(X - b, 2.5);
    
    // Pick between each pair of oppposite corners in the cube.
    vec3 v1 = b + floor(dot(i4, vec4(.25)));
    vec3 v2 = b + vec3(1, 0, 0) + vec3(-1, 1, 1) * floor(dot(i4, vec4(-.25, .25, .25, .35)));
    vec3 v3 = b + vec3(0, 1, 0) + vec3(1, -1, 1) * floor(dot(i4, vec4(.25, -.25, .25, .35)));
    vec3 v4 = b + vec3(0, 0, 1) + vec3(1, 1, -1) * floor(dot(i4, vec4(.25, .25, -.25, .35)));
    
    // Gradient hashes for the four vertices in this half-lattice.
    vec4 hashes = permute(mod(vec4(v1.x, v2.x, v3.x, v4.x), 289.0));
    hashes = permute(mod(hashes + vec4(v1.y, v2.y, v3.y, v4.y), 289.0));
    hashes = mod(permute(mod(hashes + vec4(v1.z, v2.z, v3.z, v4.z), 289.0)), 48.0);
    
    // Gradient extrapolations & kernel function
    vec3 d1 = X - v1; vec3 d2 = X - v2; vec3 d3 = X - v3; vec3 d4 = X - v4;
    vec4 a = max(0.75 - vec4(dot(d1, d1), dot(d2, d2), dot(d3, d3), dot(d4, d4)), 0.0);
    vec4 aa = a * a; vec4 aaaa = aa * aa;
    vec3 g1 = grad(hashes.x); vec3 g2 = grad(hashes.y);
    vec3 g3 = grad(hashes.z); vec3 g4 = grad(hashes.w);
    vec4 extrapolations = vec4(dot(d1, g1), dot(d2, g2), dot(d3, g3), dot(d4, g4));
    
    // Derivatives of the noise
    vec3 derivative = -8.0 * mat4x3(d1, d2, d3, d4) * (aa * a * extrapolations)
        + mat4x3(g1, g2, g3, g4) * aaaa;
    
    // Return it all as a vec4
    return vec4(derivative, dot(aaaa, extrapolations));
}

// Rotates domain, but preserve shape. Hides grid better in cardinal slices.
// Good for texturing 3D objects with lots of flat parts along cardinal planes.
vec4 os2NoiseWithDerivatives_Fallback(vec3 X) {
    X = dot(X, vec3(2.0/3.0)) - X;
    
    vec4 result = os2NoiseWithDerivativesPart(X) + os2NoiseWithDerivativesPart(X + 144.5);
    
    return vec4(dot(result.xyz, vec3(2.0/3.0)) - result.xyz, result.w);
}

// Gives X and Y a triangular alignment, and lets Z move up the main diagonal.
// Might be good for terrain, or a time varying X/Y plane. Z repeats.
vec4 os2NoiseWithDerivatives_ImproveXY(vec3 X) {
    
    // Not a skew transform.
    mat3 orthonormalMap = mat3(
        0.788675134594813, -0.211324865405187, -0.577350269189626,
        -0.211324865405187, 0.788675134594813, -0.577350269189626,
        0.577350269189626, 0.577350269189626, 0.577350269189626);
    
    X = orthonormalMap * X;
    vec4 result = os2NoiseWithDerivativesPart(X) + os2NoiseWithDerivativesPart(X + 144.5);
    
    return vec4(result.xyz * orthonormalMap, result.w);
}

//////////////////////////////// End noise code ////////////////////////////////
//


float GradientWave(float b, float t) 
{
	return smoothstep(0., b, t)*smoothstep(1., b, t);
}

float Random(vec2 UV, float Seed) 
{
    return fract(sin(dot(UV.xy*13.235, vec2(12.9898,78.233)) * 0.000001) * 43758.5453123 * Seed);
}

vec3 RandomVec3(vec2 UV, float Seed) 
{
    return vec3(Random(UV, Seed), Random(UV * 2.0, Seed), Random(UV * 3.0, Seed));
}

vec4 RandomVec4(vec2 UV, float Seed) 
{
    return vec4(Random(UV * 1.5, Seed), Random(UV * 2.5, Seed), Random(UV * 3.5, Seed), Random(UV * 4.5, Seed));
}

vec3 RaindropSurface(vec2 XY, float DistanceScale, float ZScale)
{
    /*
    Given the following equation, where A,M, N and S are all constants and Z and t are intermediate variables.
    
    YeHaike's raindrop(Raindrop on glass) surface equation:
    
        Z = (1-(x/A)^2-(y/A)^2)^(A/2) 
        t=min(max((Z-M)/(N-M),0.0),1.0) 
        z=S*(t^2)*(3.0-2.0*t)
    
    Find the derivative of z with respect to x and y:
    
        t(x, y) = min(max(((1 - (x/A)^2 - (y/A)^2)^(A/2) - M) / (N - M), 0.0), 1.0)
        N = 1.5
        M = 0.5

        When 0.0 < (Z - M)/(N - M) < 1.0：

        ∂z/∂x = S*(6t - 8t^2) * (1/(N - M)) * (-x/A*(1 - (x/A)^2 - (y/A)^2)^((A/2)-1))

        When (Z - M)/(N - M) ≤ 0.0 or (Z - M)/(N - M) ≥ 1.0：

        ∂z/∂x = 0
        
        Similarly, we can find the partial derivative of z with respect to y：

        When 0.0 < (Z - M)/(N - M) < 1.0：

        ∂z/∂y = S*(6t - 8t^2) * (1/(N - M)) * (-y/A*(1 - (x/A)^2 - (y/A)^2)^((A/2)-1))

        When (Z - M)/(N - M) ≤ 0.0 or (Z - M)/(N - M) ≥ 1.0：

        ∂z/∂y = 0

    This is the partial derivative of z with respect to x and y.
    */
    
    float A = DistanceScale;
    float x = XY.x;
    float y = XY.y;
    float N = 1.5;
    float M = 0.5;
    float S = ZScale;
    
    float TempZ = 1.0-pow(x/A,2.0)-pow(y/A,2.0);
    float Z = pow(TempZ, A/2.0);
    float ZInMAndN = (Z-M)/(N-M);
    float t = min(max(ZInMAndN, 0.0), 1.0);
    
    float Height = S*t*t*(3.0-2.0*t);
    
    float Part01 = S*(6.0*t - 8.0*t*t);
    float Part02 = 1.0/(N - M);
    float Part03 = -1.0/A*pow(TempZ,A/2.0-1.0);
    
    float Part03OfX = x*Part03;
    float Part03OfY = y*Part03;
    
    float TempValue = (ZInMAndN > 0.0 && ZInMAndN < 1.0) ? Part01*Part02 : 0.0;
    
    float PartialDerivativeX=TempValue*Part03OfX;
    float PartialDerivativeY=TempValue*Part03OfY;
    vec2 PartialDerivative = Height > 0.0 ? vec2(PartialDerivativeX, PartialDerivativeY) : vec2(0.0,0.0);
    return vec3(Height, PartialDerivative);
}

// Map to range and clamp to [0.0,1.0]
float MapToRange(float edge0, float edge1, float x)
{
    float t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
    return t;
}

// x is in [0.0,1.0]
float ProportionalMapToRange(float edge0, float edge1, float x)
{
    float t = edge0+(edge1-edge0)*x;
    return t;
}


// Return: x is height; yz is normal
// UVScale: Default is 20.0
vec3 StaticRaindrops(vec2 UV, float Time, float UVScale) 
{
    vec2 TempUV = UV;
	TempUV *= UVScale; //15.0
       
    vec2 ID = floor(TempUV);
    vec3 RandomValue = RandomVec3(vec2(ID.x*470.15, ID.y*653.58), RandomSeed);
    TempUV = fract(TempUV)-0.5;
    vec2 RandomPoint = (RandomValue.xy-0.5)*0.25;
    vec2 XY = RandomPoint - TempUV;
    float Distance = length(TempUV-RandomPoint);  
    
    vec3 X = vec3(vec2(TempUV.x*305.0*0.02, TempUV.y*305.0*0.02), 1.8660254037844386);
    vec4 noiseResult = os2NoiseWithDerivatives_ImproveXY(X);
    float EdgeRandomCurveAdjust = noiseResult.w*mix(0.02, 0.175, fract(RandomValue.x));
    
    Distance = EdgeRandomCurveAdjust*0.5+Distance;
    Distance = Distance* clamp(mix(1.0, 55.0,RandomPoint.x),1.0, 3.0);
    float Height = smoothstep(.2, 0., Distance);
    
    float GradientFade = GradientWave(.0005, fract(Time*0.02+RandomValue.z));
    
    float DistanceMaxRange =  1.45 * GradientFade;
    vec2 Direction = (TempUV-RandomPoint);
    
    float Theta = 3.141592653-acos(dot(normalize(Direction), vec2(0.0,1.0)));
    Theta = Theta * RandomValue.z;
    float DistanceScale = 0.2/(1.0-0.8*cos(Theta-3.141593/2.0-1.6));
    float YDistance = length(vec2(0.0,TempUV.y)-vec2(0.0,RandomPoint.y));
    
    float NewDistance = MapToRange(0.0,DistanceMaxRange*pow(DistanceScale,1.0),Distance);

    float Scale = 1.65*(0.2+DistanceScale*1.0)*DistanceMaxRange*mix(1.5,0.5,RandomValue.x);
    vec2 TempXY = vec2(XY.x*1.0,XY.y)*4.0;
    float RandomScale = ProportionalMapToRange(0.85,1.35,RandomValue.z);
    TempXY.x = RandomScale*mix(TempXY.x ,TempXY.x / smoothstep(1.0,0.4,YDistance*RandomValue.z),smoothstep(1.0,0.0,RandomValue.x));
    TempXY = TempXY + EdgeRandomCurveAdjust*1.0;
    vec3 HeightAndNormal = RaindropSurface(TempXY, Scale,1.0);
    HeightAndNormal.yz = -HeightAndNormal.yz;
    
    float RandomVisible = (fract(RandomValue.z*10.*RandomSeed) < NumberScaleOfStaticRaindrops ? 1.0f : 0.0f);
    HeightAndNormal.yz = HeightAndNormal.yz*RandomVisible;
    HeightAndNormal.x = smoothstep(0.0, 1.0, HeightAndNormal.x)*RandomVisible;

    return HeightAndNormal;
}


// Return: x is height; yz is normal; w is trail.
// UVScale: Default is 2.25
vec4 RollingRaindrops(vec2 UV, float Time, float UVScale) 
{
    vec2 LocalUV = UV*UVScale;
    vec2 TempUV = LocalUV;

    vec2 ConstantA = vec2(6.0, 1.0);
    vec2 GridNum = ConstantA*2.0;
    vec2 GridID = floor(LocalUV*GridNum);
    
    float RandomFloat = Random(vec2(GridID.x*131.26, GridID.x*101.81), RandomSeed);

    float TimeMovingY = Time*0.85*ProportionalMapToRange(0.1,0.25,RandomFloat); //Time
    LocalUV.y += TimeMovingY;
    float YShift = RandomFloat;
    LocalUV.y += YShift;
    
    
    vec2 ScaledUV = LocalUV*GridNum;
    GridID = floor(ScaledUV);
    vec3 RandomVec3 = RandomVec3(vec2(GridID.x*17.32, GridID.y*2217.54), RandomSeed);
    
    vec2 GridUV = fract(ScaledUV)-vec2(0.5, 0.0);
      
    
    float SwingX = RandomVec3.x-0.5;
    
    float SwingY = TempUV.y*20.0;
    float SwingPosition = sin(SwingY+sin(GridID.y*RandomVec3.z+SwingY)+GridID.y*RandomVec3.z);
    SwingX += SwingPosition*(0.5-abs(SwingX))*(RandomVec3.z-0.5);
    SwingX *= 0.65;
    float RandomNormalizedTime = fract(TimeMovingY+RandomVec3.z)*1.0; // Time
    SwingY = (GradientWave(0.87, RandomNormalizedTime)-0.5)*0.9+0.5;
    SwingY = clamp(SwingY,0.15,0.85);
    vec2 Position = vec2(SwingX, SwingY);    
    
    
    vec2 XY = Position - GridUV;
    vec2 Direction = (GridUV-Position)*ConstantA.yx;
    float Distance = length(Direction);
   
    //---------
    vec3 X = vec3(vec2(TempUV.x*513.20*0.02, TempUV.y*779.40*0.02), 2.1660251037743386);
    vec4 NoiseResult = os2NoiseWithDerivatives_ImproveXY(X);
    float EdgeRandomCurveAdjust = NoiseResult.w*mix(0.02, 0.175, fract(RandomVec3.y));
    
    Distance = EdgeRandomCurveAdjust+Distance;
    float Height = smoothstep(.2, 0., Distance);
    float NewDistance = MapToRange(0.0,0.2,Distance);

    
    float DistanceMaxRange =  1.45;
    
    float Theta = 3.141592653-acos(dot(normalize(Direction), vec2(0.0,1.0)));
    Theta = Theta * RandomVec3.z;
    float DistanceScale = 0.2/(1.0-0.8*cos(Theta-3.141593/2.0-1.6));
    float Scale = 1.65*(0.2+DistanceScale*1.0)*DistanceMaxRange*mix(1.0,0.25,RandomVec3.x*1.0);
    vec2 TempXY = vec2(XY.x*1.0,XY.y)*4.0;
    float RandomScale = ProportionalMapToRange(0.85,1.35,RandomVec3.z);
    TempXY = TempXY*vec2(1.0,4.2) + EdgeRandomCurveAdjust*0.85;
    vec3 HeightAndNormal = RaindropSurface(TempXY, Scale,1.0);

    //----------
        
    // Trail
    float TrailY = pow(smoothstep(1.0, SwingY, GridUV.y), 0.5);
    float TrailX = abs(GridUV.x-SwingX)*mix(0.8,4.0,smoothstep(0.0,1.0,RandomVec3.x));
    float Trail = smoothstep(0.25*TrailY, 0.15*TrailY*TrailY, TrailX);
    float TrailClamp = smoothstep(-0.02, 0.02, GridUV.y-SwingY);
    Trail *= TrailClamp*TrailY;
    
    float SignOfTrailX = sign(GridUV.x-SwingX);
    vec3 NoiseInput = vec3(vec2(TempUV.x*513.20*0.02*SignOfTrailX, TempUV.y*779.40*0.02), 2.1660251037743386);
    vec4 TrailNoiseResult = os2NoiseWithDerivatives_ImproveXY(NoiseInput);
    float TrailEdgeRandomCurveAdjust = TrailNoiseResult.w*mix(0.002, 0.175, fract(RandomVec3.y));
    float TrailXDistance = MapToRange(0.0,0.1,TrailEdgeRandomCurveAdjust*0.5+TrailX);
    vec2 TrailDirection = SignOfTrailX*vec2(1.0,0.0) + vec2(0.0,1.0)*smoothstep(1.0, 0.0,Trail)*0.5;
    vec2 TrailXY = TrailDirection*1.0*TrailXDistance;
 
    vec3 TrailHeightAndNormal = RaindropSurface(TrailXY, 1.0,1.0);
    
    TrailHeightAndNormal = TrailHeightAndNormal * pow(Trail*RandomVec3.y, 2.0);
    TrailHeightAndNormal.x = smoothstep(0.0, 1.0, TrailHeightAndNormal.x);
    
    //fragColor = vec4(TrailHeightAndNormal.yz,0.0, 1.0);
    
    // Remain Trail Droplets
    SwingY = TempUV.y;
    float RemainTrail = smoothstep(0.2*TrailY, 0.0, TrailX);
    float RemainDroplet = max(0.0, (sin(SwingY*(1.0-SwingY)*120.0)-GridUV.y))*RemainTrail*TrailClamp*RandomVec3.z;
    SwingY = fract(SwingY*10.0)+(GridUV.y-0.5);
    vec2 RemainDropletXY= GridUV-vec2(SwingX, SwingY);
    RemainDropletXY = RemainDropletXY * vec2(1.2,0.8);

    RemainDropletXY = RemainDropletXY + EdgeRandomCurveAdjust*0.85;
    vec3 RemainDropletHeightAndNormal = RaindropSurface(RemainDropletXY, 2.0*RemainDroplet,1.0);
    
    RemainDropletHeightAndNormal.x = smoothstep(0.0, 1.0, RemainDropletHeightAndNormal.x);
    RemainDropletHeightAndNormal = TrailHeightAndNormal.x > 0.0 ? vec3(0.0,0.0,0.0) : RemainDropletHeightAndNormal;
    
    
    vec4 ReturnValue;
    ReturnValue.x = HeightAndNormal.x + TrailHeightAndNormal.x*TrailY*TrailClamp + RemainDropletHeightAndNormal.x*TrailY*TrailClamp;
    
    ReturnValue.yz = HeightAndNormal.yz + TrailHeightAndNormal.yz + RemainDropletHeightAndNormal.yz;
    ReturnValue.w = Trail;
    
    float RandomVisible = (fract(RandomVec3.z*20.*RandomSeed) < NumberScaleOfRollingRaindrops ? 1.0f : 0.0f);
    ReturnValue = ReturnValue * RandomVisible;
    return ReturnValue;

}

vec4 Raindrops(vec2 UV, float Time, float UVScale00, float UVScale01, float UVScale02) 
{
    vec3 StaticRaindrop = StaticRaindrops(UV, Time, UVScale00);
    vec4 RollingRaindrop01 = RollingRaindrops(UV, Time, UVScale01);
    //vec4 RollingRaindrop02 = RollingRaindrops(UV*1.7, Time, UVScale02);

    
    float Height = StaticRaindrop.x + RollingRaindrop01.x;// + RollingRaindrop02.x;
    vec2 Normal = StaticRaindrop.yz + RollingRaindrop01.yz;// + RollingRaindrop02.yz;
    float Trail = RollingRaindrop01.w;//(RollingRaindrop01.w + RollingRaindrop02.w)*0.5;
    
    return vec4(Height, Normal, Trail);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    float Time = iTime;
    float ScaledTime = Time*0.2;
    vec2 GlobalUV = fragCoord.xy/iResolution.xy;
	vec2 LocalUV = (fragCoord.xy-.5*iResolution.xy) / iResolution.y;

    float RaindropsAmount = sin(Time*0.25)*0.5+0.5;
    
    float MaxBlur = mix(BackgroundBlur, BackgroundBlur*2.0, RaindropsAmount);
    float MinBlur = RaindropBlur;
       
    float StaticRaindropsAmount = smoothstep(-0.5, 1.0, RaindropsAmount)*2.0;
    float RollingRaindropsAmount01 = smoothstep(0.25, 0.75, RaindropsAmount);
    float RollingRaindropsAmount02 = smoothstep(0.0, 0.5, RaindropsAmount);
    
    //
    vec4 Raindrop = Raindrops(LocalUV, Time,
        StaticRaindropUVScale, RollingRaindropUVScaleLayer01, RollingRaindropUVScaleLayer02); 
    //
    
    float RaindropHeight = Raindrop.x;
    float RaindropTrail = Raindrop.w;
    vec2 RaindropNormal = -Raindrop.yz;
    RaindropNormal = RaindropHeight > 0.0 ? RaindropNormal*0.15 : vec2(0.0,0.0);

    vec2 UVWithNormal = GlobalUV+RaindropNormal;
    float EdgeColorScale = smoothstep(0.2, 0.0, length(RaindropNormal));
    EdgeColorScale = RaindropHeight > 0.0 ? pow(EdgeColorScale,0.5)*0.2 + 0.8 : 1.0;

    float Blur = mix(MinBlur, MaxBlur, smoothstep(0.0, 1.6, length(RaindropNormal)));
    Blur = RaindropHeight > 0.0 ? Blur : MaxBlur;
    Blur = ProportionalMapToRange(MinBlur, Blur, 1.0 - RaindropTrail);
    EdgeColorScale = pow(EdgeColorScale, 0.85);
    
    vec3 FinalColor = textureLod(iChannel0, UVWithNormal, Blur).rgb * EdgeColorScale;
    
    fragColor = vec4(FinalColor, 1.0);
    
}
