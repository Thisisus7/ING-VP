import os
import json
import csv
from collections import defaultdict

DENOMINATOR = 20

def process_jsonl(file_path):
    if not os.path.exists(file_path):
        return 0
    with open(file_path, 'r') as f:
        for line in f:
            pass
        last_obj = json.loads(line)
        return 1 if last_obj.get('is_valid', False) else 0

def calculate_score(game_dir):
    score = 0
    for level in range(1, 21):
        file_path = os.path.join(game_dir, f'level_{level}.jsonl')
        score += process_jsonl(file_path)
    return round(score / DENOMINATOR * 100, 1)

def generate_score(base_dir='outputs/multi_step'):
    games = ['maze', 'sokoban', 'n_queens', 'n_puzzle', 'hanoi', 'sudoku']
    output_dir = os.path.join(base_dir, 'final')
    os.makedirs(output_dir, exist_ok=True)

    for setting1 in os.listdir(base_dir):
        setting1_path = os.path.join(base_dir, setting1)
        if not os.path.isdir(setting1_path) or setting1 == 'final':
            continue

        for setting2 in os.listdir(setting1_path):
            setting2_path = os.path.join(setting1_path, setting2)
            if not os.path.isdir(setting2_path):
                continue

            eval_path = os.path.join(setting2_path, 'eval')
            if not os.path.exists(eval_path):
                continue

            scores = defaultdict(dict)
            for model in os.listdir(eval_path):
                model_path = os.path.join(eval_path, model)
                for game in games:
                    game_dir = os.path.join(model_path, game)
                    if os.path.exists(game_dir):
                        scores[model][game] = calculate_score(game_dir)
                    else:
                        scores[model][game] = '-'

            combined_setting = f"{setting1}_{setting2}"
            output_file = os.path.join(output_dir, f'{combined_setting}.csv')
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([''] + games)
                for model, game_scores in scores.items():
                    writer.writerow([model] + [game_scores.get(game, '-') for game in games])

            print(f"Generated {output_file}")