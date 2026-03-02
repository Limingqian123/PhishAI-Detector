# PhishAI-Detector 后端

## 安装
1. 安装依赖：`pip install -r requirements.txt`
2. 安装 Playwright 浏览器：`playwright install chromium`
3. 复制 `.env.example` 为 `.env`，填写 API 密钥
4. 运行：`uvicorn src.main:app --reload`

## API 使用
POST `/analyze`  JSON: `{"url": "https://example.com"}`