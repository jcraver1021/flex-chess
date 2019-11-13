#   Copyright 2019 James Craver #
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
"""Test the board functionality"""
from nose.tools import assert_equal, assert_is_none

from common.object import Board, Mutation, Piece
from common.common import Point
from common.player import Player

SIZE_SMALL = Point(5)
SIZE_MED = Point(6, 7)
SIZE_LARGE = Point(3, 5, 7)


def mutate_and_check(board: Board, mutation: Mutation):
    """Test that a mutation produces valid results.

    In particular, the following predicates are tested:
    * If the source is a point, the source is now empty
    * If a piece was at the target, it is no longer on the board
    * The return value is equal to contents of the target point
    * The source piece is now equal to the contents of the target point

    Args:
        board: The board on which to apply the mutation.
        mutation: The mutation to apply
    """
    if isinstance(mutation.source, Point):
        source_point = mutation.source
        source_piece = board[source_point]
    else:
        source_point = None
        source_piece = mutation.source
    target_piece = board[mutation.target] if mutation.target else None
    captured_piece = board.mutate(mutation)

    # If the source is a point, assert the source is now empty.
    if source_point is not None:
        assert_is_none(board[source_point])

    # If a piece was at the target, assert it is no longer on the board
    # unless it is equal to the source piece.
    if target_piece is not None and source_piece != target_piece:
        assert_equal((board, None), target_piece.find())

    # If the source and target pieces are different, assert that the target
    # piece is equal to the return piece
    if source_piece != target_piece:
        assert_equal(target_piece, captured_piece)

    assert_equal(source_piece, board[mutation.target])


def _get_point(length: int, value: int):
    return Point(*(value for _ in range(length)))


class TestBoards:
    """Test board properties on a small board"""
    def __init__(self) -> None:
        self.sizes = [SIZE_SMALL, SIZE_MED, SIZE_LARGE]
        self.boards = [Board(size) for size in self.sizes]
        self.player = Player('Player 1')

    def setup(self):
        """Reinitialize the boards."""
        self.boards = [Board(size) for size in self.sizes]

    def test_place(self):
        """Test placing a piece at a point."""
        for dims, board in zip(self.sizes, self.boards):
            point = Point.zero(len(dims))
            piece = Piece(self.player)
            mutation = Mutation(piece, point)
            mutate_and_check(board, mutation)

    def test_replace(self):
        """Test placing a piece twice at a point."""
        for dims, board in zip(self.sizes, self.boards):
            point = Point.zero(len(dims))
            piece = Piece(self.player)
            mutation = Mutation(piece, point)
            mutate_and_check(board, mutation)
            mutate_and_check(board, mutation)

    def test_overplace(self):
        """Test placing two pieces at the same point."""
        for dims, board in zip(self.sizes, self.boards):
            point = Point.zero(len(dims))
            piece_one = Piece(self.player)
            piece_two = Piece(self.player)
            mutation_one = Mutation(piece_one, point)
            mutate_and_check(board, mutation_one)
            mutation_two = Mutation(piece_two, point)
            mutate_and_check(board, mutation_two)

    def test_remove(self):
        """Test placing and removing a piece a point."""
        for dims, board in zip(self.sizes, self.boards):
            point = Point.zero(len(dims))
            piece = Piece(self.player)
            mutation_add = Mutation(piece, point)
            mutate_and_check(board, mutation_add)
            mutation_remove = Mutation(None, point)
            mutate_and_check(board, mutation_remove)

    def test_move_piece(self):
        """Test moving a piece to a new point."""
        for dims, board in zip(self.sizes, self.boards):
            point_one = _get_point(len(dims), 1)
            point_two = _get_point(len(dims), 2)
            piece = Piece(self.player)
            mutation_add = Mutation(piece, point_one)
            mutate_and_check(board, mutation_add)
            mutation_move = Mutation(piece, point_two)
            mutate_and_check(board, mutation_move)

    def test_move_point(self):
        """Test moving a piece from one point to a new point."""
        for dims, board in zip(self.sizes, self.boards):
            point_one = _get_point(len(dims), 1)
            point_two = _get_point(len(dims), 2)
            piece = Piece(self.player)
            mutation_add = Mutation(piece, point_one)
            mutate_and_check(board, mutation_add)
            mutation_move = Mutation(point_one, point_two)
            mutate_and_check(board, mutation_move)

    def test_capture_piece(self):
        """Test capturing a piece with another piece."""
        for dims, board in zip(self.sizes, self.boards):
            point_one = _get_point(len(dims), 1)
            point_two = _get_point(len(dims), 2)
            piece_one = Piece(self.player)
            piece_two = Piece(self.player)
            mutation_one = Mutation(piece_one, point_one)
            mutation_two = Mutation(piece_two, point_two)
            mutate_and_check(board, mutation_one)
            mutate_and_check(board, mutation_two)
            mutation_move = Mutation(piece_one, point_two)
            mutate_and_check(board, mutation_move)

    def test_capture_point(self):
        """Test capturing a piece from another point."""
        for dims, board in zip(self.sizes, self.boards):
            point_one = _get_point(len(dims), 1)
            point_two = _get_point(len(dims), 2)
            piece_one = Piece(self.player)
            piece_two = Piece(self.player)
            mutation_one = Mutation(piece_one, point_one)
            mutation_two = Mutation(piece_two, point_two)
            mutate_and_check(board, mutation_one)
            mutate_and_check(board, mutation_two)
            mutation_move = Mutation(point_one, point_two)
            mutate_and_check(board, mutation_move)
