import asyncio
import logging
from src.browser.playwright_manager import PlaywrightManager
from src.analyzers.vision import VisionAnalyzer
from src.analyzers.language import LanguageAnalyzer
from src.analyzers.threat_intel import ThreatIntelAnalyzer
from src.analyzers.similarity import SimilarityAnalyzer
from src.explainer.report_generator import ReportGenerator
from src.models.response import AnalysisResponse

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    def __init__(self):
        self.browser = PlaywrightManager()
        self.vision = VisionAnalyzer()
        self.language = LanguageAnalyzer()
        self.threat = ThreatIntelAnalyzer()
        self.similarity = SimilarityAnalyzer()
        self.report_gen = ReportGenerator()

    async def run(self, url: str) -> AnalysisResponse:
        logger.info(f"开始分析: {url}")
        await self.browser.start()
        try:
            page_data = await self.browser.capture(url)
        except Exception as e:
            logger.error(f"页面捕获失败: {e}")
            await self.browser.close()
            raise

        vision_task = asyncio.create_task(asyncio.to_thread(self.vision.analyze, page_data['screenshot']))
        similarity_task = asyncio.create_task(asyncio.to_thread(self.similarity.compare_with_brand, page_data['screenshot']))
        language_task = self.language.analyze(page_data['page_text'], url, page_data['forms'])
        threat_task = self.threat.check(url)

        vision_result, similarity_score, language_result, threat_result = await asyncio.gather(
            vision_task, similarity_task, language_task, threat_task, return_exceptions=True
        )

        if isinstance(vision_result, Exception):
            logger.error(f"视觉分析失败: {vision_result}")
            vision_result = {'logos': [], 'ocr_text': '', 'safe_search': {}}
        if isinstance(similarity_score, Exception):
            logger.error(f"相似度分析失败: {similarity_score}")
            similarity_score = 0.0
        if isinstance(language_result, Exception):
            logger.error(f"语言分析失败: {language_result}")
            language_result = {'is_phishing': False, 'explanation': '分析失败'}
        if isinstance(threat_result, Exception):
            logger.error(f"威胁情报失败: {threat_result}")
            threat_result = {}

        await self.browser.close()

        # 综合评分
        phishing_score = 0
        if threat_result.get('google_safe') == 'malicious':
            phishing_score += 30
        vt_stats = threat_result.get('virustotal', {})
        if isinstance(vt_stats, dict) and vt_stats.get('malicious', 0) > 0:
            phishing_score += 20
        if threat_result.get('urlhaus') is True:
            phishing_score += 20
        if language_result.get('is_phishing'):
            phishing_score += 30
        if similarity_score > 0.8:
            phishing_score += 20
        elif similarity_score > 0.6:
            phishing_score += 10
        sensitive_logos = ['paypal', 'apple', 'microsoft', 'google', 'facebook', 'amazon', 'bank']
        detected_logos = [logo.lower() for logo in vision_result.get('logos', [])]
        if any(logo in sensitive_logos for logo in detected_logos):
            phishing_score += 15

        is_phishing = phishing_score >= 50
        confidence = phishing_score / 100.0

        explanation = await self.report_gen.generate({
            'url': url,
            'phishing_score': phishing_score,
            'is_phishing': is_phishing,
            'vision': vision_result,
            'similarity': similarity_score,
            'language': language_result,
            'threat_intel': threat_result
        })

        details = {
            'score': phishing_score,
            'vision': vision_result,
            'similarity': similarity_score,
            'language': language_result,
            'threat_intel': threat_result
        }

        return AnalysisResponse(
            url=url,
            is_phishing=is_phishing,
            confidence=confidence,
            explanation=explanation,
            details=details
        )