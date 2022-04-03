import re
import requests
import base64
import json
from collections import namedtuple
import enum

from game import Cage, Cell, op, Puzzle

def get_puzzle(puzzle_id: int) -> Puzzle:
    return parse_puzzle_data(download_puzzle(puzzle_id))

PuzzleData = list[list[str]]

def download_puzzle(puzzle_id: int) -> PuzzleData:
    req = requests.post('http://www.kenkenpuzzle.com/find_puzzle', {'puzzle_id': puzzle_id})
    if req.status_code != 200:
        raise RuntimeException(f'http error {req.status_code}')

    m = re.search('base64_decode\(\'([\w=]+)\'', req.text)
    if not m:
        raise RuntimeException ('no regex match')

    puzzle_b64 = m.group(1)
    puzzle_raw = base64.b64decode(puzzle_b64) 
    puzzle_data = [l.rstrip().split() for l in json.loads(puzzle_raw)['data'].split('\n')]
    return puzzle_data

def parse_puzzle_data(puzzle_data: PuzzleData) -> Puzzle:
    board_size = puzzle_data.index(['T'])-1

    val_grid = puzzle_data[puzzle_data.index(['T'])+1:puzzle_data.index(['S'])]
    op_grid = puzzle_data[puzzle_data.index(['S'])+1:puzzle_data.index(['V'])]
    borders  = {'V': puzzle_data[puzzle_data.index(['V'])+1:puzzle_data.index(['H'])], 
        'H': puzzle_data[puzzle_data.index(['H'])+1:puzzle_data.index(['H'])+board_size+1]}
    ops = {Cell(row, col): op_grid[row][col] for row in range(board_size) for col in range(board_size) if op_grid[row][col] != '0'}
    cages = [Cage( find_cage(cell, board_size, borders), op(opstr), int(val_grid[cell.row][cell.col]) ) for (cell, opstr) in ops.items()]

    return Puzzle(board_size, cages)

def find_neighbors(cell: Cell, cage: list[Cell], board_size: int, borders: dict) -> list[Cell]:
    to_search = []

    # try going down
    if cell.row < board_size-1:
        if borders['H'][cell.col][cell.row] == '0':
            next = Cell(cell.row+1, cell.col)
            if next not in cage:
                cage.append(next)
                to_search.append(next)

    # try going right
    if cell.col < board_size-1:
        if borders['V'][cell.row][cell.col] == '0':
            next = Cell(cell.row, cell.col+1)
            if next not in cage:
                cage.append(next)
                to_search.append(next)

    # try going left
    if cell.col>0:
        if borders['V'][cell.row][cell.col-1] == '0':
            next = Cell(cell.row, cell.col-1)
            if next not in cage:
                cage.append(next)
                to_search.append(next)
    return to_search


def find_cage(start_cell: Cell, board_size: int, borders: dict) -> list[Cell]:
    cage = [start_cell]
    neighbors = find_neighbors(start_cell, cage, board_size, borders)
    if neighbors:
        for neighbor in neighbors:
            find_neighbors(neighbor, cage, board_size, borders)
    return cage
