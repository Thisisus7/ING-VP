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
        "prompt_path": r"prompts\prompt_maze_os.txt",
        "prompt_ms_path": r"prompts\prt_maze.txt",
        "prompt_ms_history_path": r"prompts\prt_maze.txt",
        "image_path_format": r'data\maze\LevelImages\level_{}.png'
    },
    {
        "name": "sokoban",
        "prompt_path": r"prompts\prompt_sokoban_os.txt",
        "prompt_ms_path": r"prompts\prt_sokoban.txt",
        "prompt_ms_history_path": r"prompts\prt_sokoban_history.txt",
        "image_path_format": r'data\sokoban\LevelImages\level_{}.png'
    },
    {
        "name": "n-queens",
        "prompt_path": r"prompts\prompt_n_queens_os.txt",
        "prompt_ms_path": r"prompts\prt_n_queens.txt",
        "prompt_ms_history_path": r"prompts\prt_n_queens_history.txt",
        "image_path_format": r'data\n-queens\LevelImages\level_{}.png'
    },
    {
        "name": "sudoku",
        "prompt_path": r"prompts\prompt_sudoku_os.txt",
        "prompt_ms_path": r"prompts\prt_sudoku.txt",
        "prompt_ms_history_path": r"prompts\prt_sudoku._history.txt",
        "image_path_format": r'data\sudoku\LevelImages\level_{}.png'
    },
    {
        "name": "hanoi",
        "prompt_path": r"prompts\prompt_hanoi_os.txt",
        "prompt_ms_path": r"prompts\prt_hanoi.txt",
        "prompt_ms_history_path": r"prompts\prt_hanoi_history.txt",
        "image_path_format": r'data\sudoku\LevelImages\level_{}.png'
    },
]

# Configuration for inference levels and output directory
START_LEVEL = 1
END_LEVEL = 1
OUTPUT_OS_DIR = r'outputs\one_step\models\raw'
OUTPUT_MS_DIR = r'outputs\multi_step\models\raw'
