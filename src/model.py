import torch
import base64
from transformers import AutoModelForCausalLM, AutoTokenizer, Blip2Processor, Blip2ForConditionalGeneration, BitsAndBytesConfig
from PIL import Image
from abc import ABC, abstractmethod
from openai import OpenAI

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
        if image_path == "Null":
            query = prompt
        else:
            query = self.tokenizer.from_list_format([
                {'image': image_path},
                {'text': prompt},
            ])
        response, _ = self.model.chat(self.tokenizer, query=query, history=None, max_new_tokens=20)
        return response

class BLIP2Inferencer(ModelInferencer):
    def load_model(self):
        self.processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        self.model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b", device_map="auto")

    def infer(self, prompt: str, image_path: str) -> str:
        image_path = "prompts/blank.png"
        raw_image = Image.open(image_path).convert('RGB')
        inputs = self.processor(raw_image, prompt, return_tensors="pt").to("cuda", torch.float16)
        with torch.inference_mode():
            generation = self.model.generate(**inputs, max_new_tokens=300)
            result = self.processor.decode(generation[0], skip_special_tokens=True).strip()
        return result


class APIInferencer(ABC):
    @abstractmethod
    def infer(self, prompt: str, image_path: str) -> str:
        pass

    def load_client(self):
        return OpenAI(
            api_key='09c9021c0811db8d65c8bd9dd1df7341',
            base_url="https://idealab.alibaba-inc.com/api/openai/v1",
        )

    def cleanup(self):
        if hasattr(self, 'client'):
            del self.client

    def encode_image_to_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def get_correct_response(
                            self, 
                            model_name: str, 
                            system_prompt: str, 
                            user_prompt: str, 
                            image_path: str, 
                            temperature: float
                            ) -> str:
        response = self.model_chat(model_name, system_prompt, user_prompt, image_path, temperature)
        return response if response else self.get_correct_response(model_name, system_prompt, user_prompt, image_path, temperature)

    def model_chat(self, model_name: str, system_prompt: str, user_prompt: str, image_path: str, temperature: float) -> str:
        client = self.load_client()
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            } if system_prompt else {},
            {
                "role": "user",
                "content": self.build_message_content(user_prompt, image_path)
            }
        ]
        messages = [msg for msg in messages if msg]
        try:
            completion = client.chat.completions.create(model=model_name, messages=messages, temperature=temperature)
            return completion.choices[0].message.content
        except:
            return self.model_chat(model_name, system_prompt, user_prompt, image_path, temperature)

    def build_message_content(self, prompt: str, image_path: str):
        if image_path == "Null":
            return prompt
        base64_image = self.encode_image_to_base64(image_path)
        return [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                },
            },
        ]

class GPT4oInferencer(APIInferencer):
    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response('gpt-4o-0513', system_prompt, prompt, image_path, temperature)
        return response
    
class Claude35Inferencer(APIInferencer):
    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response('claude35_sonnet', system_prompt, prompt, image_path, temperature)
        return response

class GPT4VInference(APIInferencer):
    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response('gpt-4-vision-preview', system_prompt, prompt, image_path, temperature)
        return response

class Gemini15ProInference(APIInferencer):
    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response('gemini-1.5-pro', system_prompt, prompt, image_path, temperature)
        return response

class GPT4TurboInference(APIInferencer):
    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response('gpt-4-turbo-128k', system_prompt, prompt, image_path, temperature)
        return response
    
class GPT4TurboInference(APIInferencer):
    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response('claude3_opus', system_prompt, prompt, image_path, temperature)
        return response

class Claude3OpusInference(APIInferencer):
    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response('claude3_opus', system_prompt, prompt, image_path, temperature)
        return response

class Qwen2_72BInference(APIInferencer):
    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response('qwen2-72b-instruct', system_prompt, prompt, image_path, temperature)
        return response

class LLaMA3_72BInference(APIInferencer):
    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response('llama3', system_prompt, prompt, image_path, temperature)
        return response
     
class QwenVLMaxInference(APIInferencer):
    def build_message_content(self, prompt: str, image_url: str):
        if image_url == "Null":
            return prompt
        return [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"{image_url}"
                },
            },
        ]
    
    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response('qwen-vl-max', system_prompt, prompt, image_path, temperature)
        return response
    
