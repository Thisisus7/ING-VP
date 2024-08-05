# src\multi_step\prompts.py

import json
import os

def add_conversation_history(prompt, model_name, game_name, level):
    conversation_history_path = os.path.join(
        "outputs", "multi_step", "history", "models",
        model_name, game_name, f"level_{level}.jsonl"
    )
    
    history_text = ""
    
    if os.path.exists(conversation_history_path):
        with open(conversation_history_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                history_text += f"step {data['step']}: {data['output']}\n"
    
    return prompt.replace("{conversation_history_path}", history_text)