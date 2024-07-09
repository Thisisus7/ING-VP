import pygame
import json
import os

# Initialize Pygame
pygame.init()

# Define constants
WINDOW_SIZE = 600
GRID_SIZE = 9
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
FONT_SIZE = CELL_SIZE // 2

MIN_DELAY = .01  # Minimum delay between steps (in seconds)
MAX_DELAY = .02  # Maximum delay between steps (in seconds)
INITIAL_DELAY = .1  # Initial delay between steps (in seconds)
DELAY_STEP = .01  # How much to change the delay when adjusting speed

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Load levels and instructions
def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

levels = load_jsonl('data/sudoku/levels_50.jsonl')
instructions = load_jsonl('outputs/one_step/sudoku/models/sudoku.jsonl')

# Initialize screen
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Sudoku Game')
font = pygame.font.SysFont(None, FONT_SIZE)

# Draw grid
def draw_grid():
    for i in range(GRID_SIZE + 1):
        thickness = 1 if i % 3 else 3
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WINDOW_SIZE), thickness)
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WINDOW_SIZE, i * CELL_SIZE), thickness)

# Draw numbers on the grid
def draw_numbers(board, added_positions):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            index = row * GRID_SIZE + col
            num = board[index]
            if num != '0':
                color = RED if (row, col) in added_positions else BLACK
                text = font.render(num, True, color)
                screen.blit(text, (col * CELL_SIZE + CELL_SIZE // 3, row * CELL_SIZE + CELL_SIZE // 4))

# Apply instructions to the board
def apply_instructions(board, instruction):
    added_positions = set()
    for key, value in instruction.items():
        row, col = int(key[0]), int(key[1])
        index = row * GRID_SIZE + col
        if board[index] == '0':
            board = board[:index] + str(value) + board[index + 1:]
            added_positions.add((row, col))
    return board, added_positions

# Save the final frame as an image
def save_final_frame(level, board, added_positions):
    screen.fill(WHITE)
    draw_grid()
    draw_numbers(board, added_positions)
    pygame.display.flip()
    pygame.image.save(screen, f'outputs/one_step/sudoku/eval/results/level_{level}.png')

# Validate the final board against the solution
def validate_solution(board, solution):
    return board == solution

# Main game loop
def main():
    running = True
    clock = pygame.time.Clock()
    delay = INITIAL_DELAY
    last_step_time = 0

    eval_results = []
    added_positions = set()

    if not os.path.exists('outputs/One_Step/Sudoku/Eval/Results'):
        os.makedirs('outputs/One_Step/Sudoku/Eval/Results')

    for level in levels:
        board = level['quiz']
        solution = level['solutions']
        try:
            instruction_set = next(item['output'] for item in instructions if item['level'] == level['level'])
        except StopIteration:
            print(f"No instructions found for level {level['level']}")
            eval_results.append({"level": level['level'], "is_valid": False})
            continue

        step_index = 0
        steps = list(instruction_set.items())
        added_positions.clear()

        while step_index < len(steps) and running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        delay = max(MIN_DELAY, delay - DELAY_STEP)
                    elif event.key == pygame.K_DOWN:
                        delay = min(MAX_DELAY, delay + DELAY_STEP)

            if current_time - last_step_time > delay * 1000:  # Convert delay to milliseconds
                screen.fill(WHITE)
                draw_grid()
                draw_numbers(board, added_positions)

                key, value = steps[step_index]
                row, col = int(key[0]), int(key[1])
                index = row * GRID_SIZE + col
                if board[index] == '0':
                    board = board[:index] + str(value) + board[index + 1:]
                    added_positions.add((row, col))
                step_index += 1

                last_step_time = current_time

            pygame.display.flip()
            clock.tick(60)  # Cap the frame rate at 60 FPS

        if running:
            save_final_frame(level['level'], board, added_positions)
            is_valid = validate_solution(board, solution)
            eval_results.append({"level": level['level'], "is_valid": is_valid})

    with open('outputs/one_step/sudoku/eval/eval.jsonl', 'w') as eval_file:
        for result in eval_results:
            eval_file.write(json.dumps(result) + '\n')

    pygame.quit()

if __name__ == '__main__':
    main()
