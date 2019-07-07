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
"""Tests for the coordinate module"""
from nose.tools import assert_equal, assert_false, assert_true

from common.coordinates import Point


def test_equality():
    """Test point equality"""
    yield assert_true, Point(1, 2) == Point(1, 2)
    yield assert_false, Point(1, 2) == Point(2, 1)


def test_length():
    """Test that len(point) works as expected."""
    yield assert_equal, len(Point()), 0
    yield assert_equal, len(Point(1)), 1
    yield assert_equal, len(Point(1, 2)), 2


def test_zeros():
    """Test that Point.zero is equivalent to creating one using the constructor"""
    for i in range(5):
        yield assert_equal, Point(*tuple(0 for _ in range(i))), Point.zero(i)


def test_add():
    """Test adding points"""
    for i in range(5):
        point1 = Point(*tuple(j for j in range(i)))
        point2 = Point(*tuple(i - j for j in range(i)))
        point3 = Point(*tuple(i for _ in range(i)))
        yield assert_equal, point1 + Point.zero(i), point1
        yield assert_equal, point1 + point2, point3


def test_lt_le():
    """Test the partial order of comparing points"""
    point0 = Point.zero(3)
    point1 = Point(1, 2, 3)
    point2 = Point(2, 4, 4)
    point3 = Point(3, 3, 3)
    yield assert_true, point0 < point1
    yield assert_true, point0 <= point1
    yield assert_true, point0 < point2
    yield assert_true, point0 <= point2
    yield assert_true, point0 < point3
    yield assert_true, point0 <= point3
    yield assert_true, point1 < point2
    yield assert_true, point1 <= point2
    yield assert_false, point1 < point3
    yield assert_true, point1 <= point3
    yield assert_false, point2 < point3
    yield assert_false, point2 <= point3
    yield assert_true, point0 < point1 < point2
    yield assert_false, point0 < point1 < point3
    yield assert_true, point0 < point1 <= point3
