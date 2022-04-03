from collections import namedtuple
import enum

# Classes used for declaring the board
Cage = namedtuple("Cage", "cells op val")

# The values correspond to those used in the encoded layout of the game
class op(enum.Enum):
    DIV = '/'
    PROD = '*'
    SUM = '+'
    SUB = '-'
    NULL = '1'