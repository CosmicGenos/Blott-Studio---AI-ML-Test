from fastapi import Depends
from app.services.geographic_analysis_service import GeographicAnalysis
from app.services.record_history_analysis_service import RecordAvailability
from app.services.transaction_pattern_analysis_service import PatternAnalysis
from app.services.prompt_service import propmtService
from app.db.database_connection import get_session
from app.services.LLM_service import LLMService
from app.services.transaction_risk_analysis_service import TransactionRiskAnalysis
from app.services.data_update_service import DataIntegration

async def get_GeographicAnalysis():
    return GeographicAnalysis()

async def get_PatternAnalysis(session=Depends(get_session)):
    return PatternAnalysis(session)

async def get_RecordAvailability(session=Depends(get_session)):
    return RecordAvailability(session)

async def get_prompt_service():
    return propmtService()

async def get_LLMService():
    return LLMService()


async def get_data_integration_service(session=Depends(get_session)):
    return DataIntegration(session)

async def get_transaction_analysis_service(
    geographic_analysis: GeographicAnalysis = Depends(get_GeographicAnalysis),
    record_availability: RecordAvailability = Depends(get_RecordAvailability),
    pattern_analysis: PatternAnalysis = Depends(get_PatternAnalysis),
    prompt_service: propmtService = Depends(get_prompt_service),
    llm_service: LLMService = Depends(get_LLMService),
    data_integration_service: DataIntegration = Depends(get_data_integration_service)
):
    return TransactionRiskAnalysis(
        geographic_analysis=geographic_analysis,
        record_availability=record_availability,
        pattern_analysis=pattern_analysis,
        prompt_service=prompt_service,
        llm_service=llm_service,
        dataIntegration_service=data_integration_service
    )
