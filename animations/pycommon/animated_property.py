import sys
from .maths import Point

class AnimatedProperty:
    def __init__(self, **kwargs):
        """

        :speed: control the speed of the animation, subclasses should use this variable in its frame generation
        :returns: None

        """
        self.speed = kwargs.get('speed', 1)

    def __iter__(self):
        """
        :returns: self

        """
        raise NotImplementedError(
            "Abstract base class AnimatedProperty does not implement the __iter__ method")


class LerpValue(AnimatedProperty):
    """ A linearly interpolated value """

    def __init__(self, **kwargs):
        """TODO: Docstring for __init__.

        :start: starting value
        :end: ending value
        :infinite: value will keep incrementing forever if true

        """
        super().__init__(**kwargs)
        self.start = kwargs.get('start', 0)
        self.end = kwargs.get('end', 1)
        self.infinite = kwargs.get('infinite', False)
        self.increment = (1 if self.end > self.start else -1) * self.speed

    def __iter__(self):
        """
        :returns: an iterator from start to end

        """
        value = self.start
        while True:
            if not self.infinite:
                # check for terminating condition
                if ((self.increment < 0 and value < self.end) or
                        (self.increment > 0 and value > self.end)):
                    return
            yield value
            value += self.increment


class LerpPoint(AnimatedProperty):

    """ A linearly interpolated point in 3D, represented by a list with 3 numbers """

    def __init__(self, **kwargs):
        """
        :start: a Point object
        :end: a Point object

        """
        super().__init__(**kwargs)
        self.start = Point.fromList(kwargs.get('start', [0, 0, 0]))
        self.end = Point.fromList(kwargs.get('end', [1, 0, 0]))
        self.infinite = kwargs.get('infinite', False)
        self.increment = self.end - self.start

        sei = zip(self.start.toList(), self.end.toList(), self.increment.toList())

        self.lerp_xyz = [ LerpValue(start=start, end=end, infinite=self.infinite, speed=(
            self.speed * abs(increment) / self.increment.length)) for start, end, increment in sei ]

    def __iter__(self):
        its = [ iter(lerp_value) for lerp_value in self.lerp_xyz ]
        while True:
            try:
                yield [ next(it) for it in its ]
            except StopIteration:
                return

