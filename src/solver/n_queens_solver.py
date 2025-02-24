from typing import List, Tuple

def is_safe(board: List[List[int]], row: int, col: int) -> bool:
    # Check the column
    for i in range(8):
        if board[i][col] == 1:
            return False

    # Check this row on left side
    for i in range(col):
        if board[row][i] == 1:
            return False

    # Check upper diagonal on left side
    for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
        if board[i][j] == 1:
            return False

    # Check lower diagonal on left side
    for i, j in zip(range(row, 8, 1), range(col, -1, -1)):
        if board[i][j] == 1:
            return False

    return True

def solve_n_queens_util(board: List[List[int]], col: int) -> bool:
    if col >= 8:
        return True

    for i in range(8):
        if is_safe(board, i, col):
            board[i][col] = 1
            if solve_n_queens_util(board, col + 1):
                return True
            board[i][col] = 0

    return False

def solve_n_queens(initial_queens: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    board = [[0 for _ in range(8)] for _ in range(8)]

    # Place initial queens
    for row, col in initial_queens:
        if not is_safe(board, row, col):
            return []  # Invalid initial configuration
        board[row][col] = 1

    # Start solving from the next column
    start_col = len(initial_queens)
    if solve_n_queens_util(board, start_col):
        solution = initial_queens[:]
        for col in range(start_col, 8):
            for row in range(8):
                if board[row][col] == 1:
                    solution.append((row, col))
                    break
        return solution
    else:
        return []  # No solution found

def n_queens_solver(initial_state: str) -> int:
    # print(f"Solving N-Queens...")
    # print(initial_state)
    solution = solve_n_queens(initial_state)

    if solution:
        # print(f"  Solution: {solution}")
        moves = len(solution) - len(initial_state)
        # print(f"  Queens added: {moves}")
        return moves
    else:
        # print(f"  No solution found")
        return 99999