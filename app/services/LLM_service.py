from openai import AsyncOpenAI, AuthenticationError, RateLimitError
import os
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import ValidationError
from app.DTO.ResponseDTO import RiskAssessmentDTO
from app.DTO.enum import RecommendedAction

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("DEEPINFRA_API_KEY","nSaVs82I0ZTuB9k0W2TdTQMGZKPsm6g7"),
            base_url="https://api.deepinfra.com/v1/openai",
        )
        self.model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
        self.max_tokens = 500
        self.temperature = 0.1

    def create_payload(self, system_prompt: str, user_prompt: str) -> dict:

        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": 1.0,
            "n": 1,
            "stream": False
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitError, ConnectionError, TimeoutError))
    )
    async def call_llm_with_retry(self, payload: dict) -> dict:

        try:
            response = await self.client.chat.completions.create(**payload)
            return response.model_dump()
        except AuthenticationError as e:
            logger.error(f"Authentication failed - check API key: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            raise

    def parse_llm_response(self, raw_response: dict) -> dict:

        try:

            content = raw_response["choices"][0]["message"]["content"]

            if not content or content.strip() == "":
                raise ValueError("LLM returned empty response")

            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            parsed_data = json.loads(content)
            return parsed_data

        except (KeyError, IndexError) as e:
            raise ValueError(f"Invalid response structure: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in LLM response: {str(e)}")

    def validate_response(self, parsed_data: dict) -> RiskAssessmentDTO:

        try:
            return RiskAssessmentDTO(**parsed_data)
        except ValidationError as e:
            raise ValueError(f"Response validation failed: {str(e)}")

    def create_fallback_response(self, error_msg: str) -> RiskAssessmentDTO:

        return RiskAssessmentDTO(
            risk_score=0.5,
            risk_factors=["LLM analysis unavailable"],
            reasoning=f"Unable to complete risk analysis: {error_msg}",
            recommended_action=RecommendedAction.REVIEW,
            merchant_risk_score=0.5,
            customer_risk_score=0.5
        )

    async def get_risk_assessment(
            self,
            system_prompt: str,
            user_prompt: str
    ) -> RiskAssessmentDTO:

        try:
            payload = self.create_payload(system_prompt, user_prompt)
            raw_response = await self.call_llm_with_retry(payload)
            print(f"Raw response from LLM: {raw_response}")
            parsed_data = self.parse_llm_response(raw_response)
            validated_response = self.validate_response(parsed_data)
            logger.info(f"Successfully analyzed transaction with risk score: {validated_response.risk_score}")
            return validated_response

        except Exception as e:

            logger.error(f"LLM risk assessment failed: {str(e)}", exc_info=True)

            return self.create_fallback_response(str(e))
