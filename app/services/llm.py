from google import genai
from google.genai import types
from app.config import settings
from app.schemas import ExtractResponse

import asyncio
import logging


logger = logging.getLogger(__name__)


class LLMService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    async def generate(self, prompt: str) -> str:
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):

            try:
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt,
                    ),
                    timeout=30,
                )

                return response.text

            except Exception as exc:
                logger.warning(
                    "Gemini request failed. attempt = %s error = %s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                delay = 2 ** (attempt - 1)
                await asyncio.sleep(delay)

    async def extract(self, text: str) -> ExtractResponse:

        response = await asyncio.wait_for(
            self.client.aio.models.generate_content(
                model="gemini-3.8-flash",
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

        return ExtractResponse.model_validate_json(response.text)


llm_service = LLMService()