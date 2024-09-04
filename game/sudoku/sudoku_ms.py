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
SCREEN_SIZE = 450
GRID_SIZE = 9
CELL_SIZE = SCREEN_SIZE // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

def create_game_state(level, current_state=None):
    if current_state:
        return current_state

    return {
        'position': level['position'],
        'solution': level['solutions'],
        'clue_numbers': level['clue_numbers'],
        'current_board': level['position']
    }

def draw_grid(screen):
    for i in range(GRID_SIZE + 1):
        thickness = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, SCREEN_SIZE), thickness)
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (SCREEN_SIZE, i * CELL_SIZE), thickness)

def draw_numbers(screen, board, solution, added_positions):
    font = pygame.font.Font(None, 36)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            num = board[row * GRID_SIZE + col]
            if num != '0':
                if (row, col) in added_positions:
                    color = BLUE if num == solution[row * GRID_SIZE + col] else RED
                else:
                    color = BLACK
                text = font.render(num, True, color)
                screen.blit(text, (col * CELL_SIZE + CELL_SIZE // 3, row * CELL_SIZE + CELL_SIZE // 4))

def draw_game_state(state, output_path, added_positions):
    screen = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
    screen.fill(WHITE)
    draw_grid(screen)
    draw_numbers(screen, state['current_board'], state['solution'], added_positions)
    pygame.image.save(screen, output_path)

def extract_move(input_string):
    if input_string:
        pattern = r'\{((?:[^{}]|\{[^{}]*\})*)\}'
        match = re.search(pattern, input_string)
        if match:
            json_string = match.group(0)
            try:
                move = json.loads(json_string)
                return move["output"]
            except Exception as e:
                print(f"Error: {e}")
    return None

def update_game_state(state, move):
    added_positions = set()
    new_board = list(state['current_board'])
    pos = next(iter(move))
    value = move[pos]
    row, col = int(pos[0]), int(pos[1])
    index = row * GRID_SIZE + col
    if new_board[index] == '0':
        new_board[index] = str(value)
        added_positions.add((row, col))
    state['current_board'] = ''.join(new_board)
    return state, added_positions

def back_to_step(extracted_move, step_states, state):
    previous_state = step_states.get(extracted_move)
    if previous_state:
        return previous_state
    else:
        return state

def is_valid_move(extracted_move):
    key = list(extracted_move.keys())[0]
    value = list(extracted_move.values())[0]
    if not key.isdigit() or len(key) != 2:
        return False
    if not isinstance(value, int):
        return False
    if int(key[0]) > 8 or int(key[1]) > 8 or value > 9 or value < 1:
        return False
    
    return True

def active_move(previous_state, state):
    return previous_state != state

def evaluate_moves(levels, last_move, model_name, output_base_dir, step, current_state, step_states):
    results = []

    level_num = last_move['level']
    level = json.loads(levels[0][level_num-1])
    # level = next(l for l in json.loads(levels[0]) if l['level'] == level_num)
    print(f"Processing model {model_name}, sudoku, level {level_num}, step {step}")

    state = create_game_state(level, current_state)
    previous_state = copy.deepcopy(state)

    extracted_move = extract_move(last_move['output'])
    if extracted_move:
        if isinstance(extracted_move, int):
            state = back_to_step(extracted_move, step_states, state)
            added_positions = set()
        elif is_valid_move(extracted_move):
            state, added_positions = update_game_state(state, extracted_move)
        else:
            added_positions = set()
    else:
        added_positions = set()

    # Save intermediate states
    image_dir = os.path.join(output_base_dir, "process_images",  model_name, "sudoku", f"level_{level_num}")
    level_dir = os.path.join(output_base_dir, "process_levels",  model_name, "sudoku")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(level_dir, exist_ok=True)

    image_path = os.path.join(image_dir, f"step_{step}.png")
    level_path = os.path.join(level_dir, f"level_{level_num}.jsonl")

    draw_game_state(state, image_path, added_positions)
    save_game_state_to_file(state, level_path, level_num, step, extracted_move)

    is_active = active_move(previous_state, state)
    is_valid = validate_solution(state['current_board'], state['solution'])

    results.append({
        "model": model_name,
        "level": level_num,
        "output": extracted_move,
        "is_active": is_active,
        "is_valid": is_valid,
        "step": step
    })

    return results, is_valid, state

def validate_solution(board, solution):
    return board == solution

def save_game_state_to_file(state, output_path, level, step, output):
    data = {
        "game": "sudoku",
        "level": level,
        "clue_numbers": state['clue_numbers'],
        "position": state['position'],
        "step": step,
        "output": output
    }
    
    with open(output_path, 'a') as f:
        json.dump(data, f)
        f.write('\n')

def main(last_move, output_dir_base, model_name, step, levels, current_level, step_states):    
    if step > 1 and current_level is None:
        # Load the previous state from the process_levels file
        level_num = last_move['level']
        level_path = os.path.join(output_dir_base, "process_levels",  model_name, "sudoku", f"level_{level_num}.jsonl")
        with open(level_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                if data['step'] == step - 1:
                    current_level = {
                        'position': data['position'],
                        'solutions': data['solutions'],
                        'clue_numbers': data['clue_numbers'],
                        'current_board': data['current_board']
                    }
                    break

    results, is_valid, updated_state = evaluate_moves(levels, last_move, model_name, output_dir_base, step, current_level, step_states)

    if not results:
        print("No valid results found.")
        return False, None

    eval_dir = os.path.join(output_dir_base, "eval",  model_name, "sudoku")
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
