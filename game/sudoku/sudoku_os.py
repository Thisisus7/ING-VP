import pygame
import sys
import json
import os
import re

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

def extract_move(input_string):
    if input_string:
        # pattern = r'\{((?:[^{}]|\{[^{}]*\})*)\}'
        pattern = r'\{\s*"output":\s*\{([^}]*)\}\s*\}'
        match = re.search(pattern, input_string)
        if match:
            json_string = match.group(0)
            try:
                move = json.loads(json_string)
                return move["output"]
            except Exception as e:
                print(f"Error: {e}")

def update_game_state(state, moves):
    added_positions = set()
    new_board = list(state['position'])
    total_moves = 0
    active_moves = 0

    for pos,value in moves.items():
        total_moves += 1
        move_active = False

        row, col = int(pos[0]), int(pos[1])
        index = row * GRID_SIZE + col
        if new_board[index] == '0':
            new_board[index] = str(value)
            added_positions.add((row, col))
            move_active = True 

        if move_active:
            active_moves += 1

        state['position'] = ''.join(new_board)

    total_moves = 10 if total_moves < 10 else total_moves
    is_active = round(active_moves / total_moves * 100, 2) if total_moves > 0 else 0.0

    return state, added_positions, is_active

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
    draw_numbers(screen, state['position'], state['solutions'], added_positions)
    pygame.image.save(screen, output_path)

def is_valid_move(extracted_moves):
    valid_moves = {}

    for key, value in extracted_moves.items():
        if not key.isdigit() or len(key) != 2:
            continue
        if not isinstance(value, int):
            continue
        if int(key[0]) > 8 or int(key[1]) > 8 or value > 9 or value < 1:
            continue

        valid_moves[key] = value

    return valid_moves

def save_game_state_to_file(state, output_path, level, output):
    data = {
        "game": "sudoku",
        "level": level,
        "clue_numbers": state['clue_numbers'],
        "position": state['position'],
        "output": output
    }
    
    with open(output_path, 'a') as f:
        json.dump(data, f)
        f.write('\n')

def validate_solution(board, solution):
    return board == solution

def evaluate_moves(levels, last_move, model_name, output_base_dir):
    is_active = 0.0
    level_num = last_move['level']
    print(f"Processing model {model_name}, sudoku, level {level_num}")

    state = json.loads(levels[0][level_num-1])

    extracted_move = extract_move(last_move['output'])
    if extracted_move:
        extracted_move =  is_valid_move(extracted_move)
        state, added_positions, is_active = update_game_state(state, extracted_move)
    else:
        added_positions = set()

    # Save intermediate states
    image_dir = os.path.join(output_base_dir, "process_images",  model_name, "sudoku")
    level_dir = os.path.join(output_base_dir, "process_levels",  model_name)
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(level_dir, exist_ok=True)
    image_path = os.path.join(image_dir, f"level_{level_num}.png")
    level_path = os.path.join(level_dir, "sudoku.jsonl")

    draw_game_state(state, image_path, added_positions)
    save_game_state_to_file(state, level_path, level_num, extracted_move)

    is_valid = validate_solution(state['position'], state['solutions'])

    result = {
        "model": model_name,
        "level": level_num,
        "output": extracted_move,
        "is_active": is_active,
        "is_valid": is_valid,
    }

    return result


def main(move, output_dir_base, model_name, levels):
    result = evaluate_moves(levels, move, model_name, output_dir_base)

    eval_dir = os.path.join(output_dir_base, "eval",  model_name, )
    os.makedirs(eval_dir, exist_ok=True)
    eval_path = os.path.join(eval_dir, "sudoku.jsonl")

    with open(eval_path, 'a') as f:
        json.dump(result, f)
        f.write('\n')