from ..pycommon.animated_property import AnimatedProperty
from ..pycommon.lerp_property import LerpPoint
from ..pycommon.maths import Point


class MovingCamera(AnimatedProperty):
    def __init__(self):
        super().__init__()

        self.register_child_property(
            'cameraEye', LerpPoint.from_interval(
                start=Point(
                    22, 0, 50), end=Point(
                    22, 20, 0), num_frames=500))
        self.append_child_property(
            'cameraEye', LerpPoint.from_interval(
                start=Point(
                    22, 20, 0), end=Point(
                    22, 0, -50), num_frames=500))
        self.register_child_property('cameraTarget', LerpPoint.from_interval(
            start=Point(-20, 0, 0), end=Point(40, 0, 0), num_frames=1000))

    def get_frame_data(self, property_frame):
        return {
            "camera": { "eye": property_frame.props['cameraEye'].get_frame_data(), 
                "target": property_frame.props['cameraTarget'].get_frame_data() },
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
