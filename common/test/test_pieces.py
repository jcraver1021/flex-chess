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

from common.board import CartesianBoard, Piece
from common.coordinates import CartesianPoint
from common.piecemeal import get_repeated_points, direct_move
from common.player import Player


BOARD_DIMS = (5, 5)


class TestCartesianBoards:
    """Test board properties on a small board"""
    def __init__(self):
        self.players = [Player(color) for color in ['Red', 'Blue']]

    def test_direct_move(self):
        board = CartesianBoard(BOARD_DIMS)
        piece = Piece(self.players[0])
        origin = CartesianPoint(0, 0)
        destination = CartesianPoint(4, 4)
        board[origin] = piece
        yield assert_equal, board[origin], piece
        yield assert_is_none, board[destination]
        board.apply(direct_move(board, origin, destination))
        yield assert_equal, board[destination], piece
        yield assert_is_none, board[origin]

    def test_direct_capture(self):
        board = CartesianBoard(BOARD_DIMS)
        piece = Piece(self.players[0])
        victim = Piece(self.players[1])
        origin = CartesianPoint(0, 0)
        destination = CartesianPoint(4, 4)
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

    def test_repeated_points(self):
        board = CartesianBoard(BOARD_DIMS)
        origin = CartesianPoint(0, 0)
        r = repeat(CartesianPoint(1, 2))
        for x, y in zip(get_repeated_points(board, origin, r), [CartesianPoint(1, 2), CartesianPoint(2, 4)]):
            yield assert_equal, x, y
