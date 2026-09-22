import asyncio
import logging

from google import genai
from google.genai import errors
from google.genai import types
from pydantic import BaseModel, ValidationError

from app.config import settings
from app.schemas import ExtractResponse, RAGEvaluation


logger = logging.getLogger(__name__)


class LLMService:

    def __init__(self):
        # Create the Gemini client once when the service starts.
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        # Keep the model name in one place.
        self.model_name = "gemini-3.8-flash"

    @staticmethod
    def _is_non_retryable_error(exc: Exception) -> bool:
        """
        Decide whether an exception should NOT be retried.

        Daily quota exhaustion is not fixed by retrying.
        The application should fail immediately instead.
        """

        if isinstance(exc, errors.ClientError):
            # 429 = resource exhausted / quota / rate limit
            if exc.code == 429:
                return True

            # 400-level client errors are generally request/configuration
            # problems and retrying the exact same request won't help.
            if 400 <= exc.code < 500:
                return True

        return False

    @staticmethod
    async def _backoff(attempt: int) -> None:
        """
        Exponential backoff.

        attempt 1 -> 1 second
        attempt 2 -> 2 seconds
        attempt 3 -> 4 seconds
        """

        delay = 2 ** (attempt - 1)

        logger.info(
            "Retrying Gemini request after %s seconds.",
            delay,
        )

        await asyncio.sleep(delay)

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

            except errors.ClientError as exc:

                if self._is_non_retryable_error(exc):
                    logger.error(
                        "Non-retryable Gemini client error. "
                        "attempt=%s error=%s",
                        attempt,
                        exc,
                    )
                    raise

                logger.warning(
                    "Retryable Gemini client error. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                await self._backoff(attempt)

            except Exception as exc:
                logger.warning(
                    "Gemini request failed. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                await self._backoff(attempt)

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

        Retry behavior:
        - ValidationError -> retry
        - transient API/network error -> retry
        - 429 quota/client error -> DO NOT retry
        - other 4xx client error -> DO NOT retry
        """

        max_attempts = max_retries + 1

        for attempt in range(1, max_attempts + 1):
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

                # Validate Gemini's JSON against the expected
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

                if attempt == max_attempts:
                    raise

                await self._backoff(attempt)

            except errors.ClientError as exc:

                if self._is_non_retryable_error(exc):
                    logger.error(
                        "Non-retryable structured Gemini error. "
                        "attempt=%s error=%s",
                        attempt,
                        exc,
                    )
                    raise

                logger.warning(
                    "Retryable structured Gemini error. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                await self._backoff(attempt)

            except Exception as exc:
                logger.warning(
                    "Structured LLM generation failed. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                await self._backoff(attempt)

        raise RuntimeError(
            "Structured generation failed unexpectedly."
        )

    async def generate_stream(self, prompt: str):
        """
        Generate a streaming response.

        Transient errors are retried.
        Non-retryable client errors, including quota exhaustion,
        are raised immediately.
        """

        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                response = (
                    await self.client.aio.models.generate_content_stream(
                        model=self.model_name,
                        contents=prompt,
                    )
                )

                async for chunk in response:
                    if chunk.text:
                        yield chunk.text

                return

            except errors.ClientError as exc:

                if self._is_non_retryable_error(exc):
                    logger.error(
                        "Non-retryable streaming Gemini error. "
                        "attempt=%s error=%s",
                        attempt,
                        exc,
                    )
                    raise

                logger.warning(
                    "Retryable streaming Gemini error. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                await self._backoff(attempt)

            except Exception as exc:
                logger.warning(
                    "Gemini streaming request failed. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                await self._backoff(attempt)

    async def evaluate_rag_answer(
        self,
        question: str,
        context: str,
        generated_answer: str,
        reference_answer: str,
        max_retries: int = 2,
    ) -> RAGEvaluation:
        """
        Evaluate a generated RAG answer using an LLM judge.

        The judge evaluates:

        - relevance
        - faithfulness
        - correctness

        The result is validated against the RAGEvaluation
        Pydantic schema.

        Quota exhaustion is not retried.
        """

        prompt = f"""
You are evaluating a RAG system.

Evaluate the generated answer using the question,
retrieved context, and reference answer.

Evaluation criteria:

1. relevance:
Does the generated answer directly answer the question?

2. faithfulness:
Are the claims in the generated answer supported
by the retrieved context?

3. correctness:
Is the generated answer consistent with the reference answer?

Give each score between 0 and 1.

Do not reward information that is not supported by
the retrieved context.

Question:
{question}

Retrieved context:
{context}

Reference answer:
{reference_answer}

Generated answer:
{generated_answer}
"""

        max_attempts = max_retries + 1

        for attempt in range(1, max_attempts + 1):
            try:
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=RAGEvaluation,
                        ),
                    ),
                    timeout=30,
                )

                return RAGEvaluation.model_validate_json(
                    response.text
                )

            except ValidationError as exc:
                logger.warning(
                    "RAG evaluation validation failed. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                await self._backoff(attempt)

            except errors.ClientError as exc:

                if self._is_non_retryable_error(exc):
                    logger.error(
                        "Non-retryable RAG evaluation error. "
                        "attempt=%s error=%s",
                        attempt,
                        exc,
                    )
                    raise

                logger.warning(
                    "Retryable RAG evaluation error. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                await self._backoff(attempt)

            except Exception as exc:
                logger.warning(
                    "RAG evaluation failed. "
                    "attempt=%s error=%s",
                    attempt,
                    exc,
                )

                if attempt == max_attempts:
                    raise

                await self._backoff(attempt)

        raise RuntimeError(
            "RAG evaluation failed unexpectedly."
        )


llm_service = LLMService()