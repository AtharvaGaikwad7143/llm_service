from fastapi import FastAPI, HTTPException
from app.schemas import GenerateRequest, GenerateResponse, ExtractRequest, ExtractResponse
from app.api.routes.documents import router as documents_router
from app.api.routes.query import router as query_router
from app.services.llm import llm_service
import logging

app = FastAPI()

app.include_router(documents_router)
app.include_router(query_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):

    try:
        result = await llm_service.generate(request.prompt)
        return GenerateResponse(response=result)

    except Exception:
        raise HTTPException(status_code=503, 
                            detail="LLM Service temporarily Unavailable",)

@app.post("/extract", response_model=ExtractResponse)
async def extract(request: ExtractRequest):
    result = await llm_service.extract(request.text)
    return result

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)