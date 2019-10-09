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
from itertools import repeat, zip_longest
from nose.tools import assert_equal, assert_in, assert_is_none

from common.object import Board, Piece
from common.coordinates import Point
from common.piecemeal import get_repeated_points, direct_move
from common.player import Player


BOARD_DIMS = (5, 5)
EMPTY_SENTINEL = 'Empty'


def check_iterators(iter_actual, iter_expected):
    """Assert that two iterators return the same values and are the same length"""
    for actual_value, expected_value in zip_longest(iter_actual, iter_expected,
                                                    fillvalue=EMPTY_SENTINEL):
        assert_equal(actual_value, expected_value)


class TestBoards:
    """Test board properties on a small board"""
    def __init__(self):
        self.players = [Player(color) for color in ['Red', 'Blue']]
        self.board = None

    def setup(self):
        """Reinitialize the board for each test"""
        self.board = Board(BOARD_DIMS)

    def test_direct_move(self):
        """Test that sequences can move pieces"""
        piece = Piece(self.players[0])
        origin = Point(0, 0)
        destination = Point(4, 4)
        self.board[origin] = piece
        assert_equal(self.board[origin], piece)
        assert_is_none(self.board[destination])
        self.board.apply(direct_move(self.board, origin, destination))
        assert_equal(self.board[destination], piece)
        assert_is_none(self.board[origin])

    def test_direct_capture(self):
        """Test that direct capture mutates state appropriately"""
        piece = Piece(self.players[0])
        victim = Piece(self.players[1])
        origin = Point(0, 0)
        destination = Point(4, 4)
        self.board[origin] = piece
        self.board[destination] = victim
        assert_equal(self.board[origin], piece)
        assert_equal(self.board[destination], victim)
        assert_equal(len(self.board.jail[self.players[0]]), 0)
        assert_equal(len(self.board.jail[self.players[1]]), 0)
        self.board.apply(direct_move(self.board, origin, destination))
        assert_equal(self.board[destination], piece)
        assert_is_none(self.board[origin])
        assert_equal(len(self.board.jail[self.players[0]]), 1)
        assert_in(victim, self.board.jail[self.players[0]])
        assert_equal(len(self.board.jail[self.players[1]]), 0)

    def test_repeated_points(self):
        """Test that point repeater returns expected results"""
        origin = Point(0, 0)
        self.board[origin] = Piece(self.players[0])
        # Test that it continues until the piece would leave the board
        repeater = repeat(Point(1, 2))
        expected_points = [Point(1, 2), Point(2, 4)]
        check_iterators(get_repeated_points(self.board, origin, repeater), expected_points)
        # Test that it won't move over an ally
        repeater = repeat(Point(1, 1))
        self.board[Point(3, 3)] = Piece(self.players[0])
        expected_points = [Point(1, 1), Point(2, 2), Point(3, 3)]
        check_iterators(get_repeated_points(self.board, origin, repeater), expected_points[:-1])
        # Test that it will move onto an opponent
        self.board[Point(3, 3)] = Piece(self.players[1])
        check_iterators(get_repeated_points(self.board, origin, repeater), expected_points)
        # Test that it won't move onto an opponent if told not to
        check_iterators(get_repeated_points(self.board, origin, repeater, capture=False),
                        expected_points[:-1])
