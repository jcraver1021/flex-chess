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
"""Module for coordinates to address points on a board"""
from itertools import repeat
from nose.tools import assert_equal, assert_in, assert_is_none

from common.board import Board, Piece
from common.coordinates import Point
from common.piecemeal import get_repeated_points, direct_move
from common.player import Player


BOARD_DIMS = (5, 5)


class TestBoards:
    """Test board properties on a small board"""
    def __init__(self):
        self.players = [Player(color) for color in ['Red', 'Blue']]

    def test_direct_move(self):
        """Test that sequences can move pieces"""
        board = Board(BOARD_DIMS)
        piece = Piece(self.players[0])
        origin = Point(0, 0)
        destination = Point(4, 4)
        board[origin] = piece
        yield assert_equal, board[origin], piece
        yield assert_is_none, board[destination]
        board.apply(direct_move(board, origin, destination))
        yield assert_equal, board[destination], piece
        yield assert_is_none, board[origin]

    def test_direct_capture(self):
        """Test that direct capture mutates state appropriately"""
        board = Board(BOARD_DIMS)
        piece = Piece(self.players[0])
        victim = Piece(self.players[1])
        origin = Point(0, 0)
        destination = Point(4, 4)
        board[origin] = piece
        board[destination] = victim
        yield assert_equal, board[origin], piece
        yield assert_equal, board[destination], victim
        yield assert_equal, len(board.jail[self.players[0]]), 0
        yield assert_equal, len(board.jail[self.players[1]]), 0
        board.apply(direct_move(board, origin, destination))
        yield assert_equal, board[destination], piece
        yield assert_is_none, board[origin]
        yield assert_equal, len(board.jail[self.players[0]]), 1
        yield assert_in, victim, board.jail[self.players[0]]
        yield assert_equal, len(board.jail[self.players[1]]), 0

def test_repeated_points():
    """Test that point repeater returns expected results"""
    board = Board(BOARD_DIMS)
    origin = Point(0, 0)
    repeater = repeat(Point(1, 2))
    for actual_point, expected_point in zip(get_repeated_points(board, origin, repeater),
                                            [Point(1, 2), Point(2, 4)]):
        yield assert_equal, actual_point, expected_point
