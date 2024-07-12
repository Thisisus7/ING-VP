import json
import pygame
import os

# Constants for the game
TILE_SIZE = 32
MOVE_DELAY = 200  # Milliseconds between moves

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

# Load levels from levels.txt
def load_levels(filename='data/sokoban/levels_50.txt'):
    with open(filename, 'r') as file:
        levels = file.read().split(';')[1:]
    parsed_levels = []
    for level in levels:
        level = [row for row in level.strip().split('\n') if row.strip()]
        parsed_levels.append(level)
    return parsed_levels

# Parse JSONL moves
def parse_moves(filename='outputs/one_step/models/formatted/sokoban.jsonl'):
    with open(filename, 'r') as file:
        moves = [json.loads(line) for line in file]
    return moves

# Save evaluation results
def save_eval_results(eval_results, filename='outputs/one_step/eval/sokoban.jsonl'):
    with open(filename, 'w') as file:
        for result in eval_results:
            file.write(json.dumps(result) + '\n')

# Initialize Pygame
pygame.init()

def draw_level(level, images, screen):
    for y, row in enumerate(level):
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

def move_worker(level, direction):
    # Find worker position
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile in ('@', '+'):
                worker_pos = (x, y)
                break

    dx, dy = 0, 0
    if direction == 'U':
        dy = -1
    elif direction == 'D':
        dy = 1
    elif direction == 'L':
        dx = -1
    elif direction == 'R':
        dx = 1

    new_x, new_y = worker_pos[0] + dx, worker_pos[1] + dy
    next_x, next_y = new_x + dx, new_y + dy

    def is_floor_or_dock(tile):
        return tile in ('.', ' ')

    if level[new_y][new_x] in (' ', '.'):
        # Move worker to the new position
        level[worker_pos[1]][worker_pos[0]] = ' ' if level[worker_pos[1]][worker_pos[0]] == '@' else '.'
        level[new_y][new_x] = '@' if level[new_y][new_x] == ' ' else '+'
    elif level[new_y][new_x] in ('$','*'):
        # Move box and worker if possible
        if is_floor_or_dock(level[next_y][next_x]):
            level[worker_pos[1]][worker_pos[0]] = ' ' if level[worker_pos[1]][worker_pos[0]] == '@' else '.'
            level[new_y][new_x] = '@' if level[new_y][new_x] == '$' else '+'
            level[next_y][next_x] = '$' if level[next_y][next_x] == ' ' else '*'

def run_game():
    levels = load_levels()
    moves = parse_moves()
    images = load_images()
    eval_results = []

    if not os.path.exists('outputs/one_step/eval/sokoban_results'):
        os.makedirs('outputs/one_step/eval/sokoban_results')

    for move in moves:
        level_index = move['level'] - 1
        move_sequence = move['output']
        model_name = move['model']
        level = [list(row) for row in levels[level_index]]

        # Set screen size based on level dimensions
        screen_width = max(len(row) for row in level) * TILE_SIZE
        screen_height = len(level) * TILE_SIZE
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(f'Sokoban - Level {move["level"]} - Model {model_name}')
        clock = pygame.time.Clock()

        # If no move sequence, just save the initial state
        if not move_sequence:
            image_path = f'outputs/one_step/eval/sokoban_results/level_{move["level"]}_model_{model_name}.png'
            draw_level(level, images, screen)
            pygame.display.flip()
            pygame.image.save(screen, image_path)
            eval_results.append({
                "level": move['level'],
                "model": model_name,
                "output": move_sequence,
                "is_valid": False,  # No moves made, so not valid
                "image": image_path
            })
            continue

        for direction in move_sequence:
            move_worker(level, direction)
            draw_level(level, images, screen)
            pygame.display.flip()
            pygame.time.delay(MOVE_DELAY)

        # Save final level state
        image_path = f'outputs/one_step/eval/sokoban_results/level_{move["level"]}_model_{model_name}.png'
        pygame.image.save(screen, image_path)

        # Example evaluation (you can expand this to be more complex)
        eval_results.append({
            "level": move['level'],
            "model": model_name,
            "output": move_sequence,
            "is_valid": all('$' not in row for row in level),  # Level is valid if no boxes ('$') are left
            "image": image_path
        })

    save_eval_results(eval_results)

if __name__ == "__main__":
    run_game()
    pygame.quit()
