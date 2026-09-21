import asyncio
import logging

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from app.config import settings
from app.schemas import ExtractResponse


logger = logging.getLogger(__name__)


class LLMService:

    def __init__(self):
        # Create the Gemini client once when the service starts.
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        # Keep the model name in one place instead of repeating
        # the hardcoded model name across every method.
        self.model_name = "gemini-3.8-flash"

    async def generate(self, prompt: str) -> str:
        """
        Generate a normal plain-text response.

        Used by the existing /generate endpoint.
        """

        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                    ),
                    timeout=30,
                )

                return response.text

            except Exception as exc:
                logger.warning(
                    "Gemini request failed. attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                # Exponential backoff:
                # attempt 1 -> 1 second
                # attempt 2 -> 2 seconds
                await asyncio.sleep(2 ** (attempt - 1))

    async def extract(self, text: str) -> ExtractResponse:
        """
        Generate a structured extraction response.

        This is the existing Day 1 structured-output endpoint.
        """

        response = await asyncio.wait_for(
            self.client.aio.models.generate_content(
                model=self.model_name,
                contents=f"""
Extract structured information from the following text.

Return:
- title: a short title
- summary: a concise summary
- keywords: important keywords from the text

Text:
{text}
""",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractResponse,
                ),
            ),
            timeout=30,
        )

        # Validate Gemini's JSON against our Pydantic schema.
        return ExtractResponse.model_validate_json(
            response.text
        )

    async def generate_structured(
        self,
        prompt: str,
        response_model: type[BaseModel],
        max_retries: int = 2,
    ) -> BaseModel:
        """
        Generate and validate a structured LLM response.

        The caller provides the Pydantic model that defines
        the expected response contract.
        """

        for attempt in range(1, max_retries + 2):
            try:
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=response_model,
                        ),
                    ),
                    timeout=30,
                )

                # Validate the returned JSON against the expected
                # Pydantic response model.
                return response_model.model_validate_json(
                    response.text
                )

            except ValidationError as exc:
                logger.warning(
                    "Structured output validation failed. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_retries + 1:
                    raise

                # Retry because the model output did not satisfy
                # the expected application contract.
                await asyncio.sleep(2 ** (attempt - 1))

            except Exception as exc:
                logger.exception(
                    "Structured LLM generation failed. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_retries + 1:
                    raise

                # Retry transient API/network failures.
                await asyncio.sleep(2 ** (attempt - 1))

        raise RuntimeError(
            "Structured generation failed unexpectedly."
        )


llm_service = LLMService()