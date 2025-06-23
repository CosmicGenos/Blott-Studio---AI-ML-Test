from fastapi import APIRouter, Depends, HTTPException
from app.DTO.RequestDTO import Transaction
from app.services.transaction_risk_analysis_service import TransactionRiskAnalysis
from ..dependancy import get_transaction_analysis_service
from app.DTO.ResponseDTO import RiskAssessmentDTO
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze-risk", response_model=RiskAssessmentDTO)
async def analyze_transaction_risk(
    transaction: Transaction,
    service: TransactionRiskAnalysis = Depends(get_transaction_analysis_service)
) -> RiskAssessmentDTO:
    try:
        return await service.analyze_the_risk(transaction)
    except Exception as e:
        logger.error(f"Risk analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing transaction: {str(e)}"
        ) from e