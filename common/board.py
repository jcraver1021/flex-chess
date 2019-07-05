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
from collections import defaultdict
from enum import Enum
from functools import reduce
from typing import Any, Dict, Iterable, List, NamedTuple, Set, Tuple

from common.coordinates import CartesianPoint
from common.player import Player
from common.tools import make_list_matrix


class Piece:
    """A piece belonging to a player"""
    def __init__(self, player):
        # type: (Player) -> None
        self.player = player


class Operation(Enum):
    """An operation on the game board

    PLACE: Place a piece on the board. Capture the piece that is currently there (if any).
    REMOVE: Remove a piece from the board, but do not store it in the jail.
    CAPTURE: Remove a piece from the board and place it into the jail.
    """
    PLACE = 1
    REMOVE = 2
    CAPTURE = 3


CAPTURE_OPS = {Operation.PLACE, Operation.CAPTURE}
REMOVE_OPS = {Operation.REMOVE, Operation.CAPTURE}


class Mutation(NamedTuple):
    """A change to the state of the board"""
    op: Operation
    point: CartesianPoint
    payload: Piece = None


class CartesianBoard:
    """A game board with cartesian coordinates. CartesianPoint are finite and at least 0."""

    def __init__(self, shape):
        # type: (Tuple) -> None
        self.shape = CartesianPoint(*shape)  # type: CartesianPoint
        self.board = make_list_matrix(shape)  # type: List
        self.jail = defaultdict(set)  # type: Dict[Player, Set[Piece]]

    def __contains__(self, item):
        # type: (CartesianPoint) -> bool
        return CartesianPoint.zero(len(item)) <= item < self.shape

    def _assert_on_board(self, coordinates):
        # type: (CartesianPoint) -> None
        if coordinates not in self:
            raise IndexError('{} not on board'.format(coordinates))

    def __getitem__(self, item):
        # type: (CartesianPoint) -> Any
        self._assert_on_board(item)
        return reduce(lambda matrix, index: matrix[index], item, self.board)

    def __setitem__(self, key, value):
        # type: (CartesianPoint, Any) -> None
        self._assert_on_board(key)
        final_column = reduce(lambda matrix, index: matrix[index], key[:-1], self.board)
        final_column[key[-1]] = value

    def __delitem__(self, key):
        # type: (CartesianPoint) -> None
        self._assert_on_board(key)
        final_column = reduce(lambda matrix, index: matrix[index], key[:-1], self.board)
        final_column[key[-1]] = None

    def apply(self, sequence):
        # type: (Iterable[Mutation]) -> None
        """Apply a sequence of mutations to the board"""
        for mutation in sequence:
            if self[mutation.point] and mutation.op in CAPTURE_OPS:
                self.jail[mutation.payload.player].add(self[mutation.point])
            if mutation.op in REMOVE_OPS:
                del self[mutation.point]
            if mutation.op == Operation.PLACE:
                self[mutation.point] = mutation.payload
