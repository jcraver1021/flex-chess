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
"""General tools used across FlexChess"""
from functools import reduce
from itertools import product
from typing import Any, List, Optional, Tuple


def make_list_matrix(shape, default=None):
    # type: (Tuple, Optional[Any]) -> List[Any]
    """Make a matrix of embedded lists"""
    def _list_matrix_helper(index):
        # type: (int) -> List[Any]
        if index + 1 == len(shape):
            return [default for _ in range(shape[index])]
        return [_list_matrix_helper(index + 1) for _ in range(shape[index])]

    return _list_matrix_helper(0)


def iterate_submatrices(bounds, matrix):
    # type: (Tuple, List[Any]) -> List[Any]
    """Iterate across the lowest layers of the matrix

    For example, if the final two dimensions are omitted,
    this function will generate every 2D layer"""
    for sub_index in product(*[range(b) for b in bounds]):
        yield reduce(lambda m, i: m[i], sub_index, matrix)
