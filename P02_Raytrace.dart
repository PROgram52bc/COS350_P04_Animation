import 'dart:io';
import 'dart:math';

import 'common/image.dart';
import 'common/jsonloader.dart';
import 'common/maths.dart';
import 'common/scene.dart';

// The following functions provide algorithms for raytracing a scene.
//
// `raytraceScene` renders an image for given scene by calling `irradiance`.
// `irradiance` computes irradiance from scene "seen" along ray.
// `intersectRayScene` finds the first intersection of ray and scene.
//
// You will provide your implementation to each of the functions below.
// We have left pseudocode in comments for all problems but extra credits.
// For extra credit, you will need to modify this and `common/scene.dart` files.
//
// Note: The code structure here is only a suggestion.
//       Feel free to modify it as you see fit.
//       Your final image must match _perfectly_ the corresponding images in references folder.
//       If your final image is not **exactly** the same, you will lose points.
//
// Hint: Use the image to debug your code!
//       - Store x,y,z values of ray direction as r,g,b to make sure the rays are pointing in correct direction.
//       - Store x,y,z values of intersection to make sure they seem reasonable.
//       - Store x,y,z values of normals at intersections to make sure they are reasonable.
//       - Et cetera.
//
// Hint: Implement this project in stages!
//       Trying to write the entire raytracing system at once will often introduce multiple errors that will be very tricky to debug.
//       Use the critical thinking skill of Developing Sub-Goals from COS 265 to attack this project!


// Set `writeImageInBinary` to `false` to write image files in ASCII.
// ASCII image files can be opened and analyzed in a text editor.
bool writeImageInBinary = true;

// Set `overrideResolution` to `Size2i(32, 32)` to override the resolution settings stored in the JSON file.
// You can use this override to render a smaller image that is perhaps easier to debug, especially when combined with `writeImageInBinary`.
Size2i overrideResolution = null;
// Size2i overrideResolution = Size2i(32, 32);     // uncomment to render 64x64 image

const int irradianceMaxDepth = 5;

// Comment out lines below to prevent re-rendering every scene.
// If you create a new scene file, add it to the list below.
// NOTE: **BEFORE** you submit your solution, uncomment all lines, so
//       your code will render all the scenes!
List<String> scenePaths = [
    // 'scenes/P02_00_sphere.json',
    // 'scenes/P02_01_sphere_ka.json',
    // 'scenes/P02_02_sphere_room.json',
    // 'scenes/P02_03_quad.json',
    // 'scenes/P02_04_quad_room.json',
    // 'scenes/P02_05_ball_on_plane.json',
    // 'scenes/P02_06_balls_on_plane.json',
    // 'scenes/P02_07_reflection.json',
    // 'scenes/P02_08_aa.json',
    // 'scenes/P02_09_refraction.json',
    // 'scenes/P02_10_direction_light.json',
    'scenes/P02_11_triangle.json'
];

