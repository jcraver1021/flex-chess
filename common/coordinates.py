#   Copyright 2019 James Craver
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""Module for coordinates to address points on a board"""
from typing import Any, Iterable


class Point(tuple):
    """A point on a cartesian plane of n-dimensions."""
    @classmethod
    def zero(cls, dimensions):
        # type: (int) -> Point
        """Construct a zero point in the given dimension.

        Args:
            dimensions (int): dimension of the point
        Return:
            A zero point in the given dimension
        """
        return Point(*tuple(0 for _ in range(dimensions)))

    def __new__(cls, *x):
        # type: (type, Iterable[Any]) -> Point
        """Construct a point with the given values as components.

        Roughly speaking, a Point is similar to a tuple of the same values.
        For example, Point(1, 2) ~ (1, 2)
        The dimension of the point will be equal to the number of components given.

        Args:
            *x: components of the point
        Return:
            The point described by the input
        """
        return tuple.__new__(Point, x)

    def _check_size(self, other):
        # type: (Point) -> None
        if len(self) != len(other):
            raise ValueError('Dimensions do not match ({}, {})'.format(len(self), len(other)))

    def __add__(self, other):
        # type: (Point) -> Point
        """Add two points.

        Args:
            other: another Point
        Return:
            A Point, where each component is the sum of that component
            in the first and second Points
        """
        self._check_size(other)
        return Point(*tuple(x + y for x, y in zip(self, other)))

    def __le__(self, other):
        # type: (Point) -> bool
        """Test if each component is less than or equal the corresponding component in the other.

        Note this constitutes a partial ordering, as a <= b and b <= a may both be false
        for certain Points

        Args:
            other: another Point
        Return:
            True iff each component of the first is less than the corresponding
            component of the second
        """
        self._check_size(other)
        return all(map(lambda pair: pair[0] <= pair[1], zip(self, other)))

    def __lt__(self, other):
        # type: (Point) -> bool
        """Test if each component is less than the corresponding component in the other point.

        Note this constitutes a partial ordering, as a < b and b < a may both be false
        for certain Points

        Args:
            other: another Point
        Return:
            True iff each component of the first is less than the corresponding
            component of the second
        """
        self._check_size(other)
        return all(map(lambda pair: pair[0] < pair[1], zip(self, other)))
