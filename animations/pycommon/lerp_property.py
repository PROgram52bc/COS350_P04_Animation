from .animated_property import AnimatedProperty

class LerpValue(AnimatedProperty):
    """ A linearly interpolated value """

    def __init__(self, start, increment, max_frame=None):
        """

        :start: starting value
        :increment: the value to increment for each frame
        :max_frame: maximum frame number

        """
        super().__init__()
        self.register_child_property('start', start)
        self.register_child_property('increment', increment)

        @self.dynamic_property('value', start)
        def update(property_frame):
            return property_frame.props['value'] + property_frame.props['increment']

        if max_frame is not None:
            self.register_terminator(lambda pf: pf.frame_num >= max_frame)

    @classmethod
    def from_interval(cls, start, end, num_frames):
        """
        :start: starting value
        :end: the value to increment for each frame
        :num_frames: number of frame to fill in between start and end
        """
        interval = end - start
        increment = interval / (num_frames - 1)
        return cls(start, increment, num_frames)

    def get_frame_data(self, property_frame):
        return property_frame.props['value']


class LerpPoint(LerpValue):

    """ A linearly interpolated point in 3D, represented by a list with 3 numbers """

    def __init__(self, start, direction, max_frame=None):
        super().__init__(start, direction, max_frame)

    def get_frame_data(self, property_frame):
        return property_frame.props['value'].toList() 
