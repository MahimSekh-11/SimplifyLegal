from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Clause(BaseModel):
    type: str
    description: str
    risk_level: RiskLevel
    explanation: str

class DocumentAnalysis(BaseModel):
    summary: str
    plain_language: str
    clauses: List[Clause]
    risk_score: float  # 0.0 to 1.0
    recommended_actions: List[str]

class AnalysisRequest(BaseModel):
    text: Optional[str] = None
    language: str = "english"