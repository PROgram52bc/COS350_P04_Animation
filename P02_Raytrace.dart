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

const int irradianceMaxDepth = 3;

// Comment out lines below to prevent re-rendering every scene.
// If you create a new scene file, add it to the list below.
// NOTE: **BEFORE** you submit your solution, uncomment all lines, so
//       your code will render all the scenes!
List<String> scenePaths = [
    'scenes/P02_00_sphere.json',
    'scenes/P02_01_sphere_ka.json',
    'scenes/P02_02_sphere_room.json',
    'scenes/P02_03_quad.json',
    'scenes/P02_04_quad_room.json',
    'scenes/P02_05_ball_on_plane.json',
    'scenes/P02_06_balls_on_plane.json',
    'scenes/P02_07_reflection.json',
    'scenes/P02_08_aa.json',
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
        for (Light light in scene.lights) {
            Ray shadowRay = Ray.fromPoints(intersection.o, light.frame.o);
            Intersection obstruction = intersectRayScene(scene, shadowRay);
            if (obstruction != null) {
                // TODO: handle refraction or transparency, so that only part of the light is obstructed?
                continue;
            }
            Direction lightDirection = Direction.fromPoints(light.frame.o, intersection.frame.o);
            Direction viewingDirection = Direction.fromPoints(ray.e, intersection.frame.o);
            // the cos of the angle between normal and light direction
            // negative if normal and light forms an acute angle
            double normalFraction = intersection.n.dot(-lightDirection);
            // TODO: add attenuation to light property
            double attenuation = 1;
            RGBColor response = light.intensity * attenuation / (light.frame.o-intersection.frame.o).lengthSquared;
            // calculate diffuse light
            var diffuse = response * intersection.material.kd * normalFraction;
            color += diffuse;
            // calculate specular light
            Direction bisector = Direction.fromVector(-lightDirection-viewingDirection);
            var specular = response
                    * intersection.material.ks
                    * pow(max(0, intersection.n.dot(bisector)),
                            intersection.material.n)
                    * normalFraction;
            color += specular;
        }
        // calculate reflection
        Ray reflectionRay = Ray(intersection.frame.o,
                Direction.fromVector(-intersection.n * 2 * ray.d.dot(intersection.n) + ray.d));
        RGBColor reflection = intersection.material.kr * irradiance(scene, reflectionRay, depth+1);
        color += reflection;
        // TODO: calculate refraction
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

    for (var row=0; row<image.height; row++) {
        for (var col=0; col<image.width; col++) {
            var horizontalOffset = ((col+0.5)/image.width-0.5) * (camera.sensorSize.width);
            var verticalOffset = -((row+0.5)/image.height-0.5) * (camera.sensorSize.height);
            Point pixelPoint = camera.frame.l2wPoint(
                    Point(horizontalOffset, verticalOffset, -camera.sensorDistance));
            Ray ray = Ray(camera.eye, Direction.fromPoints(camera.eye, pixelPoint));
            // do stuff here with pixel
            RGBColor pixelColor = irradiance(scene, ray);
            image.setPixelSafe(col, row, pixelColor);
        }
    }

    // if no anti-aliasing
    //     foreach image row (scene.resolution.height)
    //         foreach pixel in row (scene.resolution.width)
    //             compute ray-camera parameters (u,v) for pixel
    //             compute camera ray
    //             set pixel to color raytraced with ray (`irradiance`)
    // else
    //     foreach image row
    //         foreach pixel in row
    //             init accumulated color
    //             foreach sample in y
    //                 foreach sample in x
    //                     compute ray-camera parameters
    //                     computer camera ray
    //                     accumulate color raytraced with ray
    //             set pixel to average of accum color (scale by number of samples)
    // return rendered image



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
