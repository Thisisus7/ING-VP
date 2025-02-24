import json
from config import GAMES

def sudoku_solver(final_state):
    degree = 100
    # finish state
    init_level_path = next((game['levels_path'] for game in GAMES if game['name'] == 'sudoku'), None)
    with open(init_level_path, 'r') as f:
        for line in f:
            obj = json.loads(line)
            if obj["level"] == final_state["level"]:
                init_state = obj

    # comparison
    for i in range(len(final_state['position'])):
        if final_state['position'][i] != init_state['solutions'][i]:
                degree -= 10

    return degree