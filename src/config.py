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
        "prompt_path": "prompts/prompt_maze.txt",
        "image_path_format": r'data\maze\LevelImages\level_{}.png'
    },
    {
        "name": "sokoban",
        "prompt_path": "prompts/prompt_sokoban.txt",
        "image_path_format": r'data\sokoban\LevelImages\level_{}.png'
    },
    {
        "name": "n-queens",
        "prompt_path": "prompts/prompt_n_queens.txt",
        "image_path_format": r'data\n-queens\LevelImages\level_{}.png'
    },
    {
        "name": "sudoku",
        "prompt_path": "prompts/prompt_sudoku.txt",
        "image_path_format": r'data\sudoku\LevelImages\level_{}.png'
    },
]

# Configuration for inference levels and output directory
START_LEVEL = 1
END_LEVEL = 1
OUTPUT_DIR = r'outputs\one_step\models\raw'
