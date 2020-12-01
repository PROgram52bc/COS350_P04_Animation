from .animated_property import AnimatedProperty, LerpPoint
from .maths import Point


class PlanetScene(AnimatedProperty):
    def __init__(self, cameraStartPoint, cameraEndPoint, **kwargs):
        super().__init__(**kwargs)
        self.cameraEye = LerpPoint(start=cameraStartPoint, end=cameraEndPoint, speed=self.speed)

    def next_frame(self):
        pass

    def __iter__(self):
        cameraEye = iter(self.cameraEye)
        for _ in range(1000):  # maximum 1000 frames
            yield {
                "camera": {"eye": next(cameraEye), "target": [20, 0, 0]},
                "surfaces": [
                    {
                        "frame": {"o": [-15, 3, 0]},
                        "size": 0.5,
                        "material": {
                            "kd": [0.11, 0.11, 0.11]
                        }
                    },
                    {
                        "frame": {"o": [-12, 3, 0]},
                        "size": 1.3,
                        "material": {
                            "kd": [0.9, 0.9, 0.9]
                        }
                    },
                    {
                        "frame": {"o": [-9, 3, 0]},
                        "size": 1.3,
                        "material": {
                            "kd": [0.19, 0.42, 0.41]
                        }
                    },
                    {
                        "frame": {"o": [-4, 3, 0]},
                        "size": 0.7,
                        "material": {
                            "kd": [0.6, 0.24, 0]
                        }
                    },
                    {
                        "frame": {"o": [7, 3, 0]},
                        "size": 8,
                        "material": {
                            "kd": [0.69, 0.5, 0.21]
                        }
                    },
                    {
                        "frame": {"o": [22, 3, 0]},
                        "size": 6,
                        "material": {
                            "kd": [0.69, 0.56, 0.21]
                        }
                    },
                    {
                        "frame": {"o": [35, 3, 0]},
                        "size": 5,
                        "material": {
                            "kd": [0.34, 0.5, 0.67]
                        }
                    },
                    {
                        "frame": {"o": [46, 3, 0]},
                        "size": 5,
                        "material": {
                            "kd": [0.21, 0.41, 0.59]
                        }
                    }
                ],
                "lights": [
                    {
                        "type": "direction",
                        "frame": {"z": [-1, -1, 0]},
                        "intensity": [2, 2, 2]
                    }
                ]
            }
