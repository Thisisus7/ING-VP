import pygame
import sys
import json
import os

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

# Function to load movement commands from a file
def load_moves(filename, current_step):
    moves = []
    with open(filename, 'r') as f:
        for line in f:
            move = json.loads(line)
            if move['step'] == current_step:
                moves.append(move)
    return moves

# Function to create the maze from a given level data
def create_maze(level):
    maze = []
    start_pos = None
    end_pos = None
    for y, row in enumerate(level):
        maze_row = []
        for x, cell in enumerate(row):
            if cell == '+':
                maze_row.append(1)
            elif cell == ' ':
                maze_row.append(0)
            elif cell == 'S':
                start_pos = (x, y)
                maze_row.append(0)
            elif cell == 'X':
                end_pos = (x, y)
                maze_row.append(0)
        maze.append(maze_row)
    return maze, start_pos, end_pos

# Function to move the agent within the maze
def move_agent(maze, agent_pos, move):
    x, y = agent_pos
    if move == 'U' and y > 0 and maze[y - 1][x] == 0:
        return (x, y - 1)
    elif move == 'D' and y + 1 < len(maze) and maze[y + 1][x] == 0:
        return (x, y + 1)
    elif move == 'L' and x > 0 and maze[y][x - 1] == 0:
        return (x - 1, y)
    elif move == 'R' and x + 1 < len(maze[y]) and maze[y][x + 1] == 0:
        return (x + 1, y)
    return agent_pos

# Function to draw the maze and save it as an image
def draw_maze(level, agent_pos, end_pos, output_path):
    height = len(level)
    width = len(level[0])
    screen = pygame.Surface((width * CELL_SIZE, height * CELL_SIZE))
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            color = WHITE if cell == ' ' else BLACK
            pygame.draw.rect(screen, color, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Draw the start and end positions
    pygame.draw.rect(screen, GREEN, pygame.Rect(end_pos[0] * CELL_SIZE, end_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, RED, pygame.Rect(agent_pos[0] * CELL_SIZE, agent_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.image.save(screen, output_path)

# Function to save level to a text file
def save_level_to_file(level, output_path):
    with open(output_path, 'w') as f:
        for row in level:
            f.write(row + '\n')

# Function to evaluate moves, calculate results, and manage output
def evaluate_moves(levels, moves, model_name, output_base_dir, step):
    results = []
    is_valid = False  # Initialize is_valid

    for move in moves:
        level_num = move['level']
        move_sequence = move['output']
        print(f"Processing level {level_num}, total levels: {len(levels)}")
        
        # Convert level number to index (0-based index)
        if level_num - 1 >= len(levels) or level_num - 1 < 0:
            print(f"Invalid level number: {level_num}")
            continue  # Skip invalid level numbers

        level = levels[level_num - 1]
        maze, start_pos, end_pos = create_maze(level)
        agent_pos = start_pos
        is_valid = True

        for move in move_sequence:
            agent_pos = move_agent(maze, agent_pos, move)
            if agent_pos == start_pos:
                is_valid = False
                break

        if agent_pos != end_pos:
            is_valid = False

        results.append({
            "model": model_name,
            "level": level_num,
            "output": move_sequence,
            "is_valid": is_valid,
            "step": step
        })

        # Save the image and level after running the moves
        image_dir = os.path.join(output_base_dir, "process_images", "base", model_name, "maze", f"level_{level_num}")
        level_dir = os.path.join(output_base_dir, "process_levels", "base", model_name, "maze", f"level_{level_num}")
        os.makedirs(image_dir, exist_ok=True)
        os.makedirs(level_dir, exist_ok=True)

        image_path = os.path.join(image_dir, f"step_{step}.png")
        level_path = os.path.join(level_dir, f"step_{step}.txt")

        draw_maze(level, agent_pos, end_pos, image_path)
        save_level_to_file(level, level_path)

    return results, is_valid  # Return results and is_valid

def main(levels_path, moves_path, output_dir_base, model_name, step, levels):
    moves = load_moves(moves_path, step)
    results, is_valid = evaluate_moves(levels, moves, model_name, output_dir_base, step)

    if not results:
        print("No valid results found.")
        return is_valid

    eval_dir = os.path.join(output_dir_base, "eval", "base", model_name, "maze")
    os.makedirs(eval_dir, exist_ok=True)
    eval_path = os.path.join(eval_dir, f'level_{results[0]["level"]}.jsonl')

    with open(eval_path, 'a') as f:  # Append to the file
        for result in results:
            json.dump(result, f)
            f.write('\n')

    return is_valid

if __name__ == "__main__":
    levels_path = sys.argv[1]
    moves_path = sys.argv[2]
    output_dir_base = sys.argv[3]
    model_name = sys.argv[4]
    step = int(sys.argv[5])
    levels = json.loads(sys.argv[6])  # Receive levels as a JSON string argument
    is_valid = main(levels_path, moves_path, output_dir_base, model_name, step, levels)
    sys.exit(0 if is_valid else 1)
