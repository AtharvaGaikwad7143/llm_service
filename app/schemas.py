from pydantic import BaseModel

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    response: str

class ExtractRequest(BaseModel):
    text: str

class ExtractResponse(BaseModel):
    title: str
    summary: str
    keywords: list[str]