from typing import List, Tuple
from collections import deque

class State:
    def __init__(self, position: Tuple[int, int], path: str = ""):
        self.position = position
        self.path = path

def parse_maze(maze_str: str) -> Tuple[List[List[str]], Tuple[int, int], Tuple[int, int]]:
    maze = [list(row.strip()) for row in maze_str.strip().split('\n') if row.strip()]
    if not maze:
        raise ValueError("Empty maze")
    
    max_width = max(len(row) for row in maze)
    maze = [row + [' '] * (max_width - len(row)) for row in maze]
    
    start = None
    end = None
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 'S':
                start = (x, y)
            elif cell == 'X':
                end = (x, y)
    
    if start is None or end is None:
        raise ValueError("Start (S) or end (X) position not found in the maze")
    
    return maze, start, end

def is_valid_move(pos: Tuple[int, int], maze: List[List[str]]) -> bool:
    x, y = pos
    if 0 <= y < len(maze) and 0 <= x < len(maze[y]):
        return maze[y][x] != '+'
    return False

def get_neighbors(state: State, maze: List[List[str]]) -> List[State]:
    x, y = state.position
    directions = [(-1, 0, 'L'), (1, 0, 'R'), (0, -1, 'U'), (0, 1, 'D')]
    neighbors = []
    for dx, dy, move in directions:
        new_pos = (x + dx, y + dy)
        if is_valid_move(new_pos, maze):
            neighbors.append(State(new_pos, state.path + move))
    return neighbors

def solve_maze(maze_str: str) -> Tuple[str, int]:
    try:
        maze, start, end = parse_maze(maze_str)
    except ValueError as e:
        print(f"Error parsing maze: {e}")
        return "", 0
    
    if start == end:
        return "", 0
    
    initial_state = State(start)
    queue = deque([initial_state])
    visited = set([start])
    states_explored = 0

    while queue:
        current_state = queue.popleft()
        states_explored += 1

        if current_state.position == end:
            return current_state.path, states_explored

        for neighbor in get_neighbors(current_state, maze):
            if neighbor.position not in visited:
                visited.add(neighbor.position)
                queue.append(neighbor)

    return "", states_explored  # No solution found

def maze_solver(maze: str) -> int:
    # print(f"Solving maze...")
    solution, states_explored = solve_maze(maze)

    if solution == "" and states_explored == 0:
        # print("  S is already at X or maze is invalid")
        return 0
    elif solution:
        # print(f"  Solution moves: {len(solution)}")
        # print(f"  Solution: {solution}")
        # print(f"  States explored: {states_explored}")
        return len(solution)
    else:
        # print(f"  States explored: {states_explored}")
        # print(f"  No solution found")
        return 99999