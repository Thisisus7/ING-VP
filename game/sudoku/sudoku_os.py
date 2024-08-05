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

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Load levels and instructions
def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

levels = load_jsonl('data/sudoku/levels_50.jsonl')
instructions = load_jsonl('outputs/one_step/models/formatted/sudoku.jsonl')

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
def draw_numbers(board, solution, added_positions):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            index = row * GRID_SIZE + col
            num = board[index]
            if num != '0':
                if (row, col) in added_positions:
                    color = BLUE if num == solution[index] else RED
                else:
                    color = BLACK
                text = font.render(num, True, color)
                screen.blit(text, (col * CELL_SIZE + CELL_SIZE // 3, row * CELL_SIZE + CELL_SIZE // 4))

# Apply instructions to the board
def apply_instructions(board, instruction):
    added_positions = set()
    if instruction:
        for key, value in instruction.items():
            row, col = int(key[0]), int(key[1])
            index = row * GRID_SIZE + col
            if board[index] == '0':
                board = board[:index] + str(value) + board[index + 1:]
                added_positions.add((row, col))
    return board, added_positions

# Save the final frame as an image
def save_final_frame(level, model, board, solution, added_positions):
    screen.fill(WHITE)
    draw_grid()
    draw_numbers(board, solution, added_positions)
    pygame.display.flip()
    pygame.image.save(screen, f'outputs/one_step/eval/sudoku_results/level_{level}_model_{model}.png')

# Validate the final board against the solution
def validate_solution(board, solution):
    return board == solution

# Main game loop
def main():
    eval_results = []

    if not os.path.exists('outputs/one_step/eval/sudoku_results'):
        os.makedirs('outputs/one_step/eval/sudoku_results')

    for level in levels:
        board = level['position']
        solution = level['solutions']
        level_instructions = [item for item in instructions if item['level'] == level['level']]

        for instruction in level_instructions:
            model = instruction['model']
            output = instruction['output']
            
            try:
                instruction_set = json.loads(output) if output else {}
            except json.JSONDecodeError:
                instruction_set = {}

            board_copy = board[:]
            board_copy, added_positions = apply_instructions(board_copy, instruction_set)

            save_final_frame(level['level'], model, board_copy, solution, added_positions)
            is_valid = validate_solution(board_copy, solution)

            eval_results.append({
                "level": level['level'],
                "model": model,
                "output": output,
                "is_valid": is_valid,
                "image": f"outputs/one_step/eval/sudoku_results/level_{level['level']}_model_{model}.png"
            })

    with open('outputs/one_step/eval/sudoku.jsonl', 'w') as eval_file:
        for result in eval_results:
            eval_file.write(json.dumps(result) + '\n')

    pygame.quit()

if __name__ == '__main__':
    main()