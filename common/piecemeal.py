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
from typing import Any, Generator, List

from common.board import CartesianBoard, Mutation, Operation
from common.coordinates import CartesianPoint


def direct_move(board, origin, destination):
    # type: (CartesianBoard, CartesianPoint, CartesianPoint) -> List[Mutation]
    return [Mutation(Operation.REMOVE, origin), Mutation(Operation.PLACE, destination, board[origin])]


def get_repeated_points(board, point, step_generator, capture=True):
    # type: (CartesianBoard, CartesianPoint, Any, bool) -> Generator[CartesianPoint]
    """Generate a 'linear' sequence of points based on a starting point"""
    piece = board[point]
    point += next(step_generator)
    while point in board:
        if board[point] is None:
            yield point
            point += next(step_generator)
        else:
            if capture and piece.player != board[point].player:
                yield point
            return
