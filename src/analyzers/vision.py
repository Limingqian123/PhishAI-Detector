from google.cloud import vision
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class VisionAnalyzer:
    def __init__(self):
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            self.client = vision.ImageAnnotatorClient.from_service_account_json(
                settings.GOOGLE_APPLICATION_CREDENTIALS
            )
        else:
            logger.warning("未配置Google Cloud凭据，视觉分析将不可用")
            self.client = None

    def analyze(self, image_bytes: bytes):
        if not self.client:
            return {'logos': [], 'ocr_text': '', 'safe_search': {}}

        image = vision.Image(content=image_bytes)
        logo_response = self.client.logo_detection(image=image)
        logos = [logo.description for logo in logo_response.logo_annotations]

        text_response = self.client.text_detection(image=image)
        texts = [text.description for text in text_response.text_annotations]

        safe_search = self.client.safe_search_detection(image=image)
        safe_annotation = safe_search.safe_search_annotation

        return {
            'logos': logos,
            'ocr_text': texts[0] if texts else '',
            'safe_search': {
                'adult': safe_annotation.adult,
                'violence': safe_annotation.violence,
                'racy': safe_annotation.racy
            } if safe_annotation else {}
        }