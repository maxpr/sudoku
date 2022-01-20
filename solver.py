import numpy as np
from typing import List
import time
import logging


board = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7]
]

potential_values = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
LOGGER = logging.getLogger(__name__)


def print_board(board: List[List[int]]) -> None:
    """
    Print a sudoku board.

    :param board: Sudoku board a a list of list.
    """
    final_str = ""
    for row_number, sub_arr in enumerate(board):
        if row_number % 3 == 0:
            final_str += "- " * (len(sub_arr) + 3) + "\n"
        for idx, number in enumerate(sub_arr):
            if idx % 3 == 0:
                final_str += "| "
            final_str += str(number) + " "
        final_str += "\n"
    final_str += "- " * (len(sub_arr) + 3) + "\n"
    return final_str


def valid_combinations(board: List[List[int]], row_number: int, column_number: int) -> List[int]:
    """
    Get the potential correct number at a given location.

    :param board: The sudoku board.
    :param row_number: Row number to check.
    :param column_number: Colum number to check.

    :return: The list of potential value that can be set at this space in the board
    """
    LOGGER.debug(f"getting {row_number} and {column_number}")
    LOGGER.debug(f"row {board[row_number][:]} and column have potential values{([row[column_number] for row in board])}")
    set_used_number = set(board[row_number][:]).union(set([row[column_number] for row in board])) - set([0])
    return list(potential_values - set_used_number)


def is_board_valid(board):
    """
    Check if the sudoku board is valid.

    :param board: The sudoku board.

    :return: True if the board is valid else False.
    """
    index = 0
    while index < len(board):
        # If a value is repeated in a row, it's not valid
        if len(potential_values - set([row[index] for row in board])) > 0:
            return False
        # if a value is repeated in a column, it's not valid
        if len(potential_values - set(board[index][:])) > 0:
            return False
        index += 1
    return True


def backtrack(row: int, col: int, board: List[List[int]], original_board: List[List[int]]) -> (int, int):
    """
    Implementation of a backtrack, to understand to which cell we need to go back to from a current position

    :param row: Current row number.
    :param col: Current col number.
    :param board: Current board.
    :param original_board: Original number to remember which value not to change.

    :return: A column and row number to start back from.
    """
    # Backtrack
    col -= 1
    if col < 0:
        col = len(board[0]) - 1
        row -= 1
    # Keep track of the number of time you backtracked
    while board[row][col] == original_board[row][col]:
        col -= 1
        if col < 0:
            col = len(board[0]) - 1
            row -= 1
    board[row][col] = 0
    return row, col


def solve_board(board: List[List[int]]) -> None:
    """
    Solve the board.

    :param board: Initial state of the board.
    """
    incomplete: bool = True
    row = 0
    col = 0

    # Keep the original board, as well as the backtrack count for each cell.
    original_board = []
    backtrack_count = []
    for i in board:
        local = []
        backtrack_local = []
        for j in i:
            local.append(j)
            backtrack_local.append(0)
        original_board.append(local)
        backtrack_count.append(backtrack_local)

    board_solved = board.copy()
    # Until the board is not complete
    while incomplete:
        # Put the current cell to 0
        if board_solved[row][col] == 0:
            # Get all potential number at this cell
            potential_number = valid_combinations(board_solved, row, col)
            # If none, backtrack by one
            if len(potential_number) < 1:
                LOGGER.debug(f"Bakctracking as no potential value fit in col {col} row {row}")
                row, col = backtrack(row, col, board_solved, original_board)
            # Else, if you backtracked already and tried all values of this cell, backtrack to previous cell,
            # and put the backtrack to 0, as we will change a previous cell and try new combinations.
            elif backtrack_count[row][col] >= len(potential_number):
                backtrack_count[row][col] = 0
                LOGGER.debug(f"Backtracking from {col} {row} because value {potential_number[backtrack_count[row][col]-1]}  has been tried")
                row, col = backtrack(row, col, board_solved, original_board)
            # Else Place number index with number of backtracked time
            else:
                LOGGER.debug(f"Selecting new value from {col} {row} at index {backtrack_count[row][col]} with value {potential_number[backtrack_count[row][col]]}")
                board_solved[row][col] = potential_number[backtrack_count[row][col]]
                backtrack_count[row][col] += 1
                if col == len(board_solved[0]) - 1:
                    col = 0
                    row += 1
                else:
                    col += 1
            # Continue

        else:
            LOGGER.debug(f"At {col} {row} we have a value, we skip it")
            if col == len(board_solved[0]) - 1:
                col = 0
                row += 1
            else:
                col += 1

        if is_board_valid(board_solved):
            incomplete = False
    return board_solved


if __name__ == '__main__':
    print(print_board(board))
    solve_board(board)
    print(print_board(board))