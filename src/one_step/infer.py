import os
import sys
sys.dont_write_bytecode = True
import json
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.model import QwenVLChatInferencer, BLIP2Inferencer, GPT4oInferencer, GeminiInferencer, GPT4VInference, GPT4TurboInference
from src.config import GAMES, START_LEVEL, END_LEVEL, OUTPUT_OS_DIR, OUTPUT_TEXT_OS_DIR
from src.multi_step.prompt_text_level import add_level_to_prompt
from src.one_step.score import generate_score
# game
from game.maze import maze_os
from game.sokoban import sokoban_os
from game.n_queens import n_queens_os
from game.sudoku import sudoku_os
from game.hanoi import hanoi_os
from game.n_puzzle import n_puzzle_os
from multiprocessing import Pool

# Load levels from a file
def load_levels(filename):
    levels = []
    current_level = []

    with open(filename, 'r') as f:
        for line in f:
            line = line.rstrip('\n')  # Remove only the trailing newline
            if line.lstrip().startswith(';'):  # Check for level separator without removing leading spaces
                if current_level:
                    levels.append(current_level)
                    current_level = []
            elif line or line.isspace():  # Include empty lines that may contain only spaces
                current_level.append(line)
        if current_level:
            levels.append(current_level)
    
    return levels

# Load the prompt template from a file
def load_prompt(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read().strip()

# Factory function to create inferencers based on model name
def create_inferencer(model_name):
    inferencer_classes = {
        'blip2': BLIP2Inferencer,
        'qwen_vl_chat': QwenVLChatInferencer,
        'gpt4o': GPT4oInferencer,
        'gpt4v': GPT4VInference,
        'gemini_15_pro': GeminiInferencer,
        'gpt4turbo': GPT4TurboInference,
        # Add more model inferencer mappings here
    }
    return inferencer_classes[model_name]()


# Save the model output to a JSON file
def save_output(path, model_name, game_name, level, output):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    output_data = {
        "model": model_name,
        "game": game_name,
        "level": level,
        "output": output
    }
    with open(path, 'a', encoding='utf-8') as file:  # Append to the file
        json.dump(output_data, file, ensure_ascii=False)
        file.write('\n')

def process_level(prompt, output_dir, model_name, game, use_text, inferencer, level, levels):

    level_output_path = os.path.join(output_dir, "models", model_name, f"{game['name']}.jsonl")

    if use_text:
        prompt = add_level_to_prompt(prompt, game, level, 1, output_dir, model_name)
        image_path = "Null"
    else:
        image_path = game["level_image_path"].format(level)

    output = inferencer.infer('', prompt, image_path, 0)
    save_output(level_output_path, model_name, game["name"], level, output)
    evaluation(game["name"], level, model_name, level_output_path, levels, output_dir)

def inference(game, model_name, inferencer, levels, use_text, processes_nums):
    if use_text:
        output_dir = OUTPUT_TEXT_OS_DIR
        prompt_path = game["text_prompt_path"]
    else:
        output_dir = OUTPUT_OS_DIR
        prompt_path = game["prompt_path"]

    prompt = load_prompt(prompt_path)

    levels_to_process = list(range(START_LEVEL, END_LEVEL + 1))
    args_list = [(prompt, output_dir, model_name, game, use_text, inferencer, level, levels) for level in levels_to_process]

    with Pool(processes=processes_nums) as pool:  # You can adjust the number of processes as needed
        results = pool.starmap(process_level, args_list)

# Function to evaluate the game using the model output
def evaluation(game_name, level_number, model_name, moves_path, levels, output_dir):
    game_functions = {
        "maze": maze_os.main,
        "sokoban": sokoban_os.main,
        "n_queens": n_queens_os.main,
        "sudoku": sudoku_os.main,
        "hanoi": hanoi_os.main,
        "n_puzzle": n_puzzle_os.main,
    }

    # Read only the last line from the moves file
    with open(moves_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data["level"] == level_number:
               move = data

    game_functions[game_name](
        move=move,
        output_dir_base=output_dir,
        model_name=model_name,
        levels=levels,
    )


def main():
    parser = argparse.ArgumentParser(description="Inference mode")
    parser.add_argument('--mode', choices=["image", "text"], default="text",
                        help='Inference mode: image-text (default), or text-only')
    parser.add_argument('--model-name', choices=['qwen_vl_chat', 'gpt4o', 'claude35', 'gpt4v', 'qwen_vl_max', 'gemini_15_pro', 'blip2'], default='claude35',
                        help='Inference mode: base_image (default), history_image, base_text, or history_text')
    parser.add_argument('--processes-nums', type=int, default=4,
                        help='Number of processes to use for parallel inference.')
    args = parser.parse_args()

    inferencer = create_inferencer(args.model_name)
    if args.model_name in ['qwen_vl_chat', 'blip2']:
        inferencer.load_model()

    for game in GAMES:
        levels = load_levels(game["levels_path"])

        if args.mode == 'image':
            inference(game, args.model_name, inferencer, levels, use_text=False, processes_nums=args.processes_nums)
        elif args.mode == 'text':
            inference(game, args.model_name, inferencer, levels, use_text=True, processes_nums=args.processes_nums)

    generate_score()

if __name__ == "__main__":
    main()