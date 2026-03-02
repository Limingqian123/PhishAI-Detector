import openai
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class LanguageAnalyzer:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            openai.api_base = "https://api.deepseek.com/v1"
        else:
            logger.warning("未配置OpenAI API密钥，语言分析将不可用")
            openai.api_key = None

    async def analyze(self, page_text: str, url: str, forms: list):
        if not openai.api_key:
            return {'is_phishing': False, 'explanation': '语言分析未配置'}

        truncated_text = page_text[:2000]
        prompt = f"""
你是一位网络安全专家。请分析以下网页信息，判断它是否是钓鱼页面。

网页URL: {url}
页面文本摘要: {truncated_text}
表单信息: {forms}

请从以下角度分析：
1. 页面是否在诱导输入敏感信息（密码、信用卡、SSN等）？
2. 域名是否可疑（模仿知名品牌、拼写错误）？
3. 页面整体感觉是否合法？

请直接回答“是钓鱼页面”或“不是钓鱼页面”，并给出简要理由（不超过50字）。
"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=150
            )
            result = response.choices[0].message.content
            is_phishing = "是钓鱼页面" in result
            return {'is_phishing': is_phishing, 'explanation': result}
        except Exception as e:
            logger.error(f"LLM分析失败: {e}")
            return {'is_phishing': False, 'explanation': f'分析出错: {str(e)}'}