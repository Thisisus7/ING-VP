import json
import pygame
import sys
import os
from typing import List, Tuple
import ast

# Constants
SCREEN_SIZE = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
CELL_SIZE = SCREEN_SIZE // 8

# Read levels from JSONL file
def read_levels(input_file: str) -> List[dict]:
    levels = []
    with open(input_file, 'r') as infile:
        for line in infile:
            levels.append(json.loads(line))
    return levels

# Read instructions from JSONL file
def read_instructions(input_file: str) -> List[dict]:
    instructions = []
    with open(input_file, 'r') as infile:
        for line in infile:
            instructions.append(json.loads(line))
    return instructions

# Draw the chessboard
def draw_chessboard(screen):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Draw a queen on the chessboard
def draw_queen(screen, row: int, col: int, color: Tuple[int, int, int]):
    pygame.draw.circle(screen, color, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

# Function to validate N-Queens solution
def validate_solution(queens: List[Tuple[int, int]]) -> bool:
    if len(queens) != 8:
        return False

    for i in range(8):
        for j in range(i + 1, 8):
            if queens[i][0] == queens[j][0] or queens[i][1] == queens[j][1]:
                return False
            if abs(queens[i][0] - queens[j][0]) == abs(queens[i][1] - queens[j][1]):
                return False

    return True

# Main function
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("N-Queens Problem")

    levels_file = 'data/n-queens/levels_50.jsonl'
    instructions_file = 'outputs/one_step/models/formatted/n-queens.jsonl'
    output_file = 'outputs/one_step/eval/n-queens.jsonl'
    results_dir = 'outputs/one_step/eval/n-queens_results'

    # Ensure the output directories exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    levels = read_levels(levels_file)
    instructions = read_instructions(instructions_file)
    results = []

    for instruction in instructions:
        level = next(l for l in levels if l["level"] == instruction["level"])
        screen.fill(WHITE)
        draw_chessboard(screen)

        # Draw the initial queen
        first_queen = level["first"]
        draw_queen(screen, first_queen[0], first_queen[1], RED)

        # Draw the rest of the queens
        queens = [first_queen]
        if instruction["output"]:
            try:
                additional_queens = ast.literal_eval(instruction["output"])
                queens.extend(additional_queens)
                for queen in additional_queens:
                    draw_queen(screen, queen[0], queen[1], SKY_BLUE)
            except:
                pass

        pygame.display.flip()

        is_valid = validate_solution(queens)
        
        # Save the final frame for each level and model
        final_frame_path = os.path.join(results_dir, f'level_{level["level"]}_model_{instruction["model"]}.png')
        pygame.image.save(screen, final_frame_path)

        results.append({
            "level": level["level"],
            "model": instruction["model"],
            "output": instruction["output"],
            "is_valid": is_valid,
            "image": final_frame_path
        })

        # Pause for a moment to visualize each level
        pygame.time.wait(500)

    # Write the results to the output file
    with open(output_file, 'w') as outfile:
        for result in results:
            json.dump(result, outfile)
            outfile.write('\n')

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()