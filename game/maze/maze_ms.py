import pygame
import sys
import json
import os
import re

# Initialize Pygame without display
pygame.display.init()
pygame.display.set_mode((1, 1))

# Color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Cell size for the maze
CELL_SIZE = 30

# Function to create maze in list of list
def create_maze(level, current_maze=None):
    if current_maze:
        return current_maze, None, None  # Return the current maze state

    maze = []
    start_pos = None
    end_pos = None
    for y, row in enumerate(level):
        maze_row = []
        for x, cell in enumerate(row):
            if cell == '+':
                maze_row.append('+')
            elif cell == ' ':
                maze_row.append(' ')
            elif cell == 'S':
                start_pos = (x, y)
                maze_row.append('S')
            elif cell == 'X':
                end_pos = (x, y)
                maze_row.append('X')
        maze.append(maze_row)
    return maze, start_pos, end_pos

def find_agent_position(maze):
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 'S':
                return (x, y)
    return None

def find_end_position(maze):
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 'X':
                return (x, y)
    return None

# Function to move the agent within the maze
def move_agent(maze, agent_pos, move):
    x, y = agent_pos
    new_pos = agent_pos
    target_cells = (' ', 'X')
    if move == 'U' and y > 0 and maze[y - 1][x] in target_cells:
        return (x, y - 1)
    elif move == 'D' and y + 1 < len(maze) and maze[y + 1][x] in target_cells:
        return (x, y + 1)
    elif move == 'L' and x > 0 and maze[y][x - 1] in target_cells:
        return (x - 1, y)
    elif move == 'R' and x + 1 < len(maze[y]) and maze[y][x + 1] in target_cells:
        return (x + 1, y)
    return new_pos

def update_maze(maze, old_pos, new_pos, end_pos):
    if old_pos != new_pos:
        maze[old_pos[1]][old_pos[0]] = ' '
    if new_pos == end_pos:
        maze[new_pos[1]][new_pos[0]] = 'X'
    else:
        maze[new_pos[1]][new_pos[0]] = 'S'

    return maze

# Function to draw the maze and save it as an image
def draw_maze(maze, output_path):
    height = len(maze)
    width = len(maze[0])
    screen = pygame.Surface((width * CELL_SIZE, height * CELL_SIZE))
    screen.fill(WHITE)  # Fill the background with white
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == '+':
                pygame.draw.rect(screen, BLACK, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif cell == 'S':
                pygame.draw.rect(screen, RED, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif cell == 'X':
                pygame.draw.rect(screen, GREEN, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.image.save(screen, output_path)

# Function to save level to a text file
def save_maze_to_file(maze, output_path):
    with open(output_path, 'w') as f:
        for row in maze:
            f.write(''.join(row) + '\n')

def extract_moves(input_string):
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

# Function to evaluate moves, calculate results, and manage output
def evaluate_moves(levels, last_move, model_name, output_base_dir, step, current_maze):
    results = []
    is_valid = False  # Initialize is_valid
    is_active = False

    level_num = last_move['level']
    level = levels[level_num - 1]
    print(f"Processing model {model_name}, maze, level {level_num}, step {step}")

    if step == 1 or current_maze is None:
        maze, start_pos, end_pos = create_maze(level)
    else:
        maze, _, _ = create_maze(level, current_maze)
        start_pos = find_agent_position(maze)
        end_pos = find_end_position(maze)

    extract_move = extract_moves(last_move['output'])
    if extract_move:
        new_pos = move_agent(maze, start_pos, extract_move)   
        maze = update_maze(maze, start_pos, new_pos, end_pos)  
    else:
        new_pos = start_pos

    # Save intermediate states
    image_dir = os.path.join(output_base_dir, "process_images",  model_name, "maze", f"level_{level_num}")
    level_dir = os.path.join(output_base_dir, "process_levels",  model_name, "maze", f"level_{level_num}")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(level_dir, exist_ok=True)

    image_path = os.path.join(image_dir, f"step_{step}.png")
    level_path = os.path.join(level_dir, f"step_{step}.txt")

    draw_maze(maze, image_path)
    save_maze_to_file(maze, level_path)

    if new_pos != start_pos:
        is_active = True

    if new_pos == end_pos:
        is_valid = True

    results.append({
        "model": model_name,
        "level": level_num,
        "output": extract_move,
        "is_active": is_active,
        "is_valid": is_valid,
        "step": step
    })

    return results, is_valid, maze

def main(last_move, output_dir_base, model_name, step, levels, current_level, step_states):
    results, is_valid, updated_maze = evaluate_moves(levels, last_move, model_name, output_dir_base, step, current_level)

    if not results:
        print("No valid results found.")
        return is_valid

    eval_dir = os.path.join(output_dir_base, "eval",  model_name, "maze")
    os.makedirs(eval_dir, exist_ok=True)
    eval_path = os.path.join(eval_dir, f'level_{results[0]["level"]}.jsonl')

    with open(eval_path, 'a') as f:  # Append to the file
        for result in results:
            json.dump(result, f)
            f.write('\n')

    return is_valid, updated_maze

if __name__ == "__main__":
    levels_path = sys.argv[1]
    moves_path = sys.argv[2]
    output_dir_base = sys.argv[3]
    model_name = sys.argv[4]
    step = int(sys.argv[5])
    levels = json.loads(sys.argv[6])  # Receive levels as a JSON string argument
    is_valid = main(levels_path, moves_path, output_dir_base, model_name, step, levels)
    sys.exit(0 if is_valid else 1)