// Determines if given ray intersects any surface in the scene.
// If ray does not intersect anything, null is returned.
// Otherwise, details of first intersection are returned as an `Intersection` object.
Intersection intersectRayScene(Scene scene, Ray ray) {
    Intersection intersection;
    var t_closest = double.infinity;

    for (Surface surface in scene.surfaces) {
        if (surface.type == 'sphere') {
            double a = 1;
            double b = (ray.d*2).dot(ray.e-surface.frame.o);
            double c = (ray.e-surface.frame.o).lengthSquared - pow(surface.size, 2);
            var determinant = b*b - 4*a*c;
            // no solution
            if (determinant < 0) {
                continue;
            } else {
                // find closest valid t, if neither are valid, t = infinity
                double t = [(-b+sqrt(determinant))/(2*a), (-b-sqrt(determinant))/(2*a)]
                        .where((t)=>ray.valid(t))
                        .fold(double.infinity, min);
                // if distance 't' is closer, construct meaningful Intersection object
                if (t < t_closest) {
                    t_closest = t;
                    Frame frame = Frame(o:ray.eval(t), n:Normal.fromPoints(surface.frame.o, ray.eval(t)));
                    intersection = Intersection(frame, surface, t);
                }
            }
        } else if (surface.type == 'quad') {
            double determinant = ray.d.dot(surface.frame.z);
            if (determinant == 0) {
                // if parallel
                continue;
            }
            double t = surface.frame.z.dot(surface.frame.o - ray.e)/determinant;
            Point point = ray.eval(t);
            // check whether point is in quad
            Vector offset = point - surface.frame.o;
            if (offset.dot(surface.frame.x).abs() > surface.size 
                    || offset.dot(surface.frame.y).abs() > surface.size) {
                continue;
            }
            if (ray.valid(t) && t < t_closest) {
                t_closest = t;
                Direction normal = determinant < 0 ? surface.frame.z : -surface.frame.z;
                Frame frame = Frame(o:point, z:surface.frame.z);
                intersection = Intersection(frame, surface, t);
            }
        } else if (surface.type == 'triangle') {
            double determinant = ray.d.dot(surface.frame.z);
            if (determinant == 0) {
                // if parallel
                continue;
            }
            double t = surface.frame.z.dot(surface.frame.o - ray.e)/determinant;
            Point point = ray.eval(t);
            // check if point is in triangle
            Point c = surface.frame.o + surface.frame.y * surface.size;
            Point a = c + ((-surface.frame.y * 3/2 - surface.frame.x * sqrt(3)/2) * surface.size);
            Point b = c + ((-surface.frame.y * 3/2 + surface.frame.x * sqrt(3)/2) * surface.size);
            double alpha = ray.d.cross(b-c).dot(ray.e-c) / ray.d.cross(b-c).dot(a-c);
            double beta = (ray.e-c).cross(a-c).dot(ray.d) / ray.d.cross(b-c).dot(a-c);
            if (alpha<0 || beta<0 || alpha+beta>1) {
                continue;
            }
            if (ray.valid(t) && t < t_closest) {
                t_closest = t;
                Direction normal = determinant < 0 ? surface.frame.z : -surface.frame.z;
                Frame frame = Frame(o:point, z:surface.frame.z);
                intersection = Intersection(frame, surface, t);
            }
        }
    }
    return intersection;
}

// Computes irradiance (as RGBColor) from scene along ray
RGBColor irradiance(Scene scene, Ray ray, [int depth=0]) {
    if (depth > irradianceMaxDepth) {
        return RGBColor.black();
    }

    Intersection intersection = intersectRayScene(scene, ray);
    if (intersection != null) {
        RGBColor color = scene.ambientIntensity * intersection.material.kd;
        Direction viewingDirection = Direction.fromPoints(ray.e, intersection.frame.o);
        for (Light light in scene.lights) {
            Direction lightDirection;
            Ray shadowRay;
            if (light.type == 'point') { 
                shadowRay = Ray.fromPoints(intersection.o, light.frame.o);
                lightDirection = Direction.fromPoints(light.frame.o, intersection.frame.o);
            } else if (light.type == 'direction') {
                shadowRay = Ray(intersection.o, -light.frame.z);
                lightDirection = light.frame.z;
            }
            Intersection obstruction = intersectRayScene(scene, shadowRay);
            if (obstruction != null) {
                // possible todo: handle refraction or transparency, so that only part of the light is obstructed?
                continue;
            }
            // the cos of the angle between normal and light direction
            // negative if normal and light forms an acute angle
            double lightNormal = intersection.n.dot(-lightDirection);
            double viewingNormal = intersection.n.dot(-viewingDirection);
            if (lightNormal * viewingNormal > 0) {
                // light reflects only if light and eye are on the same side of the surface
                RGBColor response = light.intensity;
                if (light.type == 'point') {
                    response /= (light.frame.o-intersection.frame.o).lengthSquared;
                }
                // calculate diffuse light
                var diffuse = response * intersection.material.kd * lightNormal;
                color += diffuse;
                // calculate specular light
                Direction bisector = Direction.fromVector(-lightDirection-viewingDirection);
                var specular = response
                        * intersection.material.ks
                        * pow(max(0, intersection.n.dot(bisector)),
                                intersection.material.n)
                        * lightNormal;
                color += specular;
            }
        }
        // calculate reflection
        if (!intersection.material.kr.isBlack) {
            Ray reflectionRay = Ray(intersection.frame.o,
                    Direction.fromVector(-intersection.n * 2 * ray.d.dot(intersection.n) + ray.d));
            RGBColor reflection = intersection.material.kr * irradiance(scene, reflectionRay, depth+1);
            color += reflection;
        }
        // calculate refraction
        if (!intersection.material.kt.isBlack) {
            bool into = intersection.n.dot(viewingDirection) < 0;
            double ratio = into ? 1/intersection.material.nr : intersection.material.nr; 
            Vector horizontal = intersection.n.cross(viewingDirection).cross(intersection.n) * ratio;
            Vector vertical = intersection.n * sqrt(1-pow(ratio * intersection.n.cross(viewingDirection).lengthSquared, 2));
            vertical = into ? -vertical : vertical;
            Ray refractionRay = Ray(intersection.frame.o, Direction.fromVector(horizontal+vertical));
            RGBColor refraction = intersection.material.kt * irradiance(scene, refractionRay, depth+1);
            color += refraction;
        }
        return color;
    }
    else {
        return scene.backgroundIntensity;
    }
}

