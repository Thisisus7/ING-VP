import os
import csv
import sys
from collections import defaultdict
sys.dont_write_bytecode = True

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.one_step import score as one_score
from src.one_step import completion as one_completion
from src.multi_step import score as multi_score
from src.multi_step import completion as multi_completion

def process_csv_files(directories):
    metrics = ['acc', 'eff', 'comp']
    all_scores = {metric: defaultdict(lambda: defaultdict(list)) for metric in metrics}
    tasks = ["maze", "sokoban", "n_queens", "n_puzzle", "hanoi", "sudoku", "overall"]

    for directory in directories:
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                metric = next((m for m in metrics if filename.startswith(f"{m}_")), None)
                if metric is None:
                    continue  # Skip files that don't match our metric prefixes

                file_path = os.path.join(directory, filename)
                with open(file_path, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        model = row['']  # Assuming the model name is in the first unnamed column
                        for task in tasks:
                            if row[task] != '-':
                                try:
                                    score = float(row[task])
                                    all_scores[metric][model][task].append(score)
                                except ValueError:
                                    pass  # Ignore non-numeric values

    # Compute averages
    averages = {metric: defaultdict(dict) for metric in metrics}
    for metric in metrics:
        for model, task_scores in all_scores[metric].items():
            for task, scores in task_scores.items():
                if scores:
                    averages[metric][model][task] = sum(scores) / len(scores)
                else:
                    averages[metric][model][task] = '-'

    return averages

def write_results(averages, output_directory):
    tasks = ["maze", "sokoban", "n_queens", "n_puzzle", "hanoi", "sudoku", "overall"]
    
    os.makedirs(output_directory, exist_ok=True)

    for metric, model_scores in averages.items():
        output_file = os.path.join(output_directory, f"{metric}_summary.csv")
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(["Model"] + tasks)
            
            # Write scores for each model
            for model, scores in model_scores.items():
                score_values = [f"{scores.get(task, '-'):.2f}" if scores.get(task, '-') != '-' else '-' for task in tasks]
                writer.writerow([model] + score_values)
        
        print(f"Results for {metric} written to {output_file}")


def summarize():
    one_score.generate_score()
    one_completion.completion_degree()
    multi_score.generate_score()
    multi_completion.completion_degree()
    directories = ["outputs/multi_step/final", "outputs/one_step/final"]
    output_directory = "outputs/summary"
    averages = process_csv_files(directories)
    write_results(averages, output_directory)

if __name__ == "__main__":
    summarize()