import os
import sys
import json
import csv
from collections import defaultdict
sys.dont_write_bytecode = True

def process_jsonl(file_path):
    """Process a single JSONL file and calculate the percentage of valid entries and average eff score."""
    if not os.path.exists(file_path):
        return 0, 0
    
    valid_count = 0
    total_count = 50
    eff_score_sum = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            obj = json.loads(line)
            # total_count += 1
            if obj.get('is_valid', False):
                valid_count += 1
            eff_score_sum += obj.get('is_active', 0)
    
    valid_percentage = round(valid_count / total_count * 100, 1) if total_count > 0 else 0
    eff_score = round(eff_score_sum / total_count, 1) if total_count > 0 else 0
    return valid_percentage, eff_score

def generate_score(base_dir='outputs/one_step'):
    """Generate scores for each game and model, and save results to CSV files."""
    games = ['maze', 'sokoban', 'n_queens', 'n_puzzle', 'hanoi', 'sudoku']
    output_dir = os.path.join(base_dir, 'final')
    os.makedirs(output_dir, exist_ok=True)
    
    for setting1 in os.listdir(base_dir):
        setting1_path = os.path.join(base_dir, setting1)
        if not os.path.isdir(setting1_path) or setting1 == 'final':
            continue
        
        eval_path = os.path.join(setting1_path, 'eval')
        if not os.path.exists(eval_path):
            continue
        
        print(f"Processing setting: {setting1}")
        valid_scores, eff_scores = process_models(eval_path, games)
        save_scores_to_csv(valid_scores, output_dir, setting1, games, "valid")
        save_scores_to_csv(eff_scores, output_dir, setting1, games, "eff")

def process_models(eval_path, games):
    """Process all models for a given evaluation path."""
    valid_scores = defaultdict(dict)
    eff_scores = defaultdict(dict)
    
    for model in os.listdir(eval_path):
        model_path = os.path.join(eval_path, model)
        print(f"Processing model: {model}")
        
        for game in games:
            game_file = os.path.join(model_path, f"{game}.jsonl")
            if os.path.exists(game_file):
                valid_score, eff_score = process_jsonl(game_file)
                valid_scores[model][game] = valid_score
                eff_scores[model][game] = eff_score
            else:
                valid_scores[model][game] = '-'
                eff_scores[model][game] = '-'
    
    return valid_scores, eff_scores

def calculate_overall_score(scores, games):
    """Calculate the overall score for a model."""
    valid_scores = []
    for game in games:
        score = scores.get(game, '-')
        if score != '-':
            valid_scores.append(score)
        else:
            valid_scores.append(0)
    return round(sum(valid_scores) / len(games), 1)

def save_scores_to_csv(scores, output_dir, setting, games, score_type):
    """Save the calculated scores to a CSV file."""
    file_prefix = "eff_" if score_type == "eff" else "acc_"
    output_file = os.path.join(output_dir, f"{file_prefix}{setting}.csv")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([''] + games + ['overall'])
        for model, game_scores in scores.items():
            overall_score = calculate_overall_score(game_scores, games)
            writer.writerow([model] + [game_scores.get(game, '-') for game in games] + [overall_score])
    
    print(f"Generated {output_file}")

if __name__ == "__main__":
    generate_score()
