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
def create_maze(level):
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

def extract_moves(input_string):
    if input_string:
        pattern = r'(?s)\{.*?"output"\s*:\s*"(.*?)".*?\}'
        match = re.search(pattern, input_string)
        if match:
            json_string = match.group(0)
            try: 
                move = json.loads(json_string)
                return move["output"]
            except Exception as e:
                print(f"Error: {e}")
    return None

# Function to move the agent within the maze
def move_agent(maze, agent_pos, moves, end_pos):
    x, y = agent_pos
    total_moves = 0
    active_moves = 0
    path = [agent_pos]
    reached_end = False

    for move in moves:
        if reached_end:
            break
        total_moves += 1
        new_x, new_y = x, y
        if move == 'U' and y > 0:
            new_y -= 1
        elif move == 'D' and y + 1 < len(maze):
            new_y += 1
        elif move == 'L' and x > 0:
            new_x -= 1
        elif move == 'R' and x + 1 < len(maze[y]):
            new_x += 1
        
        if maze[new_y][new_x] in [' ', 'X']:  # Allow moving to empty space or end position
            x, y = new_x, new_y
            active_moves += 1
            path.append((x, y))
            if (x, y) == end_pos:
                reached_end = True

    total_moves = max(8, total_moves)
    is_active = round(active_moves / total_moves * 100, 2) if total_moves > 0 else 0.0
    
    return (x, y), is_active, path, reached_end

def update_maze(maze, path, end_pos, reached_end):
    for x, y in path[:-1]:
        maze[y][x] = '.'  # Mark the path
    
    last_pos = path[-1]
    if reached_end:
        maze[last_pos[1]][last_pos[0]] = 'X'  # Keep 'X' if reached
    else:
        maze[last_pos[1]][last_pos[0]] = 'S'  # Place 'S' at the final position

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

# Function to evaluate moves, calculate results, and manage output
def evaluate_moves(levels, moves, model_name, output_base_dir):
    is_valid = False
    is_active = 0.0
    level_num = moves['level']
    level = levels[level_num - 1]

    print(f"Processing model {model_name}, maze, level {level_num}")
    
    maze, start_pos, end_pos = create_maze(level)
    extract_move = extract_moves(moves['output'])
    if extract_move:
        new_pos, is_active, path, reached_end = move_agent(maze, start_pos, extract_move, end_pos)   
        maze = update_maze(maze, path, end_pos, reached_end)  
        
        # Check if the path is valid and reaches the end
        is_valid = reached_end and all(maze[y][x] in [' ', 'S', 'X', '.'] for x, y in path)
    else:
        new_pos = start_pos
        path = [start_pos]
        reached_end = False

    # Save intermediate states
    image_dir = os.path.join(output_base_dir, "process_images",  model_name, "maze")
    level_dir = os.path.join(output_base_dir, "process_levels",  model_name, "maze")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(level_dir, exist_ok=True)
    image_path = os.path.join(image_dir, f"level_{level_num}.png")
    level_path = os.path.join(level_dir, f"level_{level_num}.txt")

    draw_maze(maze, image_path)
    save_maze_to_file(maze, level_path)

    if new_pos == end_pos:
        is_valid = True

    result = {
        "model": model_name,
        "level": level_num,
        "output": extract_move,
        "is_active": is_active,
        "is_valid": is_valid,
    }

    return result

def main(move, output_dir_base, model_name, levels):
    result = evaluate_moves(levels, move, model_name, output_dir_base)

    eval_dir = os.path.join(output_dir_base, "eval",  model_name)
    os.makedirs(eval_dir, exist_ok=True)
    eval_path = os.path.join(eval_dir, "maze.jsonl")

    with open(eval_path, 'a') as f:  # Append to the file
        json.dump(result, f)
        f.write('\n')
