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

from nose.tools import assert_equal, assert_in, assert_is_none, assert_raises

from common.object import Board, Operation, Mutation, Piece
from common.coordinates import Point
from common.player import Player

SMALL_BOARD = (3, 3)
HIGH_D_BOARD = (1, 2, 3, 4)


class TestBoards:
    """Test board properties on a small board"""
    def __init__(self):
        self.board_scans = [[range(i) for i in SMALL_BOARD], [range(i) for i in HIGH_D_BOARD]]
        self.players = [Player(color) for color in ['Red', 'Blue']]

    @classmethod
    def setup_class(cls):
        """Set up the board we will use in these tests"""
        cls.boards = [Board(SMALL_BOARD), Board(HIGH_D_BOARD)]

    def test_get_empty(self):
        """Test that all get operations on an empty board return None"""
        for board, board_scan in zip(self.boards, self.board_scans):
            for index in product(*board_scan):
                assert_is_none(board[Point(*index)])

    def test_contains(self):
        """Test the contains operator"""
        point_sets = [
            [
                (Point(-1, 0), False),
                (Point(1, 1), True),
                (Point(*SMALL_BOARD), False)
            ],
            [
                (Point(-1, 0, 0, 0), False),
                (Point(0, 1, 1, 1), True),
                (Point(*HIGH_D_BOARD), False)
            ]
        ]
        for board, point_set in zip(self.boards, point_sets):
            for point, on_board in point_set:
                assert_equal(point in board, on_board)

    def test_oob(self):
        """Testing that accessing a point off the board causes an exception"""
        assert_raises(IndexError, self.boards[0].__getitem__, Point(-1, -1))
        assert_raises(IndexError, self.boards[0].__getitem__, Point(*SMALL_BOARD))
        assert_raises(IndexError, self.boards[1].__getitem__, Point(-1, -1, -1, -1))
        assert_raises(IndexError, self.boards[1].__getitem__, Point(*HIGH_D_BOARD))

    def test_set_object(self):
        """Test placing and removing an object"""
        piece = Piece(self.players[0])
        piece2 = Piece(self.players[0])
        points = [Point(1, 1), Point(0, 1, 0, 1)]
        for board, point in zip(self.boards, points):
            board[point] = piece
            assert_equal(board[point], piece)
            assert_equal(piece.board, board)
            assert_equal(piece.coordinates, point)
            zero_point = Point.zero(len(point))
            board[zero_point] = piece2
            assert_equal(board[zero_point], piece2)
            assert_equal(piece2.board, board)
            assert_equal(piece2.coordinates, zero_point)
            del board[zero_point]
            assert_is_none(board[zero_point])
            assert_equal(piece2.board, board)
            assert_is_none(piece2.coordinates)

    def test_mutations(self):
        """Test executing a sequence of mutations"""
        point_sets = [
            [Point(0, 0), Point(0, 1), Point(1, 1)],
            [Point(0, 1, 0, 1), Point(0, 0, 1, 2), Point(0, 1, 2, 3)]
        ]
        pieces = [Piece(self.players[0]) for _ in range(2)]
        for points, board in zip(point_sets, self.boards):
            # Place the pieces on points 1 and 2
            board[points[0]] = pieces[0]
            board[points[1]] = pieces[1]
            assert_equal(board[points[0]], pieces[0])
            assert_equal(board[points[1]], pieces[1])
            assert_is_none(board[points[2]])
            # Move the pieces to points 2 and 3
            sequence = [
                Mutation(Operation.REMOVE, points[0]),
                Mutation(Operation.REMOVE, points[1]),
                Mutation(Operation.PLACE, points[1], pieces[0]),
                Mutation(Operation.PLACE, points[2], pieces[1])
            ]
            board.apply(sequence)
            assert_is_none(board[points[0]])
            assert_equal(board[points[1]], pieces[0])
            assert_equal(board[points[2]], pieces[1])

    def test_invalid_mutation(self):
        """Test that moving a piece off the board fails"""
        point_sets = [
            [Point(0, 0), Point(-1, -1)],
            [Point(0, 0, 0, 0), Point(-1, -1, -1, -1)]
        ]
        piece = Piece(self.players[0])
        for points, board in zip(point_sets, self.boards):
            board[points[0]] = piece
            assert_equal(board[points[0]], piece)
            sequence = [
                Mutation(Operation.REMOVE, points[0]),
                Mutation(Operation.PLACE, points[1])
            ]
            assert_raises(IndexError, board.apply, sequence)

    def test_capture_no_piece(self):
        """Tests that capturing a piece puts it into jail"""
        piece1 = Piece(self.players[0])
        piece2 = Piece(self.players[1])
        points = [Point.zero(2), Point.zero(4)]
        for point, board in zip(points, self.boards):
            assert_equal(len(board.jail[self.players[0]]), 0)
            assert_equal(len(board.jail[self.players[1]]), 0)
            board[point] = piece2
            board.apply([Mutation(Operation.CAPTURE, point, piece1)])
            assert_is_none(board[point])
            assert_in(piece2, board.jail[self.players[0]])
            assert_equal(len(board.jail[self.players[0]]), 1)
            assert_equal(len(board.jail[self.players[1]]), 0)

    def test_move_capture(self):
        """Tests that capturing a piece with another piece puts it into jail"""
        piece1 = Piece(self.players[0])
        piece2 = Piece(self.players[1])
        points = [Point.zero(2), Point.zero(4)]
        for point, board in zip(points, self.boards):
            assert_equal(len(board.jail[self.players[0]]), 0)
            assert_equal(len(board.jail[self.players[1]]), 0)
            board[point] = piece2
            board.apply([Mutation(Operation.PLACE, point, piece1)])
            assert_equal(board[point], piece1)
            assert_in(piece2, board.jail[self.players[0]])
            assert_equal(len(board.jail[self.players[0]]), 1)
            assert_equal(len(board.jail[self.players[1]]), 0)
