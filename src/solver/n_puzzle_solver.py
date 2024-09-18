from typing import List, Tuple
import heapq

class State:
    def __init__(self, board: List[List[int]], g: int, parent=None, move: str = ""):
        self.board = board
        self.g = g  # Cost to reach this state
        self.h = self.calculate_heuristic()  # Heuristic cost to goal
        self.f = self.g + self.h  # Total estimated cost
        self.parent = parent
        self.move = move

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple(map(tuple, self.board)))

    def calculate_heuristic(self) -> int:
        goal = [[1,2,3,4], [5,6,7,8], [9,10,11,12], [13,14,15,0]]
        distance = 0
        for i in range(4):
            for j in range(4):
                if self.board[i][j] != 0:
                    x, y = divmod(self.board[i][j] - 1, 4)
                    distance += abs(x - i) + abs(y - j)
        return distance

def get_blank_position(board: List[List[int]]) -> Tuple[int, int]:
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0:
                return i, j

def get_neighbors(state: State) -> List[State]:
    neighbors = []
    i, j = get_blank_position(state.board)
    directions = [(-1, 0, "D"), (1, 0, "U"), (0, -1, "R"), (0, 1, "L")]

    for di, dj, move in directions:
        ni, nj = i + di, j + dj
        if 0 <= ni < 4 and 0 <= nj < 4:
            new_board = [row[:] for row in state.board]
            new_board[i][j], new_board[ni][nj] = new_board[ni][nj], new_board[i][j]
            neighbors.append(State(new_board, state.g + 1, state, move))

    return neighbors

def is_goal_state(state: State) -> bool:
    return state.board == [[1,2,3,4], [5,6,7,8], [9,10,11,12], [13,14,15,0]]

def solve_n_puzzle(initial_board: List[List[int]]) -> Tuple[List[str], int]:
    initial_state = State(initial_board, 0)
    heap = [initial_state]
    visited = set()
    states_explored = 0

    while heap:
        current_state = heapq.heappop(heap)
        states_explored += 1

        if is_goal_state(current_state):
            moves = []
            while current_state.parent:
                moves.append(current_state.move)
                current_state = current_state.parent
            return moves[::-1], states_explored

        visited.add(hash(current_state))

        for neighbor in get_neighbors(current_state):
            if hash(neighbor) not in visited:
                heapq.heappush(heap, neighbor)

    return [], states_explored  # No solution found

def n_puzzle_solver(initial_state: str) -> int:
    # print(f"Solving N-Puzzle...")
    # print(initial_state)
    solution, states_explored = solve_n_puzzle(initial_state)

    if solution:
        # print(f"  Solution moves: {len(solution)}")
        # print(f"  Solution: {solution}")
        # print(f"  States explored: {states_explored}")
        return len(solution)
    else:
        # print(f"  States explored: {states_explored}")
        # print(f"  No solution found")
        return 99999