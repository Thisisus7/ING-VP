import subprocess

def run_script(script_path):
    try:
        result = subprocess.run(["python", script_path], check=True, capture_output=True, text=True)
        print(f"Output of {script_path}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}:\n{e.stderr}")

if __name__ == "__main__":
    scripts = [
        r".\src\format.py",
        r".\game\sokoban\sokoban_os.py",
        r".\game\maze\maze_os.py",
        r".\game\sudoku\sudoku_os.py",
        r".\game\n-queens\n_queens_os.py"
    ]

    for script in scripts:
        run_script(script)
