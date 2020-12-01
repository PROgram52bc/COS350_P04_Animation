import sys
import os
import json

from animations.pycommon.maths import Point
from animations.scenes.moving_camera import MovingCamera
from animations.scenes.bouncing_balls import BouncingBalls

scenes = {
        'MovingCamera': MovingCamera,
        'BouncingBalls': BouncingBalls,
}

def usage():
    print(f"Usage: python3 {sys.argv[0]} [frames.json] [output_dir]")

if len(sys.argv) != 3:
    usage()
    exit(-1)

# TODO: Maybe eliminate the frame_file since there is a lot of data files around <2020-12-01, David Deng> #
frame_file, out_dir = sys.argv[1:]
os.makedirs(out_dir, exist_ok=True)

with open(frame_file) as f:
    frame_data = json.load(f)

scene_name = frame_data['scene'] # the name of the scene
params = frame_data['params'] # should be a dictionary, passed as keyword argument for initializing scene
Scene = scenes[scene_name]
scene = Scene(**params)
it = iter(scene)
for i, frame in enumerate(scene):
    out_file = f"{i:04}.json"
    out_name = os.path.join(out_dir, out_file)
    with open(out_name, "w") as f:
        json.dump(frame.get_frame_data(), f)
    print(f"Written frame data to {out_name}")


