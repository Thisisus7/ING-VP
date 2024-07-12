import os
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Blip2Processor, Blip2ForConditionalGeneration, BitsAndBytesConfig
from PIL import Image
from typing import List
from abc import ABC, abstractmethod
from config import GAMES, START_LEVEL, END_LEVEL, OUTPUT_DIR
import logging

class ModelInferencer(ABC):
    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def infer(self, prompt: str, image_path: str) -> str:
        pass

    def cleanup(self):
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        elif hasattr(self, 'processor'):
            del self.processor
        torch.cuda.empty_cache()

class QwenVLChatInferencer(ModelInferencer):
    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat-Int4", trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-VL-Chat-Int4", device_map="cuda", trust_remote_code=True).eval()

    def infer(self, prompt: str, image_path: str) -> str:
        query = self.tokenizer.from_list_format([
            {'image': image_path},
            {'text': prompt},
        ])
        response, _ = self.model.chat(self.tokenizer, query=query, history=None)
        return response

class BLIP2Inferencer(ModelInferencer):
    def load_model(self):
        self.processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        self.model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b", device_map="auto", quantization_config=quantization_config).eval()

    def infer(self, prompt: str, image_path: str) -> str:
        raw_image = Image.open(image_path).convert('RGB')
        inputs = self.processor(raw_image, prompt, return_tensors="pt").to("cuda", torch.float16)
        with torch.inference_mode():
            generation = self.model.generate(**inputs, max_new_tokens=100)
            result = self.processor.decode(generation[0], skip_special_tokens=True).strip()
        return result

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