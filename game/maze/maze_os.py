import pygame
import sys
import json
import os

# Initialize Pygame
pygame.init()

# Color
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Cell size
CELL_SIZE = 30

# Read level file
def load_levels(filename):
    levels = []
    with open(filename, 'r') as f:
        current_level = []
        for line in f:
            line = line.strip()
            if line.startswith(';'):
                if current_level:
                    levels.append(current_level)
                    current_level = []
            elif line:  # add non-empty line only
                current_level.append(line)
        if current_level:
            levels.append(current_level)
    return levels

# Read movement
def load_moves(filename):
    moves = []
    with open(filename, 'r') as f:
        for line in f:
            moves.append(json.loads(line))
    return moves

# Create maze
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
                maze_row.append(0)
                start_pos = (x, y)
            elif cell == 'X':
                maze_row.append(0)
                end_pos = (x, y)
        maze.append(maze_row)
    return maze, start_pos, end_pos

# Draw maze
def draw_maze(screen, maze, agent_pos, end_pos):
    screen.fill(WHITE)
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 1:
                pygame.draw.rect(screen, BLACK, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Draw destination
    pygame.draw.rect(screen, GREEN, (end_pos[0]*CELL_SIZE, end_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Draw agent
    pygame.draw.rect(screen, RED, (agent_pos[0]*CELL_SIZE, agent_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    pygame.display.flip()

# Move agent
def move_agent(maze, agent_pos, move):
    x, y = agent_pos
    if move == 'U' and y > 0 and y-1 < len(maze) and x < len(maze[y-1]) and maze[y-1][x] == 0:
        return (x, y-1)
    elif move == 'D' and y+1 < len(maze) and x < len(maze[y+1]) and maze[y+1][x] == 0:
        return (x, y+1)
    elif move == 'L' and x > 0 and maze[y][x-1] == 0:
        return (x-1, y)
    elif move == 'R' and x+1 < len(maze[y]) and maze[y][x+1] == 0:
        return (x+1, y)
    return agent_pos

# Main game loop
def play_game(levels, moves):
    results = []
    for move in moves:
        level_num = move['level']
        move_sequence = move['output']
        model_name = move['model']
        level = levels[level_num - 1]
        maze, start_pos, end_pos = create_maze(level)
        agent_pos = start_pos

        # Screen size
        width = len(maze[0]) * CELL_SIZE
        height = len(maze) * CELL_SIZE
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f"Maze Level {level_num} - Model {model_name}")

        is_valid = True

        draw_maze(screen, maze, agent_pos, end_pos)  # Initial draw

        # If no move sequence, just save the initial state
        if not move_sequence:
            image_path = f"outputs/one_step/eval/maze_results/level_{level_num}_model_{model_name}.png"
            pygame.image.save(screen, image_path)
            results.append({
                "level": level_num,
                "model": model_name,
                "output": move_sequence,
                "is_valid": False,  # No moves made, so not valid
                "image": image_path
            })
            continue

        for move in move_sequence:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            new_pos = move_agent(maze, agent_pos, move)
            if new_pos == agent_pos:
                is_valid = False
                break
            agent_pos = new_pos
            draw_maze(screen, maze, agent_pos, end_pos)
            pygame.time.wait(100)  # Watch

        if agent_pos != end_pos:
            is_valid = False

        # Save last frame
        if not os.path.exists("outputs/one_step/eval/maze_results"):
            os.makedirs("outputs/one_step/eval/maze_results")
        image_path = f"outputs/one_step/eval/maze_results/level_{level_num}_model_{model_name}.png"
        pygame.image.save(screen, image_path)

        results.append({
            "level": level_num,
            "model": model_name,
            "output": move_sequence,
            "is_valid": is_valid,
            "image": image_path
        })

    return results

# Save results
def save_results(results):
    with open("outputs/one_step/eval/maze.jsonl", 'w') as f:
        for result in results:
            json.dump(result, f)
            f.write('\n')

# Main
def main():
    if not os.path.exists("outputs/one_step/eval/maze_results"):
        os.makedirs("outputs/one_step/eval/maze_results")
    if not os.path.exists("outputs/one_step/eval"):
        os.makedirs("outputs/one_step/eval")

    levels = load_levels("data/maze/levels_50.txt")
    moves = load_moves(r"outputs\one_step\models\formatted\maze.jsonl")
    results = play_game(levels, moves)
    save_results(results)

if __name__ == "__main__":
    main()
