import os
import sys
sys.dont_write_bytecode = True
import json
import argparse

from model import QwenVLChatInferencer, BLIP2Inferencer
from config import GAMES, MODELS, START_LEVEL, END_LEVEL, MAX_STEPS, OUTPUT_IMAGE_BASE_DIR, OUTPUT_IMAGE_HIS_DIR, OUTPUT_TEXT_BASE_DIR, OUTPUT_TEXT_HIS_DIR
from multi_step.prompt_history import add_conversation_history
from multi_step.prompt_text_level import add_level_to_prompt
from multi_step.score import generate_score
# game
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from game.maze import maze_ms
from game.sokoban import sokoban_ms
from game.n_queens import n_queens_ms
from game.sudoku import sudoku_ms
from game.hanoi import hanoi_ms
from game.n_puzzle import n_puzzle_ms


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

# Save the model output to a JSON file
def save_output(path, model_name, game_name, level, step, output):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    output_data = {
        "model": model_name,
        "game": game_name,
        "level": level,
        "step": step,
        "output": output
    }
    with open(path, 'a', encoding='utf-8') as file:  # Append to the file
        json.dump(output_data, file, ensure_ascii=False)
        file.write('\n')

# Factory function to create inferencers based on model name
def create_inferencer(model_name):
    inferencer_classes = {
        'blip2': BLIP2Inferencer,
        # Add more model inferencer mappings here
    }
    return inferencer_classes[model_name]()

# Process each game level with the specified model inferencer
def inference(game, model_name, inferencer, levels, use_history, use_text):
    if use_history and use_text:
        output_dir = OUTPUT_TEXT_HIS_DIR
        prompt_path = game["text_prompt_ms_history_path"]
    elif use_history:
        output_dir = OUTPUT_IMAGE_HIS_DIR
        prompt_path = game["prompt_ms_history_path"]
    elif use_text:
        output_dir = OUTPUT_TEXT_BASE_DIR
        prompt_path = game["text_prompt_ms_path"]
    else:
        output_dir = OUTPUT_IMAGE_BASE_DIR
        prompt_path = game["prompt_ms_path"]
    
    prompt = load_prompt(prompt_path)
    level_states = {}
    
    for level in range(START_LEVEL, END_LEVEL + 1):
        step = 1
        is_valid = False
        level_output_path = os.path.join(output_dir, "models", model_name, game["name"], f"level_{level}.jsonl")

        while step <= MAX_STEPS and not is_valid:
            if step == 1:
                if use_text:  # use text
                    prompt = add_level_to_prompt(prompt, game, level, step, output_dir, model_name)
                    image_path = "Null"
                else:         # use image
                    image_path = game["level_image_path"].format(level)
            else:
                if use_text:  # use text
                    prompt = add_level_to_prompt(prompt, game, level, step, output_dir, model_name)
                    image_path = "Null"
                else:         # use image
                    image_path = os.path.join(
                        output_dir,
                        "process_images",
                        model_name,
                        game["name"],
                        f"level_{level}",
                        f"step_{step-1}.png"
                    )

            current_prompt = add_conversation_history(prompt, model_name, game["name"], level) if use_history else prompt

            output = inferencer.infer(current_prompt, image_path)

            save_output(level_output_path, model_name, game["name"], level, step, output)
            # save_output(level_output_path, model_name, game["name"], level, step, output)

            # Evaluate the game with the model output
            current_level = level_states.get(level) if step > 1 else None
            is_valid, updated_level = evaluation(game["name"], level, model_name, level_output_path, step, levels, current_level, output_dir)

            level_states[level] = updated_level
            
            if is_valid:
                break

            step += 1
        
    level_states.clear()

# Function to evaluate the game using the model output
def evaluation(game_name, level, model_name, moves_path, step, levels, current_level, output_dir):
    game_functions = {
        "maze": maze_ms.main,
        "sokoban": sokoban_ms.main,
        "n_queens": n_queens_ms.main,
        "sudoku": sudoku_ms.main,
        "hanoi": hanoi_ms.main,
        "n_puzzle": n_puzzle_ms.main
    }

    # Read only the last line from the moves file
    with open(moves_path, 'r') as f:
        last_move = json.loads(f.readlines()[-1])

    # Call the appropriate function based on game_name
    is_valid, updated_level = game_functions[game_name](
        last_move=last_move,
        output_dir_base=output_dir,
        model_name=model_name,
        step=step,
        levels=levels,
        current_level=current_level
    )

    return is_valid, updated_level

# Main function to load models and process games
def main():
    parser = argparse.ArgumentParser(description="Inference mode")
    parser.add_argument('--mode', choices=['base_image', 'history_image', 'base_text', 'history_text'], default='base_image',
                        help='Inference mode: base_image (default), history_image, base_text, or history_text')
    args = parser.parse_args()
    
    for model_name in MODELS:
        inferencer = create_inferencer(model_name)
        inferencer.load_model()
        
        for game in GAMES:
            levels = load_levels(game["levels_path"])
            
            if args.mode == 'base_image':
                inference(game, model_name, inferencer, levels, use_history=False, use_text=False)
            elif args.mode == 'history_image':
                inference(game, model_name, inferencer, levels, use_history=True, use_text=False)
            elif args.mode == 'base_text':
                inference(game, model_name, inferencer, levels, use_history=False, use_text=True)
            elif args.mode == 'history_text':
                inference(game, model_name, inferencer, levels, use_history=True, use_text=True)
        
        inferencer.cleanup()

    generate_score()

if __name__ == "__main__":
    main()
