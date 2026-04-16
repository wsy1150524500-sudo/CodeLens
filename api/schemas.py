from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    session_id: str


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str


class SummaryRequest(BaseModel):
    filename: str


class SummaryResponse(BaseModel):
    summary: str
    filename: str
