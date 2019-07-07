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
"""Test suite for the list matrix object"""
from functools import reduce
from itertools import product
from typing import Any, Iterable, List, Tuple

from nose.tools import assert_equal, assert_raises

from common.tools import iterate_submatrices, make_list_matrix

# Test parameters
TEST_VALUE = 1337  # type: int
DIMENSIONS = (2, 3, 1, 4)  # type: Tuple


def list_matrix_get(list_matrix, iter_index):
    # type: (List[Any], Iterable[int]) -> Any
    """Get a value from the list matrix"""
    return reduce(lambda matrix, index: matrix[index], iter_index, list_matrix)


def check_get(list_matrix, iter_index):
    """Assert that the matrix contains the expected value at the given index"""
    assert list_matrix_get(list_matrix, iter_index) == TEST_VALUE


def test_list_matrix():
    """Test the the list matrix method produces expected dimensions"""
    maxes = ()
    generators = []
    for i in DIMENSIONS:
        maxes += (i,)
        generators.append(range(i))
        lol = make_list_matrix(maxes, TEST_VALUE)
        for index in product(*generators):
            check_get(lol, index)


def test_list_matrix_out_of_bounds():
    """Test that list matrix cannot access addresses beyond its size"""
    lol = make_list_matrix(DIMENSIONS)
    assert_raises(IndexError, list_matrix_get, lol, DIMENSIONS)


def test_iterate_submatrices():
    """Test the ability to iterate over layers of the matrix"""
    matrix = make_list_matrix(DIMENSIONS, 1)
    for submatrix in iterate_submatrices(DIMENSIONS[:2], matrix):
        assert_equal(submatrix, [[1, 1, 1, 1]])
    for submatrix in iterate_submatrices(DIMENSIONS[:3], matrix):
        assert_equal(submatrix, [1, 1, 1, 1])
