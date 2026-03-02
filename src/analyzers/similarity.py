from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import io
import logging

logger = logging.getLogger(__name__)

class SimilarityAnalyzer:
    def __init__(self):
        try:
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.available = True
        except Exception as e:
            logger.error(f"CLIP模型加载失败: {e}")
            self.available = False

    def compare_with_brand(self, image_bytes: bytes, brand_name: str = "PayPal"):
        if not self.available:
            return 0.0
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            inputs = self.processor(text=[brand_name], images=image, return_tensors="pt", padding=True)
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            similarity = torch.sigmoid(logits_per_image).item()
            return similarity
        except Exception as e:
            logger.error(f"相似度计算失败: {e}")
            return 0.0