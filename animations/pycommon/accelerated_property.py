from .animated_property import AnimatedProperty
from .lerp_property import LerpPoint, LerpValue


class AcceleratedValue(AnimatedProperty):
    """ An accelerated value """

    def __init__(
            self,
            start_value,
            start_velocity,
            acceleration,
            max_frame=None):
        """

        :start_value: starting value
        :start_velocity: starting velocity
        :acceleration: the constant acceleration
        :max_frame: maximum frame number

        """
        super().__init__()
        self.register_child_property(
            'velocity',
            LerpValue(
                start_velocity,
                acceleration,
                max_frame))

        @self.dynamic_property('value', start_value)
        def update(property_frame):
            return property_frame.props['value'] + \
                property_frame.props['velocity']

        if max_frame is not None:
            self.register_terminator(lambda pf: pf.frame_num >= max_frame)

    def get_frame_data(self, property_frame):
        return property_frame.props['value']


class AcceleratedPoint(AcceleratedValue):
    """ An accelerated Point """

    def __init__(
            self,
            start_point,
            start_velocity,
            acceleration,
            max_frame=None):
        """

        :start_point: starting value as a point
        :start_velocity: starting velocity as a point
        :acceleration: the constant acceleration as a point
        :max_frame: maximum frame number

        """
        super().__init__(start_point, start_velocity, acceleration, max_frame=None)

    def get_frame_data(self, property_frame):
        return property_frame.props['value'].toList()

