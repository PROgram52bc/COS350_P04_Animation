import math

class Point(object):

    """A point or vector in 3D"""

    def __init__(self, x, y, z):
        """TODO: to be defined.

        :x: TODO
        :y: TODO
        :z: TODO

        """
        try:
            int(x)
            int(y)
            int(z)
        except ValueError as e:
            raise ValueError(f"Invalid parameter to initialize a point: {e}")
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @property
    def lengthSquared(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    @property
    def length(self):
        return math.sqrt(self.lengthSquared)

    @classmethod
    def fromList(cls, l):
        """construct a point object from list

        :l: TODO
        :returns: TODO

        """
        if len(l) != 3:
            raise ValueError(
                    f"List passed in to a point constructor must be 3 elements: {l}")
        return cls(*l)

    def toList(self):
        """TODO: Docstring for toList.
        :returns: TODO

        """
        return [self._x, self._y, self._z]

    def __mul__(self, other):
        """multiplication operator

        :other: either a number or a point
        :returns: a point

        """
        if isinstance(other, (float, int)):
            return Point(self.x * other,
                         self.y * other,
                         self.z * other)
        elif isinstance(other, Point):
            return Point(self.x * other.x,
                         self.y * other.y,
                         self.z * other.z)
        else:
            raise ValueError(f"Unknown type for other: {type(other)}")

    def __truediv__(self, other):
        if isinstance(other, (float, int)):
            return Point(self.x / other,
                         self.y / other,
                         self.z / other)
        elif isinstance(other, Point):
            return Point(self.x / other.x,
                         self.y / other.y,
                         self.z / other.z)
        else:
            raise ValueError(f"Unknown type for other: {type(other)}")

    def __floordiv__(self, other):
        if isinstance(other, (float, int)):
            return Point(self.x // other,
                         self.y // other,
                         self.z // other)
        elif isinstance(other, Point):
            return Point(self.x // other.x,
                         self.y // other.y,
                         self.z // other.z)
        else:
            raise ValueError(f"Unknown type for other: {type(other)}")



    def __sub__(self, other):
        """minus operator

        :other: either a number or a point
        :returns: a point

        """
        if isinstance(other, Point):
            return Point(self._x - other._x,
                         self._y - other._y,
                         self._z - other._z)
        elif isinstance(other, (float, int)):
            return Point(self._x - other,
                         self._y - other,
                         self._z - other)
        else:
            raise ValueError(f"Unknown type for other: {type(other)}")

    def __add__(self, other):
        return self - (other * -1)

    def __neg__(self):
        return self * -1

    def __repr__(self):
        return f"Point({self._x}, {self._y}, {self._z})"
