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
SCREEN_SIZE = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
CELL_SIZE = SCREEN_SIZE // 8

def create_game_state(level):
    board_size = level['board_size']
    first_queen = level['position']
    state = {
        'board_size': board_size,
        'queens': [first_queen]
    }
    return state

def extract_coordinates(input_string):
    if input_string:
        pattern = r'\{\s*"output":\s*(\[\s*(?:\[\d+,\s*\d+\]\s*,?\s*)*\])\s*\}' 
        lst = [0, 1, 2, 3, 4, 5, 6, 7]
        match = re.search(pattern, input_string)
        if match:
            json_string = match.group(0)
            try:
                move = json.loads(json_string)
                if isinstance(move, dict) and "output" in move:
                    coordinates = move["output"]
                    if (isinstance(coordinates, list) and
                        all(isinstance(coord, list) and
                            len(coord) == 2 and
                            all(isinstance(x, int) for x in coord) and
                            coord[0] in lst and
                            coord[1] in lst
                            for coord in coordinates)):
                        return coordinates
            except Exception as e:
                print(f"Error: {e}")
    return None

def is_valid_position(queen, queens):
    for q in queens:
        if (q[0] == queen[0] or              # same row
            q[1] == queen[1] or              # same column
            abs(q[0] - queen[0]) == abs(q[1] - queen[1])):  # same diagonal
            return False
    return True

def is_on_board(queen):
    return 0 <= queen[0] < 8 and 0 <= queen[1] < 8

def is_valid_move(queens, new_queens):
    valid_moves = []
    total_moves = 0
    active_moves = 0

    for new_queen in new_queens:
        total_moves += 1
        if is_on_board(new_queen) and is_valid_position(new_queen, queens):
            valid_moves.append(new_queen)
            active_moves += 1
    
    total_moves = 8 if total_moves < 8 else total_moves
    is_active = round(active_moves / total_moves * 100, 2) if total_moves > 0 else 0.0
    return valid_moves, is_active

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

def save_game_state_to_file(state, output_path, level):
    data = {
        "game": "n_queens",
        "level": level,
        "board_size": state['board_size'],
        "position": state['queens'][0],
        "output": state['queens'][1:]
    }
    
    with open(output_path, 'a') as f:
        json.dump(data, f)
        f.write('\n')

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

def evaluate_moves(levels, moves, model_name, output_base_dir):
    is_active = 0.0
    level_num = moves['level']
    print(f"Processing model {model_name}, n-queens, level {level_num}")
    levels = [json.loads(json_str) for json_str in levels[0]]  # convert string to dict
    level = next(l for l in levels if l['level'] == level_num)
    
    state = create_game_state(level)
    extract_move = extract_coordinates(moves['output'])
    if extract_move:
        valid_moves, is_active = is_valid_move(state['queens'], extract_move)
        state['queens'].extend(valid_moves)

    # Save intermediate states
    image_dir = os.path.join(output_base_dir, "process_images",  model_name, "n_queens")
    level_dir = os.path.join(output_base_dir, "process_levels",  model_name)
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(level_dir, exist_ok=True)

    image_path = os.path.join(image_dir, f"level_{level_num}.png")
    level_path = os.path.join(level_dir, "n_queens.jsonl")

    draw_game_state(state, image_path)
    save_game_state_to_file(state, level_path, level_num)

    is_valid = validate_solution(state['queens'])

    result = {
        "model": model_name,
        "level": level_num,
        "output": extract_move,
        "is_active": is_active,
        "is_valid": is_valid,
    }

    return result

def main(move, output_dir_base, model_name, levels):
    result= evaluate_moves(levels, move, model_name, output_dir_base)
    eval_dir = os.path.join(output_dir_base, "eval",  model_name)
    os.makedirs(eval_dir, exist_ok=True)
    eval_path = os.path.join(eval_dir, "n_queens.jsonl")

    with open(eval_path, 'a') as f:
        json.dump(result, f)
        f.write('\n')