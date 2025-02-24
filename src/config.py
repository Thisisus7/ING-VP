# Configuration for games
GAMES = [
    {
        "name": "maze",
        "levels_path": "data/maze/levels_50.txt",
        "level_image_path": "data/maze/LevelImages/level_{}.png",
        "prompt_path": "prompts/one_step_image/prt_maze_os.txt",
        "prompt_ms_path": "prompts/multi_step_image/prt_maze{}.txt",
        "prompt_ms_history_path": "prompts/multi_step_history_image/prt_maze{}.txt",
        "text_prompt_path": "prompts/one_step_text/prt_maze_os_text.txt",
        "text_prompt_ms_path": "prompts/multi_step_text/prt_maze{}.txt",
        "text_prompt_ms_history_path": "prompts/multi_step_history_text/prt_maze{}.txt",
    },
    {
        "name": "sokoban",
        "levels_path": "data/sokoban/levels_50.txt",
        "level_image_path": "data/sokoban/LevelImages/level_{}.png",
        "prompt_path": "prompts/one_step_image/prt_sokoban_os.txt",
        "prompt_ms_path": "prompts/multi_step_image/prt_sokoban.txt",
        "prompt_ms_history_path": "prompts/multi_step_history_image/prt_sokoban{}.txt",
        "text_prompt_path": "prompts/one_step_text/prt_sokoban_os_text.txt",
        "text_prompt_ms_path": "prompts/multi_step_text/prt_sokoban{}.txt",
        "text_prompt_ms_history_path": "prompts/multi_step_history_text/prt_sokoban{}.txt",
    },
    {
        "name": "n_queens",
        "levels_path": "data/n_queens/levels_50.jsonl",
        "level_image_path": "data/n_queens/LevelImages/level_{}.png",
        "prompt_path": "prompts/one_step_image/prt_n_queens_os.txt",
        "prompt_ms_path": "prompts/multi_step_image/prt_n_queens{}.txt",
        "prompt_ms_history_path": "prompts/multi_step_history_image/prt_n_queens{}.txt",
        "text_prompt_path": "prompts/one_step_text/prt_n_queens_os_text.txt",
        "text_prompt_ms_path": "prompts/multi_step_text/prt_n_queens{}.txt",
        "text_prompt_ms_history_path": "prompts/multi_step_history_text/prt_n_queens{}.txt",    
    },
    {
        "name": "sudoku",
        "levels_path": "data/sudoku/levels_50.jsonl",
        "level_image_path": "data/sudoku/LevelImages/level_{}.png",        
        "prompt_path": "prompts/one_step_image/prt_sudoku_os.txt",
        "prompt_ms_path": "prompts/multi_step_image/prt_sudoku{}.txt",
        "prompt_ms_history_path": "prompts/multi_step_history_image/prt_sudoku{}.txt",
        "text_prompt_path": "prompts/one_step_text/prt_sudoku_os_text.txt",
        "text_prompt_ms_path": "prompts/multi_step_text/prt_sudoku{}.txt",
        "text_prompt_ms_history_path": "prompts/multi_step_history_text/prt_sudoku{}.txt",       
    },
    {
        "name": "hanoi",
        "levels_path": "data/hanoi/levels_50.jsonl",
        "level_image_path": "data/hanoi/LevelImages/level_{}.png",
        "prompt_path": "prompts/one_step_image/prt_hanoi_os.txt",
        "prompt_ms_path": "prompts/multi_step_image/prt_hanoi{}.txt",
        "prompt_ms_history_path": "prompts/multi_step_history_image/prt_hanoi{}.txt",
        "text_prompt_path": "prompts/one_step_text/prt_hanoi_os_text.txt",
        "text_prompt_ms_path": "prompts/multi_step_text/prt_hanoi{}.txt",
        "text_prompt_ms_history_path": "prompts/multi_step_history_text/prt_hanoi{}.txt",        
    },
    {
        "name": "n_puzzle",
        "levels_path": "data/n_puzzle/levels_50.jsonl",
        "level_image_path": "data/n_puzzle/LevelImages/level_{}.png",
        "prompt_path": "prompts/one_step_image/prt_n_puzzle_os.txt",
        "prompt_ms_path": "prompts/multi_step_image/prt_n_puzzle{}.txt",
        "prompt_ms_history_path": "prompts/multi_step_history_image/prt_n_puzzle{}.txt",
        "text_prompt_path": "prompts/one_step_text/prt_n_puzzle_os_text.txt",
        "text_prompt_ms_path": "prompts/multi_step_text/prt_n_puzzle{}.txt",
        "text_prompt_ms_history_path": "prompts/multi_step_history_text/prt_n_puzzle{}.txt",        
    },
]

# Configuration for inference levels and output directory
START_LEVEL = 1
END_LEVEL = 50
MAX_STEPS = 50
SYSTEM_PROMPT_SUFFIX='_system_prompt'
INSTRUCTION_SUFFIX='_instruction'
USER_SUFFIX=''

# one step
OUTPUT_OS_DIR = "outputs/one_step/image_text"
OUTPUT_TEXT_OS_DIR = "outputs/one_step/text_only"
# multi step
OUTPUT_IMAGE_BASE_DIR = "outputs/multi_step/image_text/base"
OUTPUT_IMAGE_HIS_DIR = "outputs/multi_step/image_text/history"
OUTPUT_TEXT_BASE_DIR = "outputs/multi_step/text_only/base"
OUTPUT_TEXT_HIS_DIR = "outputs/multi_step/text_only/history"