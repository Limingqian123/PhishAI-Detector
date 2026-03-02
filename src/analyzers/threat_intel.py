import requests
import base64
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class ThreatIntelAnalyzer:
    def __init__(self):
        self.gsb_api_key = settings.GOOGLE_SAFE_BROWSING_API_KEY
        self.vt_api_key = settings.VIRUSTOTAL_API_KEY
        self.phishtank_api_key = settings.PHISHTANK_API_KEY

    async def check(self, url: str):
        results = {}

        if self.gsb_api_key:
            try:
                gsb_payload = {
                    'client': {'clientId': 'phishai', 'clientVersion': '1.0'},
                    'threatInfo': {
                        'threatTypes': ['MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE',
                                        'POTENTIALLY_HARMFUL_APPLICATION'],
                        'platformTypes': ['ANY_PLATFORM'],
                        'threatEntryTypes': ['URL'],
                        'threatEntries': [{'url': url}]
                    }
                }
                gsb_resp = requests.post(
                    f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.gsb_api_key}',
                    json=gsb_payload,
                    timeout=5
                )
                if gsb_resp.status_code == 200:
                    data = gsb_resp.json()
                    results['google_safe'] = 'malicious' if data.get('matches') else 'safe'
                else:
                    results['google_safe'] = 'error'
            except Exception as e:
                logger.error(f"Google Safe Browsing 查询失败: {e}")
                results['google_safe'] = 'error'
        else:
            results['google_safe'] = 'not_configured'

        if self.vt_api_key:
            try:
                url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
                vt_url = f'https://www.virustotal.com/api/v3/urls/{url_id}'
                headers = {'x-apikey': self.vt_api_key}
                vt_resp = requests.get(vt_url, headers=headers, timeout=5)
                if vt_resp.status_code == 200:
                    stats = vt_resp.json()['data']['attributes']['last_analysis_stats']
                    results['virustotal'] = stats
                else:
                    results['virustotal'] = 'error'
            except Exception as e:
                logger.error(f"VirusTotal 查询失败: {e}")
                results['virustotal'] = 'error'
        else:
            results['virustotal'] = 'not_configured'

        if self.phishtank_api_key:
            try:
                pt_resp = requests.post(
                    'https://checkurl.phishtank.com/checkurl/',
                    data={'url': url, 'format': 'json', 'app_key': self.phishtank_api_key},
                    timeout=5
                )
                if pt_resp.status_code == 200:
                    pt_json = pt_resp.json()
                    results['phishtank'] = pt_json['results']['in_database']
                else:
                    results['phishtank'] = 'error'
            except Exception as e:
                logger.error(f"PhishTank 查询失败: {e}")
                results['phishtank'] = 'error'
        else:
            results['phishtank'] = 'not_configured'

        return results