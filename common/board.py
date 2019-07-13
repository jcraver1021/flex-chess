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
from copy import deepcopy
from enum import Enum
from functools import reduce
from typing import Callable, Dict, Generator, Iterable, List, NamedTuple, Optional, Set, Tuple

from common.coordinates import Point
from common.player import Player
from common.tools import iterate_submatrices, make_list_matrix


class IllegalBoardState(Exception):
    """Raised when the board is moved into an illegal state"""


class Piece:
    """A piece belonging to a player"""
    def __init__(self, player, token='X', move_generators=None):
        # type: (Player, str, Optional[Callable[[Board, Point], Generator]]) -> None
        self.player = player
        self.token = token
        self.move_generators = move_generators or []
        self.board = None
        self.coordinates = None

    def get_moves(self, board, point):
        # type: (Board, Point) -> List[List[Mutation]]
        """Get a list of all legal sequences by this piece from this point"""
        moves = []
        for generator in self.move_generators:
            for sequence in generator(board, point):
                # It is incumbent on the board to say if it has been put into an illegal state
                try:
                    board_copy = deepcopy(board)
                    board_copy.apply(sequence)
                    moves.append(sequence)
                except IllegalBoardState:
                    pass
        return moves

    def __str__(self):
        return self.token


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
    point: Point
    payload: Piece = None


class Board:
    """A game board with cartesian coordinates. Point are finite and at least 0."""

    def __init__(self, shape):
        # type: (Tuple) -> None
        self.shape = Point(*shape)  # type: Point
        self.board = make_list_matrix(shape)
        self.jail = defaultdict(set)  # type: Dict[Player, Set[Piece]]

    def __contains__(self, item):
        # type: (Point) -> bool
        return Point.zero(len(item)) <= item < self.shape

    def _assert_on_board(self, coordinates):
        # type: (Point) -> None
        if coordinates not in self:
            raise IndexError('{} not on board'.format(coordinates))

    def __getitem__(self, item):
        # type: (Point) -> Piece
        self._assert_on_board(item)
        # noinspection PyTypeChecker
        return reduce(lambda matrix, index: matrix[index], item, self.board)

    def __setitem__(self, key, value):
        # type: (Point, Piece) -> None
        self._assert_on_board(key)
        piece = self[key]
        if piece:
            self._update_piece_location(piece, None)
        final_column = reduce(lambda matrix, index: matrix[index], key[:-1], self.board)
        final_column[key[-1]] = value
        if value:
            self._update_piece_location(value, key)

    def __delitem__(self, key):
        # type: (Point) -> None
        self._assert_on_board(key)
        piece = self[key]
        if piece:
            self._update_piece_location(piece, None)
        final_column = reduce(lambda matrix, index: matrix[index], key[:-1], self.board)
        final_column[key[-1]] = None

    def _update_piece_location(self, piece, place):
        # type: (Piece, Point) -> None
        piece.board = self
        piece.coordinates = place

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

    def __str__(self):
        strings = []

        # Board portion (2D cross-section at a time)
        for sub_board in iterate_submatrices(self.shape[:-2], self.board):
            strings.append(self._print_2d(sub_board))
            strings.append('\n')

        # Jail portion
        for player, jail in self.jail.items():
            strings.append("{}'s captures: {}".format(player.name, ', '.join(map(str, jail))))

        return ''.join(strings)

    @staticmethod
    def _print_2d(sub_board):
        # Override this if your chess variant needs to
        return '\n'.join(
            ''.join(map(lambda square: str(square) if square else ' ', row)) for row in sub_board)
