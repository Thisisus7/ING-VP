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
TILE_SIZE = 32

# Load images
def load_images():
    images = {
        'box': pygame.image.load('game/sokoban/images/box.png'),
        'box_docked': pygame.image.load('game/sokoban/images/box_docked.png'),
        'dock': pygame.image.load('game/sokoban/images/dock.png'),
        'floor': pygame.image.load('game/sokoban/images/floor.png'),
        'wall': pygame.image.load('game/sokoban/images/wall.png'),
        'worker': pygame.image.load('game/sokoban/images/worker.png'),
        'worker_dock': pygame.image.load('game/sokoban/images/worker_dock.png')
    }
    return images

# Function to create game state
def create_game_state(level, current_state=None):
    if current_state:
        return current_state

    return [list(row) for row in level]

# Function to move the worker
def move_worker(state, direction):
    # Find worker position
    worker_pos = None
    for y, row in enumerate(state):
        for x, tile in enumerate(row):
            if tile in ('@', '+'):
                worker_pos = (x, y)
                break
        if worker_pos:
            break

    if not worker_pos:
        return state
    
    if direction not in ['U', 'D', 'L', 'R']:
        return state

    dx, dy = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}[direction]
    new_x, new_y = worker_pos[0] + dx, worker_pos[1] + dy
    next_x, next_y = new_x + dx, new_y + dy

    if state[new_y][new_x] in (' ', '.'):
        state[worker_pos[1]][worker_pos[0]] = ' ' if state[worker_pos[1]][worker_pos[0]] == '@' else '.'
        state[new_y][new_x] = '@' if state[new_y][new_x] == ' ' else '+'
    elif state[new_y][new_x] in ('$', '*') and state[next_y][next_x] in (' ', '.'):
        state[worker_pos[1]][worker_pos[0]] = ' ' if state[worker_pos[1]][worker_pos[0]] == '@' else '.'
        state[new_y][new_x] = '@' if state[new_y][new_x] == '$' else '+'
        state[next_y][next_x] = '$' if state[next_y][next_x] == ' ' else '*'

    return state

# Function to draw the game state and save it as an image
def draw_game_state(state, output_path):
    images = load_images()
    height = len(state)
    width = max(len(row) for row in state)
    screen = pygame.Surface((width * TILE_SIZE, height * TILE_SIZE))
    
    for y, row in enumerate(state):
        for x, tile in enumerate(row):
            if tile == '#':
                screen.blit(images['wall'], (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '.':
                screen.blit(images['dock'], (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '$':
                screen.blit(images['box'], (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '*':
                screen.blit(images['box_docked'], (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '@':
                screen.blit(images['worker'], (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '+':
                screen.blit(images['worker_dock'], (x * TILE_SIZE, y * TILE_SIZE))
            else:
                screen.blit(images['floor'], (x * TILE_SIZE, y * TILE_SIZE))
        # Fill the rest of the row with floor tiles if it's shorter than the maximum width
        for x in range(len(row), width):
            screen.blit(images['floor'], (x * TILE_SIZE, y * TILE_SIZE))
    
    pygame.image.save(screen, output_path)

# Function to save game state to a text file
def save_game_state_to_file(state, output_path):
    with open(output_path, 'w') as f:
        for row in state:
            f.write(''.join(row) + '\n')

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

def active_move(previous_state, state):
    return previous_state != state

def back_to_step(direction, step_states, state):
    previous_state = step_states.get(direction)
    if previous_state:
        return previous_state
    else:
        return state

# Function to evaluate moves, calculate results, and manage output
def evaluate_moves(levels, last_move, model_name, output_base_dir, step, current_state, step_states):
    results = []
    level_num = last_move['level']
    level = levels[level_num - 1]
    print(f"Processing model {model_name}, sokoban, level {level_num}, step {step}")

    state = create_game_state(level, current_state)
    previous_state = copy.deepcopy(state)
    direction = extract_move(last_move['output'])
    if direction:
        if isinstance(direction, int):
            state = back_to_step(direction, step_states, state)
        else:
            state = move_worker(state, direction)

    # Save intermediate states
    image_dir = os.path.join(output_base_dir, "process_images",  model_name, "sokoban", f"level_{level_num}")
    level_dir = os.path.join(output_base_dir, "process_levels",  model_name, "sokoban", f"level_{level_num}")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(level_dir, exist_ok=True)

    image_path = os.path.join(image_dir, f"step_{step}.png")
    level_path = os.path.join(level_dir, f"step_{step}.txt")

    draw_game_state(state, image_path)
    save_game_state_to_file(state, level_path)

    is_active = active_move(previous_state, state)
    is_valid = all('$' not in row for row in state)

    results.append({
        "model": model_name,
        "level": level_num,
        "output": direction,
        "is_active": is_active,
        "is_valid": is_valid,
        "step": step
    })

    return results, is_valid, state

def main(last_move, output_dir_base, model_name, step, levels, current_level, step_states):
    results, is_valid, updated_state = evaluate_moves(levels, last_move, model_name, output_dir_base, step, current_level, step_states)

    if not results:
        print("No valid results found.")
        return is_valid, None

    eval_dir = os.path.join(output_dir_base, "eval",  model_name, "sokoban")
    os.makedirs(eval_dir, exist_ok=True)
    eval_path = os.path.join(eval_dir, f'level_{results[0]["level"]}.jsonl')

    with open(eval_path, 'a') as f:  # Append to the file
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
    levels = json.loads(sys.argv[6])  # Receive levels as a JSON string argument
    is_valid, _ = main(levels_path, moves_path, output_dir_base, model_name, step, levels)
    sys.exit(0 if is_valid else 1)
