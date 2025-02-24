import heapq
from typing import List, Set, Tuple, FrozenSet, Dict
from collections import deque

class State:
    def __init__(self, player: Tuple[int, int], boxes: FrozenSet[Tuple[int, int]], pushes: int = 0, path: str = ""):
        self.player = player
        self.boxes = boxes
        self.pushes = pushes
        self.path = path

    def __eq__(self, other):
        return self.player == other.player and self.boxes == other.boxes

    def __hash__(self):
        return hash((self.player, self.boxes))

def parse_level(level_str: str) -> Tuple[Set[Tuple[int, int]], FrozenSet[Tuple[int, int]], FrozenSet[Tuple[int, int]], Tuple[int, int]]:
    lines = level_str.split('\n')
    walls = set()
    boxes = set()
    goals = set()
    player = None
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == '#':
                walls.add((x, y))
            elif char in ['$', '*']:
                boxes.add((x, y))
            if char in ['.', '*', '+']:
                goals.add((x, y))
            if char in ['@', '+']:
                player = (x, y)
    return walls, frozenset(boxes), frozenset(goals), player

def is_valid_move(pos: Tuple[int, int], walls: Set[Tuple[int, int]]) -> bool:
    return pos not in walls

def get_neighbors(state: State, walls: Set[Tuple[int, int]], reverse: bool = False) -> List[State]:
    x, y = state.player
    directions = [(-1, 0, 'R' if reverse else 'L'), (1, 0, 'L' if reverse else 'R'),
                  (0, -1, 'D' if reverse else 'U'), (0, 1, 'U' if reverse else 'D')]
    neighbors = []
    for dx, dy, move in directions:
        new_pos = (x + dx, y + dy)
        if is_valid_move(new_pos, walls):
            if reverse:
                if new_pos in state.boxes:
                    old_box_pos = (new_pos[0] + dx, new_pos[1] + dy)
                    if is_valid_move(old_box_pos, walls) and old_box_pos not in state.boxes:
                        new_boxes = frozenset(box if box != new_pos else old_box_pos for box in state.boxes)
                        neighbors.append(State(new_pos, new_boxes, state.pushes + 1, move + state.path))
                else:
                    neighbors.append(State(new_pos, state.boxes, state.pushes, move + state.path))
            else:
                if new_pos in state.boxes:
                    new_box_pos = (new_pos[0] + dx, new_pos[1] + dy)
                    if is_valid_move(new_box_pos, walls) and new_box_pos not in state.boxes:
                        new_boxes = frozenset(box if box != new_pos else new_box_pos for box in state.boxes)
                        neighbors.append(State(new_pos, new_boxes, state.pushes + 1, state.path + move))
                else:
                    neighbors.append(State(new_pos, state.boxes, state.pushes, state.path + move))
    return neighbors

def bidirectional_search(start: State, goal_boxes: FrozenSet[Tuple[int, int]], walls: Set[Tuple[int, int]]) -> Tuple[str, int]:
    forward_queue = deque([start])
    backward_queue = deque([State(start.player, goal_boxes)])
    forward_visited = {start: ""}
    backward_visited = {State(start.player, goal_boxes): ""}
    states_explored = 0

    while forward_queue and backward_queue:
        # Forward search
        for _ in range(len(forward_queue)):
            current_state = forward_queue.popleft()
            states_explored += 1

            if current_state.boxes == goal_boxes:
                return current_state.path, states_explored

            if current_state in backward_visited:
                return current_state.path + backward_visited[current_state][::-1], states_explored

            for neighbor in get_neighbors(current_state, walls):
                if neighbor not in forward_visited:
                    forward_visited[neighbor] = neighbor.path
                    forward_queue.append(neighbor)

        # Backward search
        for _ in range(len(backward_queue)):
            current_state = backward_queue.popleft()
            states_explored += 1

            if current_state in forward_visited:
                return forward_visited[current_state] + current_state.path[::-1], states_explored

            for neighbor in get_neighbors(current_state, walls, reverse=True):
                if neighbor not in backward_visited:
                    backward_visited[neighbor] = neighbor.path
                    backward_queue.append(neighbor)

    return "", states_explored  # No solution found

def is_level_finished(boxes: FrozenSet[Tuple[int, int]], goals: FrozenSet[Tuple[int, int]]) -> bool:
    return boxes == goals

def solve_level(level_str: str) -> Tuple[str, int]:
    walls, boxes, goals, player = parse_level(level_str)
    
    if is_level_finished(boxes, goals):
        return "", 0  # Level is already finished

    initial_state = State(player, boxes)
    solution, states_explored = bidirectional_search(initial_state, goals, walls)
    return solution, states_explored

def sokoban_solver(level: str) -> int:
    # print(f"Solving level...")
    solution, states_explored = solve_level(level)

    if solution == "" and states_explored == 0:
        # print("  Level is already finished")
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