from ..pycommon.animated_property import AnimatedProperty
from ..pycommon.bouncing_point_property import BouncingPoint
from ..pycommon.maths import Point
import random


def get_small_balls(count):
    balls = []
    for _ in range(count):
        balls.append(
            {
                "size": 0.2,
                "frame": {"o": [random.randint(-count, count), -0.8, random.randint(-count, count)]},
                "material": {
                    "kd": [random.random(),
                           random.random(),
                           random.random()],
                    "ks": [random.random(),
                           random.random(),
                           random.random()]
                }
            }
        )
    return balls


class BouncingBalls(AnimatedProperty):

    def __init__(self):
        super().__init__()
        self.register_child_property('ballPosition', BouncingPoint(start=Point(0, 10, 0)))
        

    def get_frame_data(self, property_frame):
        return {
            "camera": {"eye": [0, 2, -10]},
            "backgroundIntensity": [0.5, 0.8, 0.9],
            "surfaces": [
                {
                    "size": 1000,
                    "frame": {
                        "o": [0, -1001, 0]
                    },
                    "material": {"kd": [0.5, 1, 0], "ks": [0, 0, 0], "n": 100}
                },
                {
                    "size": 1,
                    "frame": {"o": property_frame.props['ballPosition'].get_frame_data()},
                    "material": {
                        "kd": [0, 0, 0],
                        "ks": [0, 0, 0],
                        "kr": [0.1, 0.1, 0.1],
                        "kt": [0.9, 0.9, 0.9],
                        "nr": 1.6
                    }
                },
                {
                    "size": 1,
                    "frame": {"o": [3, 0, 0]},
                    "material": {
                        "kd": [0, 0, 0],
                        "ks": [0, 0, 0],
                        "kr": [0.9, 0.9, 0.9]
                    }
                },
                {
                    "size": 1,
                    "frame": {"o": [-3, 0, 0]},
                    "material": {
                        "kd": [0.5, 0.1, 0.2],
                        "ks": [0.5, 0.1, 0.2]
                    }
                },
                *get_small_balls(10)
            ],
            "lights": [
                {"type": "direction", "frame": {"z": [4, -10, 0]}, "intensity": [0.5, 0.5, 0.5]}
            ]
        }
