# Scene Generator and Ray Tracing Project

## Design

The `AnimatedProperty` class is the main entrance to defining an animation.
It largely relies on Python's iterator/iterable interface, and the design is that once an `AnimatedProperty` object is set up properly, it can be iterated using a `for` loop to obtain the scene data for each frame.

## Features

### Performance via parallelization

#### Sample output
As shown below, the rendering is taking place in parallel.
```bash
...
Scene: scenes/moving_camera/scene_data/0187.json...
Scene: scenes/moving_camera/scene_data/0920.json...
(97/1000) scenes/moving_camera/scene_images/0995.ppm done!
(98/1000) scenes/moving_camera/scene_images/0287.ppm done!
(99/1000) scenes/moving_camera/scene_images/0659.ppm done!
Scene: scenes/moving_camera/scene_data/0613.json...
Scene: scenes/moving_camera/scene_data/0623.json...
(100/1000) scenes/moving_camera/scene_images/0521.ppm done!
(101/1000) scenes/moving_camera/scene_images/0610.ppm done!
Scene: scenes/moving_camera/scene_data/0894.json...
Scene: scenes/moving_camera/scene_data/0463.json...
Scene: scenes/moving_camera/scene_data/0131.json...
(102/1000) scenes/moving_camera/scene_images/0229.ppm done!
Scene: scenes/moving_camera/scene_data/0237.json...
(103/1000) scenes/moving_camera/scene_images/0919.ppm done!
(104/1000) scenes/moving_camera/scene_images/0988.ppm done!
Scene: scenes/moving_camera/scene_data/0461.json...
(105/1000) scenes/moving_camera/scene_images/0004.ppm done!
Scene: scenes/moving_camera/scene_data/0729.json...
(106/1000) scenes/moving_camera/scene_images/0060.ppm done!
(107/1000) scenes/moving_camera/scene_images/0343.ppm done!
Scene: scenes/moving_camera/scene_data/0881.json...
...
```
```bash
$ top
...
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
10436 hdeng     20   0  446852 380220 335856 S 466.9   0.3  19:13.38 dart
...
```

### Animator-Driven / Key-Frame Motion

#### Moving Camera

In this demonstration, several `LerpPoint`s are evaluated in parallel or stringed together to represent some interesting movements of camera location and target.

Code fragment
```python
self.register_child_property('cameraEye', LerpPoint.from_interval(
			start=Point(22, 0, 50), end=Point(22, 20, 0), num_frames=500))
self.append_child_property('cameraEye', LerpPoint.from_interval(
			start=Point(22, 20, 0), end=Point(22, 0, -50), num_frames=500))
self.register_child_property('cameraTarget', LerpPoint.from_interval(
			start=Point(-20, 0, 0), end=Point(40, 0, 0), num_frames=1000))
```

To generate the video
```bash
./build.sh animations/moving_camera.json
```
![moving_camera](assets/moving_camera.gif)
