import os
import json
import csv
import sys
sys.dont_write_bytecode = True
from collections import defaultdict
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import START_LEVEL, END_LEVEL

DENOMINATOR = END_LEVEL - START_LEVEL + 1

def process_jsonl(file_path):
    if not os.path.exists(file_path):
        return 0, 0
    
    total_count = 0
    active_count = 0
    last_valid = False
    
    with open(file_path, 'r') as f:
        for line in f:
            obj = json.loads(line)
            total_count += 1
            if obj.get('is_active', False):
                active_count += 1
            last_valid = obj.get('is_valid', False)
    
    active_ratio = active_count / total_count if total_count > 0 else 0
    return 1 if last_valid else 0, active_ratio

def calculate_scores(game_dir):
    valid_score = 0
    active_ratios = []  # contains active_ratio for each level
    
    for level in range(START_LEVEL, END_LEVEL + 1):
        file_path = os.path.join(game_dir, f'level_{level}.jsonl')
        valid, active_ratio = process_jsonl(file_path)
        valid_score += valid
        active_ratios.append(active_ratio)
    

    valid_score = round(valid_score / DENOMINATOR * 100, 1)
    active_score = round(sum(active_ratios) / len(active_ratios) * 100, 1)
    return valid_score, active_score

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
            
            valid_scores = defaultdict(dict)
            active_scores = defaultdict(dict)
            
            for model in os.listdir(eval_path):
                model_path = os.path.join(eval_path, model)
                for game in games:
                    game_dir = os.path.join(model_path, game)
                    if os.path.exists(game_dir):
                        valid_score, active_score = calculate_scores(game_dir)
                        valid_scores[model][game] = valid_score
                        active_scores[model][game] = active_score
                    else:
                        valid_scores[model][game] = '-'
                        active_scores[model][game] = '-'
            
            combined_setting = f"{setting1}_{setting2}"
            
            # Generate valid scores CSV
            valid_output_file = os.path.join(output_dir, f'{combined_setting}.csv')
            with open(valid_output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([''] + games)
                for model, game_scores in valid_scores.items():
                    writer.writerow([model] + [game_scores.get(game, '-') for game in games])
            print(f"Generated {valid_output_file}")
            
            # Generate active scores CSV
            active_output_file = os.path.join(output_dir, f'active_{combined_setting}.csv')
            with open(active_output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([''] + games)
                for model, game_scores in active_scores.items():
                    writer.writerow([model] + [game_scores.get(game, '-') for game in games])
            print(f"Generated {active_output_file}")

if __name__ == "__main__":
    generate_score()