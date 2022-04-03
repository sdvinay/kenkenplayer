from collections import namedtuple
import enum

# Classes used for declaring the board
Cell = namedtuple("Cell", "row col")
Cage = namedtuple("Cage", "cells op val")
Puzzle = namedtuple("Puzzle", "board_size cages")

# The values for the ops correspond to those used in the encoded layout of the game
class op(enum.Enum):
    DIV = '/'
    PROD = '*'
    SUM = '+'
    SUB = '-'
    NULL = '1'
