import re
import requests
import base64
import json
from collections import namedtuple
import enum

from game import Cage, op

def get_puzzle(puzzle_id):
    return parse_puzzle_data(download_puzzle(puzzle_id))

def download_puzzle(puzzle_id):
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

def parse_puzzle_data(puzzle_data):
    board_size = puzzle_data.index(['T'])-1

    val_grid = puzzle_data[puzzle_data.index(['T'])+1:puzzle_data.index(['S'])]
    op_grid = puzzle_data[puzzle_data.index(['S'])+1:puzzle_data.index(['V'])]
    borders  = {'V': puzzle_data[puzzle_data.index(['V'])+1:puzzle_data.index(['H'])], 
        'H': puzzle_data[puzzle_data.index(['H'])+1:puzzle_data.index(['H'])+board_size+1]}
    ops = {(row, col): op_grid[row][col] for row in range(board_size) for col in range(board_size) if op_grid[row][col] != '0'}
    cages = [Cage( find_cage(pt, board_size, borders), op(opstr), int(val_grid[pt[0]][pt[1]]) ) for (pt, opstr) in ops.items()]

    return {'board_size': board_size, 'cages': cages}

def find_neighbors(cur, cage, board_size, borders):
    to_search = []

    # try going down
    if cur[0] < board_size-1:
        if borders['H'][cur[1]][cur[0]] == '0':
            next = (cur[0]+1, cur[1])
            if next not in cage:
                cage.append(next)
                to_search.append(next)

    # try going right
    if cur[1] < board_size-1:
        if borders['V'][cur[0]][cur[1]] == '0':
            next = (cur[0], cur[1]+1)
            if next not in cage:
                cage.append(next)
                to_search.append(next)

    # try going left
    if cur[1]>0:
        if borders['V'][cur[0]][cur[1]-1] == '0':
            next = (cur[0], cur[1]-1)
            if next not in cage:
                cage.append(next)
                to_search.append(next)
    return to_search


def find_cage(starting_pt, board_size, borders):
    cur = starting_pt
    cage = [cur]
    neighbors = find_neighbors(cur, cage, board_size, borders)
    if neighbors:
        for neighbor in neighbors:
            find_neighbors(neighbor, cage, board_size, borders)
    return cage
