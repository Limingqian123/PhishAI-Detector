import openai
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            logger.warning("未配置OpenAI API密钥，解释报告将使用模板")

    async def generate(self, analysis_data: dict) -> str:
        if not openai.api_key:
            return self._template_report(analysis_data)

        prompt = f"""
基于以下多维度分析结果，为普通用户生成一份易于理解的安全警告（不超过100字）：

URL: {analysis_data['url']}
钓鱼评分: {analysis_data['phishing_score']}/100
判断结果: {"钓鱼网站" if analysis_data['is_phishing'] else "安全网站"}

视觉检测到的Logo: {analysis_data['vision'].get('logos', [])}
与PayPal相似度: {analysis_data['similarity']:.2f}
LLM分析: {analysis_data['language'].get('explanation', '')}
威胁情报: {analysis_data['threat_intel']}

请用通俗的语言总结关键风险，并给出建议。
"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return self._template_report(analysis_data)

    def _template_report(self, data):
        if data['is_phishing']:
            return f"⚠️ 该网站被判定为钓鱼网站（置信度{data['phishing_score']}%）。建议立即离开，不要输入任何个人信息。"
        else:
            return f"✅ 该网站看起来安全（置信度{100 - data['phishing_score']}%）。"