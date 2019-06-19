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
"""Board objects in common use"""
from functools import reduce
from typing import Any, Optional, Tuple

from common.coordinates import CartesianPoint
from common.tools import make_list_matrix


class CartesianBoard:
    """A game board with cartesian coordinates. CartesianPoint are finite and at least 0."""
    def __init__(self, shape):
        # type: (Tuple[int]) -> None
        self.shape = CartesianPoint(*shape)
        self.board = make_list_matrix(shape)

    def _check_on_board(self, coordinates, raise_if_off=False):
        # type: (CartesianPoint, Optional[bool]) -> bool
        on_board = CartesianPoint.zero(len(coordinates)) <= coordinates < self.shape
        if raise_if_off and not on_board:
            raise IndexError('{} not on board'.format(coordinates))
        return on_board

    def __getitem__(self, item):
        # type: (CartesianPoint) -> Any
        self._check_on_board(item, True)
        return reduce(lambda matrix, index: matrix[index], item, self.board)

    def __setitem__(self, key, value):
        # type: (CartesianPoint, Any) -> None
        self._check_on_board(key, True)
        final_column = reduce(lambda matrix, index: matrix[index], key[:-1], self.board)
        final_column[key[-1]] = value
