from .accelerated_property import AcceleratedPoint
from .animated_property import AnimatedProperty
from .maths import Point

class BouncingPoint(AnimatedProperty):
    """ start from 0 velocity, """

    def __init__(
        self,
        start,
        start_velocity=Point(0, 0, 0),
        touch_floor=lambda p: p.y < 0,
        acceleration=Point(0, -1, 0),
        bouncing_repetition=5,
        bouncing_velocity_loss=0.1):
        """
        :start: a point object
        :start_velocity: a point object
        :touch_floor: a function taking a point as parameter and returns a boolean indicating whether the point touched floor, upon which the velocity is to be reversed.
        :acceleration: the acceleration, expressed as a point
        :bouncing_repetition: specifies the number of times to bounce to the floor
        :bouncing_velocity_loss: the fraction of velocity to lose upon each bounce
        """
        super().__init__()
        animated_point = AcceleratedPoint(start_point=start, start_velocity=start_velocity, acceleration=acceleration)

        self.register_child_property('value', animated_point)

        @animated_point.terminator()
        def terminate(property_frame):
            point = property_frame.props['value']
            return touch_floor(point)

        @animated_point.updater()
        def update(property_states, property_frame):
            pass


    def get_frame_data(self, property_frame):
        return property_frame.props['value'].get_frame_data()
