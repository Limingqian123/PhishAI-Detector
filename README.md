# PhishAI-Detector

多模态AI赋能的实时钓鱼检测系统，包含Python后端API和Chrome浏览器插件。  
结合视觉分析（Google Vision）、语义分析（DeepSeek/OpenAI）、威胁情报（Google Safe Browsing、VirusTotal、URLhaus）实现精准钓鱼网站识别。

## 功能特性
- **浏览器自动化**：Playwright模拟真实用户访问，捕获截图、DOM、网络请求
- **多模态分析**：
  - 视觉：Google Vision（Logo/OCR） + CLIP（品牌相似度）
  - 语言：DeepSeek/OpenAI GPT分析页面意图
  - 威胁情报：Google Safe Browsing、VirusTotal、URLhaus（无需密钥）
- **智能浏览器插件**：本地启发式检测 + 后端调用，实时警告/阻断
- **可解释报告**：LLM生成通俗易懂的安全建议

## 快速开始

### 1. 后端服务

#### 环境要求
- Python 3.10+
- 安装 [Playwright 浏览器](https://playwright.dev/python/docs/intro)

#### 安装与配置
```bash
git clone https://github.com/yourname/phishai-detector
cd phishai-detector

# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 配置环境变量（复制并编辑 .env）
cp .env.example .env
# 填写必要的 API 密钥（DeepSeek、Google Vision等）
```

**.env 关键配置示例**
```env
DEEPSEEK_API_KEY=sk-xxx
GOOGLE_VISION_API_KEY=AIzaSy...
VIRUSTOTAL_API_KEY=xxx
GOOGLE_SAFE_BROWSING_API_KEY=xxx
```

#### 运行后端
```bash
uvicorn src.main:app --reload
```
访问 `http://localhost:8000/docs` 查看API文档。

### 2. 浏览器插件

#### 安装
- 打开 Chrome `chrome://extensions`
- 开启“开发者模式”
- 点击“加载已解压的扩展程序”，选择 `phishai-extension` 目录
- 插件图标出现在工具栏

#### 配置
- 点击插件图标 → 设置，可修改后端API地址（默认 `http://localhost:8000`）和检测阈值

## 目录结构
```
phishai-detector/          # 后端
├── src/                   # 源代码
│   ├── main.py            # 入口（已添加Windows事件循环修复）
│   ├── config.py
│   ├── browser/           # Playwright封装
│   ├── analyzers/         # 各分析模块
│   └── orchestrator/      # 分析协调器
├── requirements.txt
└── .env.example

phishai-extension/         # 浏览器插件
├── manifest.json          # 已配置 default_locale 或无需国际化
├── background.js
├── content.js
├── popup/
├── options/
├── lib/                   # 本地分析引擎
└── assets/                # 图标（至少包含 icon16/48/128.png）
```

## 重要注意事项

### API 密钥说明
- **DeepSeek API**（替代 OpenAI）：设置 `DEEPSEEK_API_KEY` 和 `api_base="https://api.deepseek.com/v1"`
- **Google Vision**：使用 API 密钥（而非服务账号 JSON），已在代码中通过 REST API 调用
- **VirusTotal**：需注册获取免费密钥，限制 4 次/分钟
- **URLhaus**：无需密钥，直接使用

## API 使用示例
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

响应示例：
```json
{
  "url": "https://example.com",
  "is_phishing": false,
  "confidence": 0.12,
  "explanation": "该网站看起来安全。没有检测到可疑Logo，威胁情报显示干净。"
}
```
