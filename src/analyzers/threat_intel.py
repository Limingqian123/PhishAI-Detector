import requests
import base64
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class ThreatIntelAnalyzer:
    def __init__(self):
        self.gsb_api_key = settings.GOOGLE_SAFE_BROWSING_API_KEY
        self.vt_api_key = settings.VIRUSTOTAL_API_KEY
        # URLhaus 无需 API 密钥

    async def check(self, url: str):
        """综合查询多个威胁情报源"""
        results = {}

        # Google Safe Browsing（原有）
        results['google_safe'] = await self._check_gsb(url)

        # VirusTotal（原有）
        results['virustotal'] = await self._check_vt(url)

        # URLhaus（新增，无需密钥）
        results['urlhaus'] = await self._check_urlhaus(url)

        return results

    async def _check_gsb(self, url: str):
        if not self.gsb_api_key:
            return 'not_configured'
        try:
            payload = {
                'client': {'clientId': 'phishai', 'clientVersion': '1.0'},
                'threatInfo': {
                    'threatTypes': ['MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE'],
                    'platformTypes': ['ANY_PLATFORM'],
                    'threatEntryTypes': ['URL'],
                    'threatEntries': [{'url': url}]
                }
            }
            resp = requests.post(
                f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.gsb_api_key}',
                json=payload,
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                return 'malicious' if data.get('matches') else 'safe'
            return 'error'
        except Exception as e:
            logger.error(f"Google Safe Browsing 查询失败: {e}")
            return 'error'

    async def _check_vt(self, url: str):
        if not self.vt_api_key:
            return 'not_configured'
        try:
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            vt_url = f'https://www.virustotal.com/api/v3/urls/{url_id}'
            headers = {'x-apikey': self.vt_api_key}
            resp = requests.get(vt_url, headers=headers, timeout=5)
            if resp.status_code == 200:
                stats = resp.json()['data']['attributes']['last_analysis_stats']
                return stats
            return 'error'
        except Exception as e:
            logger.error(f"VirusTotal 查询失败: {e}")
            return 'error'

    async def _check_urlhaus(self, url: str):
        """URLhaus API 查询（无需密钥）"""
        try:
            resp = requests.post(
                'https://urlhaus-api.abuse.ch/v1/url/',
                data={'url': url},
                timeout=5,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            if resp.status_code == 200:
                data = resp.json()
                # 判断是否为恶意：query_status == 'ok' 且 url_status 为 'online' 表示活跃恶意
                if data.get('query_status') == 'ok' and data.get('url_status') == 'online':
                    return True
                else:
                    return False
            return False
        except Exception as e:
            logger.error(f"URLhaus 查询失败: {e}")
            return False