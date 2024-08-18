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
SCREEN_SIZE = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
CELL_SIZE = SCREEN_SIZE // 8

def create_game_state(level, current_state=None):
    if current_state:
        return current_state

    board_size = level['board_size']
    first_queen = level['position']
    state = {
        'board_size': board_size,
        'queens': [first_queen]
    }
    return state

def draw_chessboard(screen, board_size):
    for row in range(board_size):
        for col in range(board_size):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_queen(screen, row, col, color):
    pygame.draw.circle(screen, color, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

def draw_game_state(state, output_path):
    screen = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
    draw_chessboard(screen, state['board_size'])
    
    for i, queen in enumerate(state['queens']):
        color = RED if i == 0 else SKY_BLUE
        draw_queen(screen, queen[0], queen[1], color)
    
    pygame.image.save(screen, output_path)

def is_valid_move(queens, new_queen):
    if not isinstance(new_queen[0], int) or not isinstance(new_queen[1], int):
        return False
    if not(new_queen[0] < 8 and new_queen[1] < 8):
        return False
    for queen in queens:
        if (queen[0] == new_queen[0] or  # same row
            queen[1] == new_queen[1] or  # same column
            abs(queen[0] - new_queen[0]) == abs(queen[1] - new_queen[1])):  # same diagonal
            return False
    return True

def active_move(previous_state, state):
    return previous_state != state

def extract_coordinates(input_string):
    if input_string:
        pattern = r'\{.*?\}'
        lst = [0, 1, 2, 3, 4, 5, 6, 7]
        match = re.search(pattern, input_string)
        if match:
            json_string = match.group(0)
            try:
                move = json.loads(json_string)
                if isinstance(move, dict) and "output" in move:
                    coordinate = move["output"]
                    if (isinstance(coordinate, list) and 
                        len(coordinate) == 2 and 
                        all(isinstance(x, int) for x in coordinate) and 
                        coordinate[0] in lst and 
                        coordinate[1] in lst):
                        return coordinate
            except Exception as e:
                print(f"Error: {e}")
    return None

def back_to_step(extracted_move, step_states, state):
    previous_state = step_states.get(extracted_move)
    if previous_state:
        return previous_state
    else:
        return state

def evaluate_moves(levels, last_move, model_name, output_base_dir, step, current_state, step_states):
    results = []
    level_num = last_move['level']
    levels = [json.loads(json_str) for json_str in levels[0]]  # convert string to dict
    level = next(l for l in levels if l['level'] == level_num)
    print(f"Processing model {model_name}, n_queens, level {level_num}, step {step}")

    state = create_game_state(level, current_state)
    previous_state = copy.deepcopy(state['queens'])

    extract_move = extract_coordinates(last_move['output'])
    if extract_move and is_valid_move(state['queens'], extract_move):
        state['queens'].append(extract_move)
    elif extract_move and isinstance(extract_move, int):
        state['queen'] = back_to_step(extract_move, step_states, state['queen'])

    # Save intermediate states
    image_dir = os.path.join(output_base_dir, "process_images",  model_name, "n_queens", f"level_{level_num}")
    level_dir = os.path.join(output_base_dir, "process_levels",  model_name, "n_queens")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(level_dir, exist_ok=True)

    image_path = os.path.join(image_dir, f"step_{step}.png")
    level_path = os.path.join(level_dir, f"level_{level_num}.jsonl")

    draw_game_state(state, image_path)
    save_game_state_to_file(state, level_path, level_num, step)

    is_active = active_move(previous_state, state['queens'])
    is_valid = validate_solution(state['queens'])

    results.append({
        "model": model_name,
        "level": level_num,
        "output": extract_move,
        "is_active": is_active,
        "is_valid": is_valid,
        "step": step
    })

    return results, is_valid, state

def validate_solution(queens):
    if len(queens) != 8:
        return False

    for i in range(len(queens)):
        for j in range(i + 1, len(queens)):
            if queens[i][0] == queens[j][0] or queens[i][1] == queens[j][1]:
                return False
            if abs(queens[i][0] - queens[j][0]) == abs(queens[i][1] - queens[j][1]):
                return False

    return True

def save_game_state_to_file(state, output_path, level, step):
    data = {
        "game": "n_queens",
        "level": level,
        "board_size": state['board_size'],
        "position": state['queens'][0],
        "step": step,
        "output": state['queens'][1:]
    }
    
    with open(output_path, 'a') as f:
        json.dump(data, f)
        f.write('\n')


def main(last_move, output_dir_base, model_name, step, levels, current_level, step_states):
    if step > 1 and current_level is None:
        # Load the previous state from the process_levels file
        level_num = last_move['level']
        level_path = os.path.join(output_dir_base, "process_levels",  model_name, "n_queens", f"level_{level_num}.jsonl")
        with open(level_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                if data['step'] == step - 1:
                    current_level = {
                        'board_size': data['board_size'],
                        'position': data['position'],
                        'queens': [data['position']] + data['output']
                    }
                    break

    results, is_valid, updated_state = evaluate_moves(levels, last_move, model_name, output_dir_base, step, current_level, step_states)

    if not results:
        print("No valid results found.")
        return False, None

    eval_dir = os.path.join(output_dir_base, "eval",  model_name, "n_queens")
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