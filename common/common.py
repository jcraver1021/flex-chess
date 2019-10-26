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
"""General-purpose objects used across FlexChess."""
from functools import reduce
from itertools import islice, repeat
from typing import Any, Iterable, Optional


class Point(tuple):
    """A point on a cartesian plane of n-dimensions."""
    @classmethod
    def zero(cls, dimensions: int) -> 'Point':
        """Construct a zero point in the given dimension.

        Args:
            dimensions (int): Dimension of the point.
        Return:
            A zero point in the given dimension.
        """
        return Point(*tuple(0 for _ in range(dimensions)))

    def __new__(cls, *x: int) -> 'Point':
        """Construct a point with the given values as components.

        Roughly speaking, a Point is similar to a tuple of the same values.
        For example, Point(1, 2) ~ (1, 2)
        The dimension of the point will be equal to the number of components given.

        Args:
            *x: Components of the point
        Return:
            The point described by the input.
        """
        return tuple.__new__(Point, x)

    def _check_size(self, other: 'Point'):
        if len(self) != len(other):
            raise ValueError('Dimensions do not match ({}, {})'.format(len(self), len(other)))

    def __add__(self, other: 'Point') -> 'Point':
        """Add two points.

        Args:
            other: Another Point.
        Return:
            A Point, where each component is the sum of that component
            in the first and second Points.
        """
        self._check_size(other)
        return Point(*tuple(x + y for x, y in zip(self, other)))

    def __le__(self, other: 'Point') -> bool:
        """Test if each component is less than or equal the corresponding component in the other.

        Note this constitutes a partial ordering, as a <= b and b <= a may both be false
        for certain pairs of Points.

        Args:
            other: Another Point.
        Return:
            True iff each component of the first is less than the corresponding
            component of the second.
        """
        self._check_size(other)
        return all(map(lambda pair: pair[0] <= pair[1], zip(self, other)))

    def __lt__(self, other: 'Point') -> bool:
        """Test if each component is less than the corresponding component in the other point.

        Note this constitutes a partial ordering, as a < b and b < a may both be false
        for certain pairs of Points.

        Args:
            other: Another Point.
        Return:
            True iff each component of the first is less than the corresponding
            component of the second.
        """
        self._check_size(other)
        return all(map(lambda pair: pair[0] < pair[1], zip(self, other)))


class Tensor:
    def __init__(self, dimensions: Point,
                 source: Optional[Iterable[int]] = None,
                 default: Any = None):
        self.shape = dimensions
        self.dim = len(dimensions)
        self._size = reduce(lambda x, y: x * y, dimensions)
        source = source or repeat(default, self._size)
        self._contents = [element for element in islice(source, 0, self._size)]

    def __contains__(self, item):
        return Point.zero(self.dim) <= item < self.shape

    def _index(self, coordinates: Point):
        if coordinates not in self:
            raise IndexError('Invalid coordinates {} for dimensions {}'.format(coordinates, self.shape))

        index, _ = reduce(
            lambda x, y: (x[1] * y[0] + x[0], x[1] * y[1]),
            reversed(list(zip(coordinates, self.shape)))
        )

        return index

    def __getitem__(self, item):
        return self._contents[self._index(item)]

    def __setitem__(self, key, value):
        self._contents[self._index(key)] = value

    def __iter__(self):
        return iter(self._contents)
