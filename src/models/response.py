from pydantic import BaseModel
from typing import Optional, Dict, Any

class AnalysisResponse(BaseModel):
    url: str
    is_phishing: bool
    confidence: float
    explanation: str
    details: Optional[Dict[str, Any]] = None