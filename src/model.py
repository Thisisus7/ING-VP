import torch
# from transformers import AutoModelForCausalLM, AutoTokenizer, Blip2Processor, Blip2ForConditionalGeneration, BitsAndBytesConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
from abc import ABC, abstractmethod

class ModelInferencer(ABC):
    def __init__(self, device):
        self.device = device

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
        torch.manual_seed(1234)
        self.tokenizer = AutoTokenizer.from_pretrained("/ML-A100/public/model/Qwen-VL", trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained("/ML-A100/public/model/Qwen-VL", device_map=self.device, trust_remote_code=True).eval()

    def infer(self, prompt: str, image_path: str) -> str:
        query = self.tokenizer.from_list_format([
            {'image': image_path},
            {'text': prompt},
        ])
        inputs = self.tokenizer(query, return_tensors='pt')
        inputs = inputs.to(self.model.device)
        pred = self.model.generate(**inputs)
        response = self.tokenizer.decode(pred.cpu()[0], skip_special_tokens=False)
        
        return response

# class BLIP2Inferencer(ModelInferencer):
#     def load_model(self):
#         self.processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
#         quantization_config = BitsAndBytesConfig(load_in_8bit=True)
#         self.model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b", device_map="auto")

#     def infer(self, prompt: str, image_path: str) -> str:
#         raw_image = Image.open(image_path).convert('RGB')
#         inputs = self.processor(raw_image, prompt, return_tensors="pt").to("cuda", torch.float16)
#         with torch.inference_mode():
#             generation = self.model.generate(**inputs, max_new_tokens=300)
#             result = self.processor.decode(generation[0], skip_special_tokens=True).strip()
#         return result