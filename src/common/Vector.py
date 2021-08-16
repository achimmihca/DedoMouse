# original from https://github.com/allelos/vectors/blob/master/vectors/vectors.py
from __future__ import annotations
from __future__ import division
from functools import reduce
import math
from typing import Any, List, Tuple

class Vector:
    """Vector class: Representing a vector in 3D space.
    Can accept formats of:
    Cartesian coordinates in the x, y, z space (regular initialization).
    Spherical coordinates in the r, theta, phi space (spherical class method).
    Cylindrical coordinates in the r, theta, z space (cylindrical class method).
    """
    def __init__(self, x: float, y: float, z: float = 0) -> None:
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def distance(vec1: Vector, vec2: Vector) -> float:
        """ Calculates distance between two vectors. """
        return vec2.subtract(vec1).magnitude()

    @staticmethod
    def from_tuple2(t: Tuple[float, float]) -> Vector:
        """ Create a Vector from a tuple in the form (x, y). """
        return Vector(t[0], t[1])

    @staticmethod
    def from_tuple3(t: Tuple[float, float, float]) -> Vector:
        """ Create a Vector from a tuple in the form (x, y, z). """
        return Vector(t[0], t[1], t[2])

    @staticmethod
    def from_xy(other: Any) -> Vector:
        """ Create a Vector from an object with properties x and y. """
        return Vector(other.x, other.y)
    
    @staticmethod
    def from_xyz(other: Any) -> Vector:
        """ Create a Vector from an object with properties x and y and z. """
        return Vector(other.x, other.y, other.z)

    @staticmethod
    def from_list(l: List[float]) -> Vector:
        """ Create a 2D or 3D Vector from a list in the form [x, y] or [x, y, z] """
        if len(l) == 3:
            x, y, z = map(float, l)
            return Vector(x, y, z)
        elif len(l) == 2:
            x, y = map(float, l)
            return Vector(x, y)
        else:
            raise AttributeError("List must have 2 or 3 elements")

    @staticmethod
    def spherical(mag: float, theta: float, phi: float=0) -> Vector:
        """ Create a Vector from spherical coordinates. """
        return Vector(
            mag * math.sin(phi) * math.cos(theta),  # X
            mag * math.sin(phi) * math.sin(theta),  # Y
            mag * math.cos(phi)  # Z
        )

    @staticmethod
    def cylindrical(mag: float, theta: float, z: float=0) -> Vector:
        """ Create a Vector instance from cylindircal coordinates. """
        return Vector(
            mag * math.cos(theta),  # X
            mag * math.sin(theta),  # Y
            z  # Z
        )

    def __repr__(self) -> str:
        """ Returns a string representation of the object. """
        return '{0}({1}, {2}, {3})'.format(
            self.__class__.__name__,
            self.x,
            self.y,
            self.z
        )

    def __sub__(self, vec: Vector) -> Vector:
        """ Returns a new Vector that is this Vector minus the other Vector (component-wise). """
        return self.subtract(vec)

    def __add__(self, vec: Vector) -> Vector:
        """ Returns a new Vector that is this Vector plus the other Vector (component-wise). """
        return self.add(vec)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Vector) and
            self.x == other.x and
            self.y == other.y and
            self.z == other.z
        )

    def __mul__(self, vec: Vector) -> Vector:
        """ Return a new Vector that is the cross product of this and the other vectors. """
        return self.cross(vec)

    def __str__(self) -> str:
        """ Returns a string representation of this Vector. """
        return "Vector({0}, {1}, {2})".format(self.x, self.y, self.z)

    def __round__(self, n: int=None) -> Vector:
        """ Rounds this Vector to n decimal places (component-wise). """
        if n is not None:
            return Vector(round(self.x, n), round(self.y, n), round(self.z, n))
        return Vector(round(self.x), round(self.y), round(self.z))

    def to_int_vector(self) -> Vector:
        """ Cast the values of this Vector to integers (component-wise). """
        return Vector(int(self.x), int(self.y), int(self.z))

    def to_list(self) -> List[float]:
        """ Returns a new list in the form [x,y,z]. """
        return [self.x, self.y, self.z]
        
    def subtract(self, vec: Vector) -> Vector:
        """ Returns a new Vector that is this Vector minus the other Vector (component-wise). """
        return Vector(self.x - vec.x, self.y - vec.y, self.z - vec.z)

    def subtract_scalar(self, f: float) -> Vector:
        """ Returns a new Vector that is this Vector minus the scalar (component-wise). """
        return Vector(self.x - f, self.y - f, self.z - f)

    def add(self, pt: Vector) -> Vector:
        """ Returns a new Vector that is this Vector plus the other Vector (component-wise). """
        return Vector(pt.x + self.x, pt.y + self.y, pt.z + self.z)

    def add_scalar(self, f: float) -> Vector:
        """ Returns a new Vector that is this Vector plus the scalar (component-wise). """
        return Vector(self.x + f, self.y + f, self.z + f)

    def scale(self, vec: Vector) -> Vector:
        """ Returns a new Vector from component-wise multiplication. """
        return Vector(self.x * vec.x, self.y * vec.y, self.z * vec.z)

    def scale_by_scalar(self, factor: float) -> Vector:
        """Returns a new Vector from component-wise multiplication with a float"""
        return Vector(self.x * factor, self.y * factor, self.z * factor)

    def magnitude(self) -> float:
        """ Returns the magnitude of the Vector."""
        return math.sqrt( self.x * self.x
            + self.y * self.y
            + self.z * self.z )

    def dot(self, vec: Vector, theta_in_degrees: float = None) -> float:
        """ Returns a new Vector that is the dot product of two vectors.
        If theta is given then the dot product is computed as
        v1*v1 = |v1||v2|cos(theta). Argument theta
        is measured in degrees.
        """
        if theta_in_degrees is not None:
            return (self.magnitude() * vec.magnitude() *
                    math.degrees(math.cos(theta_in_degrees)))
        return (reduce(lambda x, y: x + y,
                [x * vec.to_list()[i] for i, x in enumerate(self.to_list())]))

    def cross(self, vec: Vector) -> Vector:
        """ Returns a new Vector as the cross product of two vectors"""
        return Vector((self.y * vec.z - self.z * vec.y),
                      (self.z * vec.x - self.x * vec.z),
                      (self.x * vec.y - self.y * vec.x))

    def unit(self) -> Vector:
        """ Returns a new Vector that is the unit vector (with magnitude 1). """
        magnitude = self.magnitude()
        return Vector(
            (self.x / magnitude),
            (self.y / magnitude),
            (self.z / magnitude)
        )

    def angle(self, vec: Vector) -> float:
        """ Returns the angle between two vectors in degrees."""
        return math.degrees(
            math.acos(
                self.dot(vec) /
                (self.magnitude() * vec.magnitude())
            )
        )

    def is_parallel(self, vec: Vector) -> bool:
        """ Returns True if vectors are parallel to each other."""
        if self.cross(vec).magnitude() == 0:
            return True
        return False

    def is_perpendicular(self, vec: Vector) -> bool:
        """ Returns True if vectors are perpendicular to each other. """
        if self.dot(vec) == 0:
            return True
        return False

    def is_non_parallel(self, vec: Vector) -> bool:
        """ Returns True if vectors are non-parallel.
        Non-parallel vectors are vectors which are neither parallel
        nor perpendicular to each other.
        """
        if (self.is_parallel(vec) is not True and
                self.is_perpendicular(vec) is not True):
            return True
        return False

    def rotate(self, angle_in_radians: float, axis: Tuple[float, float, float]=(0, 0, 1)) -> Vector:
        """ Returns the rotated vector. Assumes angle is in radians. """
        if not all(isinstance(a, int) for a in axis):
            raise ValueError
        x, y, z = self.x, self.y, self.z

        # Z axis rotation
        if(axis[2]):
            x = (self.x * math.cos(angle_in_radians) - self.y * math.sin(angle_in_radians))
            y = (self.x * math.sin(angle_in_radians) + self.y * math.cos(angle_in_radians))

        # Y axis rotation
        if(axis[1]):
            x = self.x * math.cos(angle_in_radians) + self.z * math.sin(angle_in_radians)
            z = -self.x * math.sin(angle_in_radians) + self.z * math.cos(angle_in_radians)

        # X axis rotation
        if(axis[0]):
            y = self.y * math.cos(angle_in_radians) - self.z * math.sin(angle_in_radians)
            z = self.y * math.sin(angle_in_radians) + self.z * math.cos(angle_in_radians)

        return Vector(x, y, z)

    def to_tuple_2(self) -> Tuple[float, float]:
        """ Returns a tuple in the form (x, y) """
        return (self.x, self.y)

    def to_tuple_3(self) -> Tuple[float, float, float]:
        """ Returns a tuple in the form (x, y, z) """
        return (self.x, self.y, self.z)