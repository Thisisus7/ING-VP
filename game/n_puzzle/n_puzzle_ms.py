import pygame
import sys
import json
import os
import re
import copy

# Initialize Pygame without display
pygame.init()
pygame.display.init()
pygame.display.set_mode((1, 1))

# Constants
BACKGROUND = (240, 248, 255)  # Light blue background
TILE_COLOR = (255, 182, 193)  # Light pink tiles
TEXT_COLOR = (0, 0, 0)  # Black text
WINDOW_SIZE = (400, 400)
TILE_SIZE = 80
PADDING = 20

# Create font object
FONT = pygame.font.Font(None, 36)

def create_game_state(level, current_state=None):
    if current_state:
        return current_state

    n = level['n']
    position = level['position']
    state = {
        'n': n,
        'position': position
    }
    return state


def extract_move(input_string):
    if input_string:
        pattern = r'\{.*?\}'
        match = re.search(pattern, input_string)
        if match:
            json_string = match.group(0)
            try:
                move = json.loads(json_string)
                return move["output"]
            except Exception as e:
                print(f"Error: {e}")
    return None
def is_valid_move(state, tile):
    if not isinstance(tile, int):  # tile should be an integer
        return False    
    if tile > 15:                  # tile should less than 16
        return False

    n = state['n']
    position = state['position']
    zero_row, zero_col = None, None
    tile_row, tile_col = None, None
    # Find the empty tile (0) and the tile to be moved
    for row in range(n):
        for col in range(n):
            if position[row][col] == 0:
                zero_row, zero_col = row, col
            elif position[row][col] == tile:
                tile_row, tile_col = row, col
    # Check if the tile is adjacent to the empty space
    if (abs(zero_row - tile_row) == 1 and zero_col == tile_col) or \
       (abs(zero_col - tile_col) == 1 and zero_row == tile_row):
        return True
    
    return False
def apply_move(state, tile):
    n = state['n']
    position = [row[:] for row in state['position']]  # Create a copy of the position
    
    zero_row, zero_col = None, None
    tile_row, tile_col = None, None
    
    # Find the empty tile (0) and the tile to be moved
    for row in range(n):
        for col in range(n):
            if position[row][col] == 0:
                zero_row, zero_col = row, col
            elif position[row][col] == tile:
                tile_row, tile_col = row, col
    
    # Swap the tile with the empty space
    position[zero_row][zero_col], position[tile_row][tile_col] = position[tile_row][tile_col], position[zero_row][zero_col]
    
    return {'n': n, 'position': position}
def draw_tile(surface, value, x, y):
    pygame.draw.rect(surface, TILE_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(surface, (0, 0, 0), (x, y, TILE_SIZE, TILE_SIZE), 2)
    if value != 0:
        text = FONT.render(str(value), True, TEXT_COLOR)
        text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
        surface.blit(text, text_rect)

def draw_game_state(state, output_path):
    surface = pygame.Surface(WINDOW_SIZE)
    surface.fill(BACKGROUND)

    n = state['n']
    position = state['position']

    for row in range(n):
        for col in range(n):
            value = position[row][col]
            x = PADDING + col * (TILE_SIZE + 5)
            y = PADDING + row * (TILE_SIZE + 5)
            draw_tile(surface, value, x, y)

    pygame.image.save(surface, output_path)

def save_game_state_to_file(state, output_path, level, step, model):
    data = {
        "game": "n_puzzle",
        "level": level,
        "n": state['n'],
        "position": state['position'],
        "step": step,
        "model": model
    }
    
    with open(output_path, 'a') as f:
        json.dump(data, f)
        f.write('\n')



def active_move(previous_state, state):
    return previous_state != state

def validate_solution(state):
    n = state['n']
    position = state['position']
    expected = list(range(1, n*n)) + [0]
    flattened = [num for row in position for num in row]
    return flattened == expected

def evaluate_moves(levels, last_move, model_name, output_base_dir, step, current_state):
    results = []

    level_num = last_move['level']
    level = json.loads(levels[0][level_num-1])
    if step == 1:
        # For the first step, get the correct level data from the loaded levels
        state = create_game_state(level)
    else:
        # For subsequent steps, use the current_state directly
        state = current_state

    previous_state = copy.deepcopy(state)

    print(f"Processing model {model_name}, n_puzzle, level {level_num}, step {step}")

    extract_move_result = extract_move(last_move['output'])
    if extract_move_result and is_valid_move(state, extract_move_result):
        state = apply_move(state, extract_move_result)

    # Save intermediate states
    image_dir = os.path.join(output_base_dir, "process_images",  model_name, "n_puzzle", f"level_{level_num}")
    level_dir = os.path.join(output_base_dir, "process_levels",  model_name, "n_puzzle")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(level_dir, exist_ok=True)

    image_path = os.path.join(image_dir, f"step_{step}.png")
    level_path = os.path.join(level_dir, f"level_{level_num}.jsonl")

    draw_game_state(state, image_path)
    save_game_state_to_file(state, level_path, level_num, step, model_name)

    is_active = active_move(previous_state, state)
    is_valid = validate_solution(state)

    results.append({
        "model": model_name,
        "level": level_num,
        "output": extract_move_result,
        "is_active": is_active,
        "is_valid": is_valid,
        "step": step
    })

    return results, is_valid, state

# Main function (placeholder for now)
def main(last_move, output_dir_base, model_name, step, levels, current_level, step_states):    
    if step > 1 and current_level is None:
        # Load the previous state from the process_levels file
        level_num = last_move['level']
        level_path = os.path.join(output_dir_base, "process_levels",  model_name, "n_puzzle", f"level_{level_num}.jsonl")
        with open(level_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                if data['step'] == step - 1:
                    current_level = {'n': data['n'], 'position': data['position']}
                    break

    results, is_valid, updated_state = evaluate_moves(levels, last_move, model_name, output_dir_base, step, current_level)

    if not results:
        print("No valid results found.")
        return False, None

    eval_dir = os.path.join(output_dir_base, "eval",  model_name, "n_puzzle")
    os.makedirs(eval_dir, exist_ok=True)
    eval_path = os.path.join(eval_dir, f'level_{results[0]["level"]}.jsonl')

    with open(eval_path, 'a') as f:
        for result in results:
            json.dump(result, f)
            f.write('\n')

    return is_valid, updated_state

if __name__ == "__main__":
    levels_path = sys.argv[1]
    moves_path = sys.argv[2]
    output_dir_base = sys.argv[3]
    model_name = sys.argv[4]
    step = int(sys.argv[5])
    levels = json.loads(sys.argv[6])
    is_valid, _ = main(levels_path, moves_path, output_dir_base, model_name, step, levels)
    sys.exit(0 if is_valid else 1)