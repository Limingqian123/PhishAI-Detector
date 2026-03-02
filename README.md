# PhishAI-Detector

多模态AI赋能的实时钓鱼检测系统，包含Python后端API和Chrome浏览器插件，结合视觉、语言、威胁情报实现精准检测。

## 功能特性
- **浏览器自动化**：Playwright模拟真实用户访问，捕获页面截图、DOM、网络请求
- **多模态分析**：
  - 视觉：Google Vision（Logo/OCR）+ CLIP（品牌相似度）
  - 语言：OpenAI GPT-4分析页面意图
  - 威胁情报：Google Safe Browsing、VirusTotal、PhishTank
- **智能浏览器插件**：本地缓存+启发式规则+后端调用，实时警告阻断
- **可解释报告**：LLM生成通俗易懂的安全建议

## 技术栈
- 后端：FastAPI, Playwright, transformers, Google Cloud Vision, OpenAI
- 插件：Manifest V3, Chrome Extensions API

## 快速开始

### 1. 后端启动
```bash
git clone https://github.com/yourname/phishai-detector
cd phishai-detector

# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 配置环境变量（复制 .env.example 为 .env，填入API密钥）
cp .env.example .env
# 编辑 .env 添加你的密钥

# 启动服务
uvicorn src.main:app --reload
```
访问 `http://localhost:8000/docs` 查看API文档。

### 2. 浏览器插件安装
- 打开 Chrome `chrome://extensions`
- 开启“开发者模式”
- 点击“加载已解压的扩展程序”，选择 `phishai-extension` 目录
- 插件图标出现在工具栏，访问任意网站即可自动检测

## 配置说明
### 后端环境变量 (.env)
| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI API密钥（必填） |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Vision服务账号JSON路径 |
| `VIRUSTOTAL_API_KEY` | VirusTotal API密钥 |
| `GOOGLE_SAFE_BROWSING_API_KEY` | Google Safe Browsing API密钥 |
| `PHISHTANK_API_KEY` | PhishTank API密钥（可选） |
| `BROWSER_HEADLESS` | 是否无头模式（默认true） |

### 插件设置
点击插件图标 → 设置，可配置：
- API地址（默认 `http://localhost:8000`）
- 检测阈值、警告动作、隐私选项

## API使用
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

## 目录结构
```
phishai-detector/          # 后端
├── src/                   # 源代码
├── requirements.txt
├── .env.example
└── ...

phishai-extension/         # 浏览器插件
├── manifest.json
├── background.js
├── content.js
├── popup/
├── options/
├── lib/
└── assets/
```

## 注意事项
- 首次运行后端会自动下载CLIP模型（约600MB）
- 插件需要后端服务运行才能完整工作，本地启发式规则可作为降级方案
- API密钥请妥善保管，勿提交到代码仓库
