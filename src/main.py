from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.models.request import URLRequest
from src.models.response import AnalysisResponse
from src.orchestrator.pipeline import AnalysisPipeline
import logging
import sys
import asyncio

# Windows 下设置支持子进程的事件循环策略
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(
    title="PhishAI-Detector",
    description="多模态AI赋能的实时钓鱼检测系统",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*", "moz-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)
pipeline = AnalysisPipeline()

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_url(request: URLRequest):
    try:
        result = await pipeline.run(str(request.url))
        return result
    except Exception as e:
        logger.error(f"分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}