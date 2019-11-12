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
"""Test the board functionality"""
from itertools import product

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
    * The inversion's target equals the mutation's source
    * The inversion's source equals the mutation's target
    * The source point is empty
    * If a piece was in the target point, it is no longer there, nor thinks it is there
    * If the target exists, it now contains to_place or whatever was at source
    * If there was a piece at the source point, it is now at the target point

    Args:
        board: The board on which to apply the mutation.
        mutation: The mutation to apply
    """
    source_piece = mutation.to_place
    target_piece = board[mutation.target] if mutation.target else None
    inversion = board.mutate(mutation)

    # Assert the inversion inverts the mutation.
    assert_equal((mutation.source, mutation.target), (inversion.target, inversion.source))

    # Assert the piece is no longer at its starting location.
    if mutation.source:
        assert_is_none(board[mutation.source])

    # Assert the target was removed.
    if target_piece:
        assert_equal((board, None), target_piece.find())
        assert_equal(target_piece, inversion.to_place)

    # Assert the placement succeeded.
    if mutation.target:
        assert_equal(source_piece, board[mutation.target])
    if source_piece:
        assert_equal((board, mutation.target), source_piece.find())


class TestBoards:
    """Test board properties on a small board"""
    def __init__(self) -> None:
        self.sizes = [SIZE_SMALL, SIZE_MED, SIZE_LARGE]
        self.ranges = [[range(i) for i in size] for size in self.sizes]
        self.boards = [Board(size) for size in self.sizes]
        self.player = Player('Player 1')

    def setup(self):
        """Reinitialize the boards."""
        self.boards = [Board(size) for size in self.sizes]

    def test_place(self):
        """Test placing a piece at every point."""
        for coord_range, board in zip(self.ranges, self.boards):
            for point in product(*coord_range):
                piece = Piece(self.player)
                mutation = Mutation(to_place=piece, target=Point(*point))
                mutate_and_check(board, mutation)

    def test_remove(self):
        """Test placing and removing a piece at every point."""
        for coord_range, board in zip(self.ranges, self.boards):
            for point in product(*coord_range):
                piece = Piece(self.player)
                mutate_add = Mutation(to_place=piece, target=Point(*point))
                mutate_and_check(board, mutate_add)
                mutate_remove = Mutation(target=Point(*point))
                mutate_and_check(board, mutate_remove)

    def test_capture(self):
        """Test placing a piece over each point."""
        for coord_range, board in zip(self.ranges, self.boards):
            for point in product(*coord_range):
                piece_one = Piece(self.player)
                mutate_add = Mutation(to_place=piece_one, target=Point(*point))
                mutate_and_check(board, mutate_add)
                piece_two = Piece(self.player)
                mutate_capture = Mutation(to_place=piece_two, target=Point(*point))
                mutate_and_check(board, mutate_capture)

    def test_move(self):
        """Test placing a piece at the origin and moving it to each point."""
        for size, coord_range, board in zip(self.sizes, self.ranges, self.boards):
            zero_point = Point.zero(len(size))
            for point in product(*coord_range):
                piece = Piece(self.player)
                mutate_add = Mutation(to_place=piece, target=zero_point)
                mutate_and_check(board, mutate_add)
                mutate_move = Mutation(source=zero_point, target=Point(*point))
                mutate_and_check(board, mutate_move)

    def test_move_and_capture(self):
        """Test placing a piece at the origin and moving it over each point."""
        for size, coord_range, board in zip(self.sizes, self.ranges, self.boards):
            zero_point = Point.zero(len(size))
            for point in product(*coord_range):
                piece_one = Piece(self.player)
                mutate_add = Mutation(to_place=piece_one, target=zero_point)
                mutate_and_check(board, mutate_add)
                piece_two = Piece(self.player)
                mutate_add2 = Mutation(to_place=piece_two, target=Point(*point))
                mutate_and_check(board, mutate_add2)
                mutate_move = Mutation(source=zero_point, target=Point(*point))
                mutate_and_check(board, mutate_move)
