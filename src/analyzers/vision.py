import requests
import base64
from src.config import settings

class VisionAnalyzer:
    def __init__(self):
        self.api_key = settings.GOOGLE_VISION_API_KEY
        self.api_url = "https://vision.googleapis.com/v1/images:annotate"

    def analyze(self, image_bytes: bytes):
        if not self.api_key:
            return {'logos': [], 'ocr_text': '', 'safe_search': {}}

        # 将图片转为base64
        encoded = base64.b64encode(image_bytes).decode('utf-8')

        # 构造请求
        payload = {
            "requests": [{
                "image": {"content": encoded},
                "features": [
                    {"type": "LOGO_DETECTION", "maxResults": 5},
                    {"type": "TEXT_DETECTION", "maxResults": 1},
                    {"type": "SAFE_SEARCH_DETECTION"}
                ]
            }]
        }

        # 发送请求
        response = requests.post(
            f"{self.api_url}?key={self.api_key}",
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            return {'logos': [], 'ocr_text': '', 'safe_search': {}}

        data = response.json()
        responses = data.get('responses', [{}])[0]

        # 解析结果
        logos = [anno['description'] for anno in responses.get('logoAnnotations', [])]
        text = responses.get('textAnnotations', [{}])[0].get('description', '') if responses.get(
            'textAnnotations') else ''
        safe = responses.get('safeSearchAnnotation', {})

        return {
            'logos': logos,
            'ocr_text': text,
            'safe_search': {
                'adult': safe.get('adult', 'UNKNOWN'),
                'violence': safe.get('violence', 'UNKNOWN'),
                'racy': safe.get('racy', 'UNKNOWN')
            }
        }