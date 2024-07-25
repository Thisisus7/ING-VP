import os
import logging

# Setup logging to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("inference.log"),
        logging.StreamHandler()
    ]
)

# Configuration for games
GAMES = [
    {
        "name": "maze",
        "levels_path": r"data\maze\levels_50.txt",
        "prompt_path": r"prompts\prompt_maze_os.txt",
        "prompt_ms_path": r"prompts\prt_maze.txt",
        "prompt_ms_history_path": r"prompts\prt_maze.txt",
        "image_path_format": r'data\maze\LevelImages\level_{}.png'
    },
    # {
    #     "name": "sokoban",
    #     "levels_path": r"data\sokoban\levels_50.txt",
    #     "prompt_path": r"prompts\prompt_sokoban_os.txt",
    #     "prompt_ms_path": r"prompts\prt_sokoban.txt",
    #     "prompt_ms_history_path": r"prompts\prt_sokoban_history.txt",
    #     "image_path_format": r'data\sokoban\LevelImages\level_{}.png'
    # },
    # {
    #     "name": "n_queens",
    #     "levels_path": r"data\n_queens\levels_50.jsonl",
    #     "prompt_path": r"prompts\prompt_n_queens_os.txt",
    #     "prompt_ms_path": r"prompts\prt_n_queens.txt",
    #     "prompt_ms_history_path": r"prompts\prt_n_queens_history.txt",
    #     "image_path_format": r'data\n_queens\LevelImages\level_{}.png'
    # },
    # {
    #     "name": "sudoku",
    #     "levels_path": r"data\sudoku\levels_50.jsonl",
    #     "prompt_path": r"prompts\prompt_sudoku_os.txt",
    #     "prompt_ms_path": r"prompts\prt_sudoku.txt",
    #     "prompt_ms_history_path": r"prompts\prt_sudoku._history.txt",
    #     "image_path_format": r'data\sudoku\LevelImages\level_{}.png'
    # },
    # {
    #     "name": "hanoi",
    #     "levels_path": r"data\hanoi\levels_50.jsonl",
    #     "prompt_path": r"prompts\prompt_hanoi_os.txt",
    #     "prompt_ms_path": r"prompts\prt_hanoi.txt",
    #     "prompt_ms_history_path": r"prompts\prt_hanoi_history.txt",
    #     "image_path_format": r'data\sudoku\LevelImages\level_{}.png'
    # },
    # {
    #     "name": "n_puzzle",
    #     "levels_path": r"data\n_puzzle\levels_50.jsonl",
    #     "prompt_path": r"prompts\prompt_n_puzzle_os.txt",
    #     "prompt_ms_path": r"prompts\prt_n_puzzle.txt",
    #     "prompt_ms_history_path": r"prompts\prt_n_puzzle_history.txt",
    #     "image_path_format": r'data\n_puzzle\LevelImages\level_{}.png'
    # },
]

# MODELS = ['blip2', 'qwen_vl_chat']
MODELS = ['qwen_vl_chat']

# Configuration for inference levels and output directory
START_LEVEL = 10
END_LEVEL = 10
MAX_STEPS = 50

# one step
OUTPUT_OS_DIR = r'outputs\one_step\models\raw'
# multi step
OUTPUT_BASE_DIR = r"outputs\multi_step\base"
OUTPUT_HIS_DIR = r"outputs\multi_step\history"
