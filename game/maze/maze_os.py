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

# Function to move the agent within the maze
def move_agent(maze, agent_pos, moves):
    x, y = agent_pos
    total_moves = 0
    active_moves = 0

    for move in moves:
        total_moves += 1
        if move == 'U' and y > 0 and maze[y - 1][x] == ' ':
            y -= 1
            active_moves += 1
        elif move == 'D' and y + 1 < len(maze) and maze[y + 1][x] == ' ':
            y += 1
            active_moves += 1
        elif move == 'L' and x > 0 and maze[y][x - 1] == ' ':
            x -= 1
            active_moves += 1
        elif move == 'R' and x + 1 < len(maze[y]) and maze[y][x + 1] == ' ':
            x += 1
            active_moves += 1

    is_active = round(active_moves / total_moves * 100, 2) if total_moves > 0 else 0.0
    
    return (x, y), is_active

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

# Function to evaluate moves, calculate results, and manage output
def evaluate_moves(levels, moves, model_name, output_base_dir):
    is_valid = False
    is_active = 0.0
    level_num = moves['level']
    level = levels[level_num - 1]

    maze, start_pos, end_pos = create_maze(level)
    extract_move = extract_moves(moves['output'])
    if extract_move:
        new_pos, is_active = move_agent(maze, start_pos, extract_move)   
        maze = update_maze(maze, start_pos, new_pos, end_pos)  
    else:
        new_pos = start_pos

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