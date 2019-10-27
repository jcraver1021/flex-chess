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
from typing import (Callable, Dict, Generator, Iterable, List, NamedTuple,
                    Optional, Set, Tuple)

from common.common import Point, Tensor
from common.player import Player


class IllegalBoardState(Exception):
    """Raised when the board is moved into an illegal state"""


class Piece:
    """A piece belonging to a player."""
    def __init__(self,
                 player: 'Player',
                 token: str = 'X',
                 move_generators: Generator['Mutation', None, None] = None
                 ) -> None:
        self.player = player
        self.token = token
        self.move_generators = move_generators or []
        self._board = None
        self._place = None

    def find(self) -> Tuple['Board', Point]:
        """Get the board and the place where this piece is."""
        return self._board, self._place

    def place(self, board: 'Board', place: Point) -> None:
        """Place this piece on a board."""
        self._board = board
        self._place = place

    def get_moves(self) -> List[List['Mutation']]:
        """Get a list of all legal sequences by this piece from this point."""
        moves = []
        for generator in self.move_generators:
            for sequence in generator(self._board, self._place):
                # It is incumbent on the board to say if it has been put into an illegal state
                try:
                    board_copy = deepcopy(self._board)
                    board_copy.apply(sequence)
                    moves.append(sequence)
                except IllegalBoardState:
                    pass
        return moves

    def __str__(self) -> str:
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
        self.board = Tensor(self.shape)  # type: Tensor
        self.jail = defaultdict(set)  # type: Dict[Player, Set[Piece]]

    def __contains__(self, item):
        # type: (Point) - > bool
        return item in self.board

    def __getitem__(self, item):
        # type: (Point) -> Piece
        return self.board[item]

    def __setitem__(self, key, value):
        # type: (Point, Piece) -> None
        piece = self[key]
        if piece:
            self._update_piece_location(piece, None)
        self.board[key] = value
        if value:
            self._update_piece_location(value, key)

    def __delitem__(self, key):
        # type: (Point) -> None
        piece = self[key]
        if piece:
            self._update_piece_location(piece, None)
        self.board[key] = None

    def _update_piece_location(self, piece, place):
        # type: (Piece, Optional[Point]) -> None
        piece.place(self, place)

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
