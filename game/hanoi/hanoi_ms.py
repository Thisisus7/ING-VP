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

def create_game_state(level, current_state=None):
    if current_state:
        return current_state

    position = level['position']
    state = {rod: position[rod] for rod in 'ABCD'}
    return state

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

def is_valid_move(state, source, destination):
    if not source in state or not destination in state:                    # if not A, B, C, D
        return False
    if not state[source]:                                                  # if no element in source
        return False
    if state[destination] and state[source][-1] < state[destination][-1]:  # if source < destination
        return False
    return True

def is_active_move(previous_state, current_state):
    return previous_state != current_state

def extract_move(input_string):
    if input_string:
        pattern = r'\{.*?\}'
        match = re.search(pattern, input_string)
        if match:
            json_string = match.group(0)
            try:
                move = json.loads(json_string)
                return move["output"][0], move["output"][1]
            except Exception as e:
                print(f"Error: {e}")
    return None

def validate_solution(state):
    return len(state['D']) == 5 and state['D'] == ['a', 'b', 'c', 'd', 'e']

def save_game_state_to_file(state, output_path, level, step):
    data = {
        "game": "hanoi",
        "level": level,
        "step": step,
        "position": {rod: state[rod] for rod in 'ABCD'}
    }
    
    with open(output_path, 'a') as f:
        json.dump(data, f)
        f.write('\n')

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
    print(f"Processing model {model_name}, hanoi, level {level_num}, step {step}")

    state = create_game_state(level, current_state)
    previous_state = copy.deepcopy(state)

    extract_move_result = extract_move(last_move['output'])
    if extract_move_result and len(extract_move_result) == 2:
        source, destination = extract_move_result
        if is_valid_move(state, source, destination):
            disk = state[source].pop()
            state[destination].append(disk)

    is_active = is_active_move(previous_state, state)
    # Save intermediate states
    image_dir = os.path.join(output_base_dir, "process_images",  model_name, "hanoi", f"level_{level_num}")
    level_dir = os.path.join(output_base_dir, "process_levels",  model_name, "hanoi")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(level_dir, exist_ok=True)

    image_path = os.path.join(image_dir, f"step_{step}.png")
    level_path = os.path.join(level_dir, f"level_{level_num}.jsonl")

    draw_game_state(state, image_path)
    save_game_state_to_file(state, level_path, level_num, step)

    is_valid = validate_solution(state)

    results.append({
        "model": model_name,
        "level": level_num,
        "output": f"{source}{destination}" if extract_move_result else None,
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
        level_path = os.path.join(output_dir_base, "process_levels",  model_name, "hanoi", f"level_{level_num}.jsonl")
        with open(level_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                if data['step'] == step - 1:
                    current_level = {'position': data['position']}
                    break

    results, is_valid, updated_state = evaluate_moves(levels, last_move, model_name, output_dir_base, step, current_level)

    if not results:
        print("No valid results found.")
        return False, None

    eval_dir = os.path.join(output_dir_base, "eval",  model_name, "hanoi")
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
