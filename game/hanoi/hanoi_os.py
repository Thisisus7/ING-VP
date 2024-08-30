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
BACKGROUND_COLOR = (255, 255, 255)
TOWER_COLOR = (0, 0, 0)
DISK_COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 128, 0), (0, 0, 255)]
TEXT_COLOR = (0, 0, 0)  # Text color
DISK_TEXT_COLOR = (0, 0, 0)  # Disk text color

WIDTH, HEIGHT = 800, 600
DISK_HEIGHT = 30
TOWER_WIDTH = 20
DISK_WIDTHS = [150, 120, 90, 60, 30]
MAX_DISKS = 5
TOWER_BASE = HEIGHT - 100  # Tower base position
TOWER_POSITIONS = {
    "A": (100, 100),
    "B": (300, 100),
    "C": (500, 100),
    "D": (700, 100)
}

def create_game_state(level):
    position = level['position']
    state = {rod: position[rod] for rod in 'ABCD'}
    return state

def extract_move(input_string):
    if input_string:
        pattern = r'\{\s*"output":\s*(\[\s*(?:"[A-Z]{2}"\s*(?:,\s*"[A-Z]{2}"\s*)*)\])\s*\}'
        match = re.search(pattern, input_string)
        if match:
            json_string = match.group(0)
            try:
                move = json.loads(json_string)
                return move["output"]
            except Exception as e:
                print(f"Error: {e}")
    return None

def is_valid_move(state, source, destination):
    if not source in state or not destination in state:                    # if not A, B, C, D
        return False
    if not state[source]:                                                  # if no element in source
        return False
    if state[destination] and state[source][-1] < state[destination][-1]:  # if source < destination
        return False
    return True

def draw_game_state(state, output_path):
    screen = pygame.Surface((WIDTH, HEIGHT))
    screen.fill(BACKGROUND_COLOR)

    font = pygame.font.Font(None, 72)
    disk_font = pygame.font.Font(None, 36)
    
    for rod, (x, _) in TOWER_POSITIONS.items():
        pygame.draw.line(screen, TOWER_COLOR, (x, TOWER_BASE), (x, 100), TOWER_WIDTH)

        # Add labels to towers
        text = font.render(rod, True, TEXT_COLOR)
        text_rect = text.get_rect(center=(x, HEIGHT - 50))
        screen.blit(text, text_rect)
        
        for j, disk in enumerate(state[rod]):
            disk_index = ord(disk) - ord('a')
            disk_size = DISK_WIDTHS[disk_index]
            disk_y = TOWER_BASE - (j + 1) * (DISK_HEIGHT + 5)
            disk_color = DISK_COLORS[disk_index]
            pygame.draw.rect(screen, disk_color, (x - disk_size // 2, disk_y, disk_size, DISK_HEIGHT))
    
            # Add letters on disks
            disk_text = disk_font.render(disk, True, DISK_TEXT_COLOR)
            disk_text_rect = disk_text.get_rect(center=(x, disk_y + DISK_HEIGHT // 2))
            screen.blit(disk_text, disk_text_rect)

    pygame.image.save(screen, output_path)

def save_game_state_to_file(state, output_path, level):
    data = {
        "game": "hanoi",
        "level": level,
        "position": {rod: state[rod] for rod in 'ABCD'}
    }
    
    with open(output_path, 'a') as f:
        json.dump(data, f)
        f.write('\n')

def validate_solution(state):
    return len(state['D']) == 5 and state['D'] == ['a', 'b', 'c', 'd', 'e']

def evaluate_moves(levels, last_move, model_name, output_base_dir):
    level_num = last_move['level']
    level = json.loads(levels[0][level_num-1])

    print(f"Processing model {model_name}, hanoi, level {level_num}")

    state = create_game_state(level)
        
    total_moves = 0
    active_moves = 0
    source, destination = None, None

    extract_move_results = extract_move(last_move['output'])
    if extract_move_results:
        for extract_move_result in extract_move_results:
            source, destination = extract_move_result
            total_moves += 1
            if is_valid_move(state, source, destination):
                previous_state = (state[source][-1] if state[source] else None)
                disk = state[source].pop()
                state[destination].append(disk)
                if previous_state != (state[source][-1] if state[source] else None):
                    active_moves += 1

    
    total_moves = 8 if total_moves < 8 else total_moves
    is_active = round(active_moves / total_moves * 100, 2) if total_moves > 0 else 0.0

    # Save intermediate states
    image_dir = os.path.join(output_base_dir, "process_images",  model_name, "hanoi")
    level_dir = os.path.join(output_base_dir, "process_levels",  model_name)
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(level_dir, exist_ok=True)
    image_path = os.path.join(image_dir, f"level_{level_num}.png")
    level_path = os.path.join(level_dir, "hanoi.jsonl")

    draw_game_state(state, image_path)
    save_game_state_to_file(state, level_path, level_num)

    is_valid = validate_solution(state)

    result = {
        "model": model_name,
        "level": level_num,
        "output": extract_move_results if extract_move_results else None,
        "is_active": is_active,
        "is_valid": is_valid,
    }

    return result

def main(move, output_dir_base, model_name, levels):
    result = evaluate_moves(levels, move, model_name, output_dir_base)

    eval_dir = os.path.join(output_dir_base, "eval",  model_name)
    os.makedirs(eval_dir, exist_ok=True)
    eval_path = os.path.join(eval_dir, "hanoi.jsonl")

    with open(eval_path, 'a') as f:
        json.dump(result, f)
        f.write('\n')