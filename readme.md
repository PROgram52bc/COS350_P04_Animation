# Ray Tracing Project

## Electives

### Directional Light
Directional light is implemented by adding an extra parameter to the `Light` class.

Light will always be from the same direction with the same intensity no matter where it hits.

#### Artifact
![Planets](artifacts/direction_light.png)

As shown, a directional light uniformly hits on all the spheres, creating an approximate scene for the planets in space lit by the sun light. Also notice that there is a shadow casted by planets that are close to each other.

### Refraction
Refraction is implemented using snell's law.

#### Artifact

![Refraction1](artifacts/refraction1.png)
![Refraction2](artifacts/refraction2.png)

As shown, The three big spheres have reflective, refractive, and diffusive properties respectively.

### Triangle
Triangle is implemented using Cramer's rule.

#### Artifact
![Triangle](artifacts/triangle.png)

As shown, a 3D Christmas tree is rendered using triangles.