// Computes image of scene using basic Whitted raytracer.
Image raytraceScene(Scene scene) {
    var image = Image(scene.resolution.width, scene.resolution.height);
    var camera = scene.camera;

    for (var i=0; i<image.height; i++) {
        for (var j=0; j<image.width; j++) {
            RGBColor pixelColor = RGBColor.black();

            int ps = sqrt(scene.pixelSamples).toInt();
            // sample subpixels
            for (var ii=0; ii<ps; ii++) {
                for (var jj=0; jj<ps; jj++) {
                    // calculate offset from center, range from -0.5 to 0.5 of sensor width/height respectively
                    double h = ((j+(jj+0.5)/ps)/image.width-0.5) * (camera.sensorSize.width);
                    double v = -((i+(ii+0.5)/ps)/image.height-0.5) * (camera.sensorSize.height);

                    // get ray
                    Point pixelPoint = camera.frame.l2wPoint(Point(h, v, -camera.sensorDistance));
                    Ray ray = Ray(camera.eye, Direction.fromPoints(camera.eye, pixelPoint));

                    // do stuff here with pixel
                    pixelColor += irradiance(scene, ray);
                }
            }
            pixelColor /= ps*ps; // average the result
            image.setPixelSafe(j, i, pixelColor);
        }
    }
    return image;
}

void main() {
    // Make sure images folder exists, because this is where all generated images will be saved
    Directory('images').createSync();

    for(String scenePath in scenePaths) {
        // Determine where to write the rendered image.
        // NOTE: the following line is not safe, but it is fine for this project.
        var ppmPath = scenePath.replaceAll('.json', '.ppm').replaceAll('scenes/', 'images/');

        print('Scene: $scenePath');
        print('    output image: $ppmPath');
        print('    loading...');
        var loader = JsonLoader(path:scenePath);    // load json file
        var scene = Scene.fromJson(loader);         // parse json file as Scene

        // override scene's resolution
        if(overrideResolution != null)
            scene.resolution = overrideResolution;

        print('    tracing rays...');
        Stopwatch watch = Stopwatch()..start();             // create Stopwatch, then start it (NOTE: keep the two ..)
        var image = raytraceScene(scene);                   // raytrace the scene
        var seconds = watch.elapsedMilliseconds / 1000.0;   // determine elapsed time in seconds

        image.saveImage(ppmPath, asBinary:writeImageInBinary);  // write raytraced image to PPM file

        // report details to console
        print('    time:  $seconds seconds');               // note: includes time for saving file
    }
}
