import os
import json

def add_level_to_prompt(prompt, game, level, step, output_dir, model_name):
    if game["name"] in ["maze", "sokoban"]:
        level_text = load_txt_level(game, level, step, output_dir, model_name)
    elif game["name"] in ["hanoi", "n_puzzle", "n_queens", "sudoku"]:
        level_text = load_json_level(game, level, step, output_dir, model_name)

    return prompt.replace("{text_representation_path}", level_text)


def load_txt_level(game, level_number, step, output_dir, model_name):
    if step == 1:
        with open(game["levels_path"], 'r') as file:
            data = file.read()
        levels = data.split(';')
        for level in levels:
            level_info = level.strip().split('\n')
            if level_info and level_info[0].strip() == str(level_number):
                return '\n'.join(level_info[1:])
    else:
        file_path = os.path.join(
            output_dir,
            "process_levels",
            model_name,
            game["name"],
            f"level_{level_number}",
            f"step_{step-1}.txt"
        )
        with open(file_path, 'r') as file:
            data = file.read()
        return data

def load_json_level(game, level_number, step, output_dir, model_name):
    if step == 1:
        with open(game["levels_path"], 'r') as file:
            for line in file:
                data = json.loads(line)
                if data["level"] == level_number:
                    return json.dumps(data["position"])  # to string
    else:
        file_path = os.path.join(
            output_dir,
            "process_levels",
            model_name,
            game["name"],
            
        )
        if game["name"] in ["maze", "sokoban"]:
            txt_file_path = os.path.join(file_path, f"level_{level_number}", f"step_{step-1}.txt")
            with open(txt_file_path, 'r') as file:
                for line in file:
                    data = json.loads(line)
                    if data["step"] == step-1:
                        return json.dumps(data["position"])
                    
        elif game["name"] == "n_queens":
            combined_moves = []
            json_file_path = os.path.join(file_path, f"level_{level_number}.jsonl")
            with open(json_file_path, 'r') as file:
                for line in file:
                    data = json.loads(line)
                    if data["step"] == step-1:
                        combined_moves.append(data["position"])
                        combined_moves.extend(data["output"])
            return json.dumps(combined_moves)
        
        elif game["name"] in ["sudoku", "hanoi", "n_puzzle"]:
            json_file_path = os.path.join(file_path, f"level_{level_number}.jsonl")
            with open(json_file_path, 'r') as file:
                for line in file:
                    data = json.loads(line)
                    if data["step"] == step-1:
                        return json.dumps(data["position"])