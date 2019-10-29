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
from typing import (
    Dict, Generator, Iterable, List, NamedTuple, Optional, Set, Tuple)

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

    def __init__(self, shape: Tuple) -> None:
        self.shape = Point(*shape)
        self.board = Tensor(self.shape)
        self.jail: Dict[Player, Set[Piece]] = defaultdict(set)

    def __contains__(self, point: Point) -> bool:
        return point in self.board

    def __getitem__(self, point: Point) -> Piece:
        return self.board[point]

    def __setitem__(self, point: Point, piece: Optional[Piece]):
        current_piece = self[point]
        if current_piece:
            self._update_piece_location(current_piece, None)
        self.board[point] = piece
        if piece:
            self._update_piece_location(piece, point)

    def __delitem__(self, point: Point) -> None:
        piece = self[point]
        if piece:
            self._update_piece_location(piece, None)
        self.board[point] = None

    def _update_piece_location(self, piece: Piece, place: Optional[Point]):
        piece.place(self, place)

    def apply(self, sequence: Iterable[Mutation]) -> None:
        """Apply a sequence of mutations to the board"""
        for mutation in sequence:
            if self[mutation.point] and mutation.op in CAPTURE_OPS:
                self.jail[mutation.payload.player].add(self[mutation.point])
            if mutation.op in REMOVE_OPS:
                del self[mutation.point]
            if mutation.op == Operation.PLACE:
                self[mutation.point] = mutation.payload
