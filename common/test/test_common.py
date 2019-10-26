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
"""Tests for the common module"""
from itertools import count, product, zip_longest

from nose.tools import (assert_equal, assert_false, assert_is_none,
                        assert_raises, assert_true)

from common.common import Point, Tensor


class TestPoints:
    """Tests for the Point object."""

    @staticmethod
    def test_equality() -> None:
        """Test point equality"""
        assert_true(Point(1, 2) == Point(1, 2))
        assert_false(Point(1, 2) == Point(2, 1))

    @staticmethod
    def test_length() -> None:
        """Test that len(point) works as expected."""
        assert_equal(len(Point()), 0)
        assert_equal(len(Point(1)), 1)
        assert_equal(len(Point(1, 2)), 2)

    @staticmethod
    def test_zeros() -> None:
        """Test that Point.zero is equivalent to creating one using the constructor"""
        for i in range(5):
            assert_equal(Point(*tuple(0 for _ in range(i))), Point.zero(i))

    @staticmethod
    def test_add() -> None:
        """Test adding points"""
        for i in range(5):
            point1 = Point(*tuple(j for j in range(i)))
            point2 = Point(*tuple(i - j for j in range(i)))
            point3 = Point(*tuple(i for _ in range(i)))
            assert_equal(point1 + Point.zero(i), point1)
            assert_equal(point1 + point2, point3)

    @staticmethod
    def test_lt_le() -> None:
        """Test the partial order of comparing points"""
        point0 = Point.zero(3)
        point1 = Point(1, 2, 3)
        point2 = Point(2, 4, 4)
        point3 = Point(3, 3, 3)
        assert_true(point0 < point1)
        assert_true(point0 <= point1)
        assert_true(point0 < point2)
        assert_true(point0 <= point2)
        assert_true(point0 < point3)
        assert_true(point0 <= point3)
        assert_true(point1 < point2)
        assert_true(point1 <= point2)
        assert_false(point1 < point3)
        assert_true(point1 <= point3)
        assert_false(point2 < point3)
        assert_false(point2 <= point3)
        assert_true(point0 < point1 < point2)
        assert_false(point0 < point1 < point3)
        assert_true(point0 < point1 <= point3)


SIZE_SMALL = Point(5)
SIZE_MED = Point(6, 7)
SIZE_LARGE = Point(3, 5, 7)
EMPTY_SENTINEL = 'Empty'


class TestTensor:
    """Tests for the Tensor object."""

    def __init__(self) -> None:
        self.sizes = [SIZE_SMALL, SIZE_MED, SIZE_LARGE]
        self.ranges = [[range(i) for i in size] for size in self.sizes]
        self.tensors = [Tensor(size, source=count()) for size in self.sizes]

    def test_iteration(self) -> None:
        """Tests assumptions on iteration.

        Iterating across the contents of the tensor should be equivalent
        to accessing indices of the tensor incrementally.
        """
        for coord_range, tensor in zip(self.ranges, self.tensors):
            for index, element in zip_longest(product(*coord_range), tensor,
                                              fillvalue=EMPTY_SENTINEL):
                assert_equal(tensor[index], element)

    def test_default_value(self) -> None:
        """Test that default values are assigned everywhere."""
        for size in self.sizes:
            # This default value is arbitrary
            default = len(size)
            tensor = Tensor(size, default=default)

            for element in tensor:
                assert_equal(default, element)

    def test_no_default_value(self) -> None:
        """Test that None is the default value everywhere."""
        for size in self.sizes:
            tensor = Tensor(size)

            for element in tensor:
                assert_is_none(element)

    def test_oob(self) -> None:
        """Test that invalid index access fails."""
        def one_hot_point(place: int, length: int, value: int) -> Point:
            return Point(*(value if i == place else 0 for i in range(length)))

        for tensor in self.tensors:
            dims = tensor.shape
            for digit in range(len(dims)):
                oob_points = [one_hot_point(digit, len(dims), value) for value in [-1, dims[digit]]]
                for oob_point in oob_points:
                    assert_raises(IndexError, tensor.__getitem__, oob_point)
