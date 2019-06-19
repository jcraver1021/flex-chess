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

from nose.tools import assert_equal, assert_is_none, assert_raises

from common.board import CartesianBoard
from common.coordinates import CartesianPoint

SMALL_BOARD = (3, 3)
HIGH_D_BOARD = (1, 2, 3, 4)


class TestCartesianBoards:
    """Test board properties on a small board"""
    def __init__(self):
        self.board_scans = [[range(i) for i in SMALL_BOARD], [range(i) for i in HIGH_D_BOARD]]

    @classmethod
    def setup_class(cls):
        """Set up the board we will use in these tests"""
        cls.boards = [CartesianBoard(SMALL_BOARD), CartesianBoard(HIGH_D_BOARD)]

    def test_get_empty(self):
        """Test that all get operations on an empty board return None"""
        for board, board_scan in zip(self.boards, self.board_scans):
            for index in product(*board_scan):
                yield assert_is_none, board[CartesianPoint(*index)]

    def test_oob(self):
        """Testing that accessing a point off the board causes an exception"""
        yield assert_raises, IndexError, self.boards[0].__getitem__, CartesianPoint(-1, -1)
        yield assert_raises, IndexError, self.boards[0].__getitem__, CartesianPoint(*SMALL_BOARD)
        yield assert_raises, IndexError, self.boards[1].__getitem__, CartesianPoint(-1, -1, -1, -1)
        yield assert_raises, IndexError, self.boards[1].__getitem__, CartesianPoint(*HIGH_D_BOARD)

    def test_set_object(self):
        """Test placing and removing an object"""
        piece = 'Silly King'
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
