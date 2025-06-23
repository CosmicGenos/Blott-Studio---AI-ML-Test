from typing import List, Literal
from pydantic import BaseModel
from app.DTO.enum import RecommendedAction


class RiskAssessmentDTO(BaseModel):
    risk_score: float
    risk_factors: List[str]
    reasoning: str
    recommended_action: RecommendedAction
    merchant_risk_score: float
    customer_risk_score: float