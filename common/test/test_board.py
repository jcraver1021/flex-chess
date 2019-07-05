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

from common.board import CartesianBoard, Operation, Mutation, Piece
from common.coordinates import CartesianPoint
from common.player import Player

SMALL_BOARD = (3, 3)
HIGH_D_BOARD = (1, 2, 3, 4)


class TestCartesianBoards:
    """Test board properties on a small board"""
    def __init__(self):
        self.board_scans = [[range(i) for i in SMALL_BOARD], [range(i) for i in HIGH_D_BOARD]]
        self.players = [Player(color) for color in ['Red', 'Blue']]

    @classmethod
    def setup_class(cls):
        """Set up the board we will use in these tests"""
        cls.boards = [CartesianBoard(SMALL_BOARD), CartesianBoard(HIGH_D_BOARD)]

    def test_get_empty(self):
        """Test that all get operations on an empty board return None"""
        for board, board_scan in zip(self.boards, self.board_scans):
            for index in product(*board_scan):
                yield assert_is_none, board[CartesianPoint(*index)]

    def test_contains(self):
        """Test the contains operator"""
        point_sets = [
            [
                (CartesianPoint(-1, 0), False),
                (CartesianPoint(1, 1), True),
                (CartesianPoint(*SMALL_BOARD), False)
            ],
            [
                (CartesianPoint(-1, 0, 0, 0), False),
                (CartesianPoint(0, 1, 1, 1), True),
                (CartesianPoint(*HIGH_D_BOARD), False)
            ]
        ]
        for board, point_set in zip(self.boards, point_sets):
            for point, on_board in point_set:
                yield assert_equal, point in board, on_board

    def test_oob(self):
        """Testing that accessing a point off the board causes an exception"""
        yield assert_raises, IndexError, self.boards[0].__getitem__, CartesianPoint(-1, -1)
        yield assert_raises, IndexError, self.boards[0].__getitem__, CartesianPoint(*SMALL_BOARD)
        yield assert_raises, IndexError, self.boards[1].__getitem__, CartesianPoint(-1, -1, -1, -1)
        yield assert_raises, IndexError, self.boards[1].__getitem__, CartesianPoint(*HIGH_D_BOARD)

    def test_set_object(self):
        """Test placing and removing an object"""
        piece = Piece(self.players[0])
        points = [CartesianPoint(1, 1), CartesianPoint(0, 1, 0, 1)]
        for board, point in zip(self.boards, points):
            board[point] = piece
            yield assert_equal, board[point], piece
            board[point] = None
            yield assert_is_none, board[point]
            zero_point = CartesianPoint.zero(len(point))
            board[zero_point] = piece
            yield assert_equal, board[zero_point], piece
            del board[zero_point]
            yield assert_is_none, board[zero_point]

    def test_mutations(self):
        """Test executing a sequence of mutations"""
        point_sets = [
            [CartesianPoint(0, 0), CartesianPoint(0, 1), CartesianPoint(1, 1)],
            [CartesianPoint(0, 1, 0, 1), CartesianPoint(0, 0, 1, 2), CartesianPoint(0, 1, 2, 3)]
        ]
        pieces = [Piece(self.players[0]) for _ in range(2)]
        for points, board in zip(point_sets, self.boards):
            # Place the pieces on points 1 and 2
            board[points[0]] = pieces[0]
            board[points[1]] = pieces[1]
            yield assert_equal, board[points[0]], pieces[0]
            yield assert_equal, board[points[1]], pieces[1]
            yield assert_is_none, board[points[2]]
            # Move the pieces to points 2 and 3
            sequence = [
                Mutation(Operation.REMOVE, points[0]),
                Mutation(Operation.REMOVE, points[1]),
                Mutation(Operation.PLACE, points[1], pieces[0]),
                Mutation(Operation.PLACE, points[2], pieces[1])
            ]
            board.apply(sequence)
            yield assert_is_none, board[points[0]]
            yield assert_equal, board[points[1]], pieces[0]
            yield assert_equal, board[points[2]], pieces[1]

    def test_invalid_mutation(self):
        """Test that moving a piece off the board fails"""
        point_sets = [
            [CartesianPoint(0, 0), CartesianPoint(-1, -1)],
            [CartesianPoint(0, 0, 0, 0), CartesianPoint(-1, -1, -1, -1)]
        ]
        piece = Piece(self.players[0])
        for points, board in zip(point_sets, self.boards):
            board[points[0]] = piece
            yield assert_equal, board[points[0]], piece
            sequence = [
                Mutation(Operation.REMOVE, points[0]),
                Mutation(Operation.PLACE, points[1])
            ]
            yield assert_raises, IndexError, board.apply, sequence

    def test_capture_no_piece(self):
        """Tests that capturing a piece puts it into jail"""
        piece1 = Piece(self.players[0])
        piece2 = Piece(self.players[1])
        points = [CartesianPoint.zero(2), CartesianPoint.zero(4)]
        for point, board in zip(points, self.boards):
            yield assert_equal, len(board.jail[self.players[0]]), 0
            yield assert_equal, len(board.jail[self.players[1]]), 0
            board[point] = piece2
            board.apply([Mutation(Operation.CAPTURE, point, piece1)])
            yield assert_is_none, board[point]
            yield assert_in, piece2, board.jail[self.players[0]]
            yield assert_equal, len(board.jail[self.players[0]]), 1
            yield assert_equal, len(board.jail[self.players[1]]), 0

    def test_move_capture(self):
        """Tests that capturing a piece with another piece puts it into jail"""
        piece1 = Piece(self.players[0])
        piece2 = Piece(self.players[1])
        points = [CartesianPoint.zero(2), CartesianPoint.zero(4)]
        for point, board in zip(points, self.boards):
            yield assert_equal, len(board.jail[self.players[0]]), 0
            yield assert_equal, len(board.jail[self.players[1]]), 0
            board[point] = piece2
            board.apply([Mutation(Operation.PLACE, point, piece1)])
            yield assert_equal, board[point], piece1
            yield assert_in, piece2, board.jail[self.players[0]]
            yield assert_equal, len(board.jail[self.players[0]]), 1
            yield assert_equal, len(board.jail[self.players[1]]), 0
