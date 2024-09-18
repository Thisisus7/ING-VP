from typing import Dict, List, Tuple
from collections import deque

class State:
    def __init__(self, rods: Dict[str, List[str]], moves: List[Tuple[str, str]] = None):
        self.rods = rods
        self.moves = moves if moves is not None else []

    def __eq__(self, other):
        return self.rods == other.rods

    def __hash__(self):
        return hash(tuple(tuple(v) for v in self.rods.values()))

def is_valid_move(from_rod: List[str], to_rod: List[str]) -> bool:
    if not from_rod:
        return False
    if not to_rod or from_rod[-1] > to_rod[-1]:
        return True
    return False

def get_neighbors(state: State) -> List[State]:
    neighbors = []
    for from_rod in state.rods:
        for to_rod in state.rods:
            if from_rod != to_rod and is_valid_move(state.rods[from_rod], state.rods[to_rod]):
                new_rods = {k: v[:] for k, v in state.rods.items()}
                disk = new_rods[from_rod].pop()
                new_rods[to_rod].append(disk)
                new_moves = state.moves + [(from_rod, to_rod)]
                neighbors.append(State(new_rods, new_moves))
    return neighbors

def is_goal_state(state: State) -> bool:
    return all(len(rods) == 0 for rod, rods in state.rods.items() if rod != 'D') and len(state.rods['D']) == sum(len(rods) for rods in state.rods.values())

def solve_tower_of_hanoi(initial_state: Dict[str, List[str]]) -> Tuple[List[Tuple[str, str]], int]:
    start_state = State(initial_state)
    queue = deque([start_state])
    visited = set([start_state])
    states_explored = 0

    while queue:
        current_state = queue.popleft()
        states_explored += 1

        if is_goal_state(current_state):
            return current_state.moves, states_explored

        for neighbor in get_neighbors(current_state):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return [], states_explored  # No solution found

def hanoi_solver(initial_state: str) -> int:
    # print(f"Solving Tower of Hanoi...")
    solution, states_explored = solve_tower_of_hanoi(initial_state)

    if solution:
        # print(f"  Solution moves: {len(solution)}")
        # print(f"  Solution: {solution}")
        # print(f"  States explored: {states_explored}")
        return len(solution)
    else:
        # print(f"  States explored: {states_explored}")
        # print(f"  No solution found")
        return 99999