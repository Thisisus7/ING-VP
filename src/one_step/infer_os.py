import os
import sys
import json
import torch
from typing import List
from model import QwenVLChatInferencer, BLIP2Inferencer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GAMES, START_LEVEL, END_LEVEL, OUTPUT_OS_DIR as OUTPUT_DIR 

class Game:
    def __init__(self, name: str, prompt_path: str, image_path_format: str):
        self.name = name
        self.prompt_path = prompt_path
        self.image_path_format = image_path_format

    def get_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as file:
            return file.read()

    def get_image_path(self, level: int) -> str:
        return self.image_path_format.format(level)

class InferenceManager:
    def __init__(self, games: List[Game], start_level: int, end_level: int, output_dir: str):
        self.games = games
        self.start_level = start_level
        self.end_level = end_level
        self.output_dir = output_dir
        self.inferencers = {
            "blip2": BLIP2Inferencer(),
            "qwen_vl_chat": QwenVLChatInferencer(),
        }

    def run_inference(self):
        os.makedirs(self.output_dir, exist_ok=True)

        for model_key, inferencer in self.inferencers.items():
            inferencer.load_model()
            
            for game in self.games:
                prompt = game.get_prompt()
                output_path = os.path.join(self.output_dir, f'{game.name}.jsonl')

                with open(output_path, "a", encoding="utf-8") as file:
                    for level in range(self.start_level, self.end_level + 1):
                        image_path = game.get_image_path(level)
                        response = inferencer.infer(prompt, image_path)
                        
                        result = {
                            "game": game.name,
                            "level": level,
                            "model": model_key,
                            "output": response
                        }
                        file.write(json.dumps(result, ensure_ascii=False) + "\n")

            inferencer.cleanup()

def main():
    torch.manual_seed(1234)
    games = [Game(**game) for game in GAMES]
    inference_manager = InferenceManager(
        games=games,
        start_level=START_LEVEL,
        end_level=END_LEVEL,
        output_dir=OUTPUT_DIR
    )
    inference_manager.run_inference()

if __name__ == "__main__":
    main()