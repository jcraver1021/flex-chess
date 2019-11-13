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
from copy import deepcopy
from typing import Generator, List, NamedTuple, Optional, Tuple, Union

from common.common import Point, Tensor
from common.player import Player


class IllegalBoardState(Exception):
    """Raised when the board is moved into an illegal state"""


class Piece:
    """A piece belonging to a player."""
    def __init__(self,
                 player: Player,
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


class Mutation(NamedTuple):
    """A mutation of the board state."""
    source: Optional[Union[Point, Piece]]
    target: Point


class Board:
    """A game board with cartesian coordinates. Point are finite and at least 0."""

    def __init__(self, shape: Tuple) -> None:
        self.shape = Point(*shape)
        self._board = Tensor(self.shape)

    def __getitem__(self, point) -> Piece:
        return self._board[point]

    def _place(self, piece: Optional[Piece], point: Optional[Point]) -> None:
        """Update a piece to the new location.

        Do nothing if both inputs are None.
        """
        if point:
            self._board[point] = piece
        if piece:
            piece.place(self, point)

    def mutate(self, mutation: Mutation) -> Optional[Piece]:
        """Mutate the board state.

        Args:
            mutation: The mutation to apply to the board.
        Returns:
            The piece displaced by this mutation, or None if no piece was displaced
        """
        current_piece = self[mutation.target]
        if current_piece:
            self._place(current_piece, None)

        new_piece = None
        if mutation.source:
            if isinstance(mutation.source, Point):
                new_piece = self[mutation.source]
                self._board[mutation.source] = None
            else:
                new_piece = mutation.source

        self._place(new_piece, mutation.target)

        # Do not return if no-op move, since this represents capture/removal
        return current_piece if current_piece != new_piece else None
