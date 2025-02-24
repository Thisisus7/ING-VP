import os
import sys
import csv
import json
from collections import defaultdict
sys.dont_write_bytecode = True

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import START_LEVEL, END_LEVEL
from solver import sudoku_solver, sokoban_solver, maze_solver, hanoi_solver, n_puzzle_solver, n_queens_solver

DENOMINATOR = END_LEVEL - START_LEVEL + 1

# ---------------------------- Sudoku, Hanoi ----------------------------
def process_jsonl(file_path, game):
    degree = 100

    if not os.path.exists(file_path):
        return 0
    # final state
    with open(file_path, 'r') as f:
        final_state = json.loads(f.readlines()[-1])

    if game == 'sudoku':
        degree = sudoku_solver.sudoku_solver(final_state)
    elif game == 'hanoi':
        step_num = hanoi_solver.hanoi_solver(final_state['position'])
        degree -= step_num*12.5
    elif game == 'n_puzzle':
        step_num = n_puzzle_solver.n_puzzle_solver(final_state['position'])
        degree -= step_num*12.5
    elif game == 'n_queens':
        comb_state = final_state['output'] + [final_state['position']]
        step_num = n_queens_solver.n_queens_solver(comb_state)
        degree -= step_num*14.3
    return degree if degree >=0 else 0

# ---------------------------- Sokoban & Maze ----------------------------
def process_txt(file_path, game):
    degree = 100
    if not os.path.exists(file_path):
        return 0
    with open(file_path, 'r') as f:
        final_state = f.read()
    if game == "sokoban":
        step_num = sokoban_solver.sokoban_solver(final_state)
    elif game == "maze":
        step_num = maze_solver.maze_solver(final_state)
    degree -= step_num*12.5
    return degree if degree >=0 else 0

def find_final_step(game_dir):
    max_num = -1
    max_file = ""
    
    for filename in os.listdir(game_dir):
        if filename.startswith("step_") and filename.endswith(".txt"):
            num = int(filename[5:-4])
            if num > max_num:
                max_num = num
                max_file = filename

    max_file = os.path.join(game_dir, max_file)
    return max_file if max_file else None

# --------------------------------------------------------------

def game_completion(game_dir, game):
    degree = 0
    levels = os.listdir(game_dir)
    for level in levels:
        file_path = os.path.join(game_dir, f'{level}')  # level_
        if game in ['sokoban', 'maze']:
            file_path = find_final_step(file_path)         # step_.txt
        degree += (process_txt(file_path, game) if game in ['sokoban', 'maze'] else process_jsonl(file_path, game))
    return round(degree / DENOMINATOR, 1)

def completion_degree(base_dir='outputs/multi_step'):
    games = ['maze', 'sokoban', 'n_queens', 'n_puzzle', 'hanoi', 'sudoku']
    output_dir = os.path.join(base_dir, 'final')
    os.makedirs(output_dir, exist_ok=True)

    for setting1 in os.listdir(base_dir):   # ["image_text", "text_only"]
        setting1_path = os.path.join(base_dir, setting1)
        if not os.path.isdir(setting1_path) or setting1 == 'final':
            continue
        
        for setting2 in os.listdir(setting1_path):  # ["base", "history"]
            setting2_path = os.path.join(setting1_path, setting2)
            if not os.path.isdir(setting2_path):
                continue
            
            level_path = os.path.join(setting2_path, 'process_levels')  # ["process_levels"]
            if not os.path.exists(level_path):
                continue

            degree_scores = defaultdict(dict)
            
            for model in os.listdir(level_path):  # ["model1", "model2"]
                model_path = os.path.join(level_path, model)
                for game in games:                # games
                    game_dir = os.path.join(model_path, game)
                    if os.path.exists(game_dir):
                        degree = game_completion(game_dir, game)
                        degree_scores[model][game] = degree
                    else:
                        degree_scores[model][game] = '-'

            combined_setting = f"{setting1}_{setting2}"
            # Generate degree scores CSV
            degree_output_file = os.path.join(output_dir, f'comp_{combined_setting}.csv')
            with open(degree_output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([''] + games + ['overall'])
                for model, game_scores in degree_scores.items():
                    overall_score = calculate_overall_score(game_scores)
                    writer.writerow([model] + [game_scores.get(game, '-') for game in games] + [overall_score])
            print(f"Generated {degree_output_file}")

def calculate_overall_score(scores):
    valid_scores = [scores.get(game, 0) if scores.get(game) != '-' else 0 for game in scores]
    return round(sum(valid_scores) / len(valid_scores), 1)

if __name__ == "__main__":
    completion_degree()