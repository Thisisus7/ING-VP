import os
import json
import csv
from collections import defaultdict

def process_jsonl(file_path):
    """Process a single JSONL file and calculate the percentage of valid entries."""
    if not os.path.exists(file_path):
        return 0
    
    valid_count = 0
    total_count = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            obj = json.loads(line)
            total_count += 1
            if obj.get('is_valid', False):
                valid_count += 1
    
    return round(valid_count / total_count * 100, 1) if total_count > 0 else 0

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
        scores = process_models(eval_path, games)
        save_scores_to_csv(scores, output_dir, setting1, games)

def process_models(eval_path, games):
    """Process all models for a given evaluation path."""
    scores = defaultdict(dict)
    
    for model in os.listdir(eval_path):
        model_path = os.path.join(eval_path, model)
        print(f"Processing model: {model}")
        
        for game in games:
            game_file = os.path.join(model_path, f"{game}.jsonl")
            if os.path.exists(game_file):
                scores[model][game] = process_jsonl(game_file)
            else:
                scores[model][game] = '-'
    
    return scores

def save_scores_to_csv(scores, output_dir, setting, games):
    """Save the calculated scores to a CSV file."""
    output_file = os.path.join(output_dir, f"{setting}.csv")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([''] + games)
        for model, game_scores in scores.items():
            writer.writerow([model] + [game_scores.get(game, '-') for game in games])
    
    print(f"Generated {output_file}")

if __name__ == "__main__":
    generate_score()