from playwright.async_api import async_playwright
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class PlaywrightManager:
    def __init__(self, headless: bool = None):
        self.headless = headless if headless is not None else settings.BROWSER_HEADLESS
        self.playwright = None
        self.browser = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        logger.info("浏览器启动成功")

    async def capture(self, url: str, timeout: int = 30000):
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=settings.USER_AGENT
        )
        page = await context.new_page()
        requests = []
        page.on("request", lambda req: requests.append(req.url))

        try:
            await page.goto(url, timeout=timeout, wait_until='networkidle')
        except Exception as e:
            logger.warning(f"页面加载超时或失败: {e}")

        screenshot = await page.screenshot(full_page=True)
        page_text = await page.evaluate('() => document.body.innerText')
        links = await page.evaluate('() => Array.from(document.links).map(a => a.href)')
        forms = await page.evaluate('''() => {
            return Array.from(document.forms).map(f => ({
                action: f.action,
                method: f.method,
                inputs: Array.from(f.elements).map(e => e.type)
            }))
        }''')

        await context.close()
        return {
            'screenshot': screenshot,
            'page_text': page_text,
            'links': links,
            'forms': forms,
            'requests': requests
        }

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("浏览器已关闭")