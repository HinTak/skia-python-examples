// Simulate the AT&T Pixel Machine demo in which a mouse moved the reflective sphere.
// by Eric Haines
// Derived from https://www.shadertoy.com/view/4dsGRn by Matthijs De Smedt, @anji_nl

const float ZMAX = 99999.0;
const float EPSILON = 0.001;

// model location (sphere)
vec3 lm = vec3(0.0,0.0,0.0);

vec3 backgroundColor = vec3(0.34, 0.55, 0.85);

struct Intersection
{
	vec3 p;
	float dist;
	
	vec3 n;
	vec3 diffuse;
	vec3 specular;
};
	
struct Ray
{
	vec3 o;
	vec3 dir;
};
	
struct Light
{
	vec3 p;
	vec3 color;
};
	
struct Plane
{
	vec3 n;
	float d;
};
	
struct Sphere
{
	vec3 c;
	float r;
};
	
float saturate(float f)
{
	return clamp(f,0.0,1.0);
}

Intersection RaySphere(Ray ray, Sphere sphere)
{
	Intersection i;
	i.dist = ZMAX;
	vec3 c = sphere.c;
	float r = sphere.r;
	vec3 e = c-ray.o;
	float a = dot(e, ray.dir);
	float b = r*r - dot(e,e) + a*a;
	if( b>0.0 )
	{
		float f = sqrt(b);
		float t = a - f;
		if(t > EPSILON)
		{
			i.p = ray.o + ray.dir*t;
			i.n = normalize(i.p-c);
			i.dist = t;
		}
	}
	return i;
}

Intersection RayPlane(Ray ray, Plane p)
{
	Intersection i;
	float num = p.d-dot(p.n, ray.o);
	float denom = dot(p.n, ray.dir);
	float t = num/denom;
	if(t > EPSILON)
	{
		i.p = ray.o + ray.dir * t;
		// hit rectangle?
		if ( i.p.x < -8.0 || i.p.x > 8.0 || i.p.z < 4.0 || i.p.z > 24.0 ) {
			// missed
			i.dist = ZMAX;
		} else {
			i.n = p.n;
			i.dist = t;
		}
	}
	else
	{
		// did not hit plane
		i.dist = ZMAX;
	}
	return i;
}

Intersection MinIntersection(Intersection a, Intersection b)
{
	if(a.dist < b.dist)
	{
		return a;
	}
	else
	{
		return b;
	}
}

vec3 PlaneMaterial(Intersection i)
{
	float d = 0.0;
	// checkerboard function that returns 0 or 1
	d = mod(floor(i.p.x)+floor(i.p.z),2.0);
	// vary between red (0) and yellow (1)
	return vec3(0.8 + 0.1*d, 0.3 + 0.55*d, 0.15 - 0.1*d)*0.8;
}

Intersection SceneIntersection(Ray r)
{
	Intersection iOut;
	
	Plane plane;
	plane.n = normalize(vec3(0,1,0));
	plane.d = -2.0;
	Intersection iPlane = RayPlane(r, plane);
	iPlane.diffuse = PlaneMaterial(iPlane);
	iPlane.specular = vec3(0.0);
	iOut = iPlane;
	
    vec3 pos = lm;
    Sphere sphere;
    sphere.c = pos;
    sphere.r = 2.0;
    Intersection iSphere = RaySphere(r, sphere);
    iSphere.diffuse = vec3(0.2);
    iSphere.specular = vec3(0.7);
    iOut = MinIntersection(iOut, iSphere);

	return iOut;
}

vec3 CalcLighting(Light light, Intersection i, vec3 origin)
{
	if ( i.dist >= ZMAX ) {
		return backgroundColor;
	}
	vec3 n = i.n;
	vec3 p = i.p;
	vec3 l = light.p;
	vec3 v = normalize(origin-p);
	vec3 h = normalize(l+v);
	float NdotL = saturate(dot(n,l));
	float NdotH = saturate(dot(n,h));
	vec3 diffuse = NdotL*i.diffuse;
	vec3 spec = 0.18 * pow(NdotH,40.0) * i.specular;
	vec3 color;
	color = (diffuse+spec) * light.color;

	Ray shadowRay;
	shadowRay.o = i.p;
	float lightDist = 100.0;
	shadowRay.dir = light.p;
	Intersection shadowI = SceneIntersection(shadowRay);
	if(shadowI.dist < lightDist)
	{
		color *= 0.4;
	}
	
	return color;
}

vec3 GetLighting(Intersection i, vec3 origin)
{
	vec3 color = vec3(0);
	Light light;
	
    // or just set X to -2.0 to stop animation
	light.p = normalize(vec3(2.0*sin(iTime*0.5),2.0,-2.0));
	light.color = vec3(2.5);
	color += CalcLighting(light, i, origin);

	return color;
}

vec3 GetColor(Ray ray, vec2 fragCoord)
{
	// Branch version
	Intersection i = SceneIntersection(ray);
	vec3 color = GetLighting(i, ray.o);
	if(i.dist < ZMAX-EPSILON && i.specular.x > 0.0)
	{
		vec3 specular = i.specular;
		vec3 incident = normalize(i.p-ray.o);
		ray.dir = reflect(incident,i.n);
		ray.o = i.p+ray.dir*EPSILON;
		// First bounce
		i = SceneIntersection(ray);
		color += GetLighting(i, ray.o) * specular;
        /* no second bounce needed, since there's just the shiny sphere.
		if(i.dist < ZMAX-EPSILON && i.specular.x > 0.0)
		{
			specular *= i.specular;
			incident = normalize(i.p-ray.o);
			ray.dir = reflect(incident,i.n);
			ray.o = i.p+ray.dir*EPSILON;
			// Second bounce
			i = SceneIntersection(ray);
			if(i.dist < ZMAX-EPSILON && specular.x > 0.0)
			{
				color += GetLighting(i, ray.o) * specular;
			}
		}
		*/
    }
	return color;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{

    vec2 mouse = (iMouse.xy/iResolution.xy*2.0-vec2(1.0))*vec2(iResolution.x/iResolution.y,1.0)*2.0;
    lm = vec3(1.5*mouse.x,0.0,3.0*mouse.y+14.0);

	vec2 pos = -1.0 + 2.0 * ( fragCoord.xy / iResolution.xy );
	vec2 posAR;
	posAR.x = pos.x * (iResolution.x/iResolution.y);
	posAR.y = pos.y;
    // fov knob
    posAR *= 0.3;
	vec3 rayDir = normalize(vec3(posAR.x, posAR.y - 0.30, 1.0));
	Ray ray;
	ray.o = vec3(0,2.2,0);
	ray.dir = rayDir;
	
	vec3 color = GetColor(ray, fragCoord);
	fragColor = vec4(color.x, color.y, color.z, 1.0 );
}
