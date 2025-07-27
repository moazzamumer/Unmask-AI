from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class BiasItem(BaseModel):
    category: str
    score: float = Field(..., ge=0.0, le=1.0)
    insight_summary: Optional[str] = None

class BiasDetectionOutput(BaseModel):
    biases: List[BiasItem]
    highlighted_terms: List[str] = []

class SessionCreate(BaseModel):
    model_used: Optional[str]
    domain: Optional[str]

class SessionOut(BaseModel):
    id: UUID
    created_at: datetime
    model_used: Optional[str]
    domain: Optional[str]

    class Config:
        orm_mode = True

class PromptCreate(BaseModel):
    session_id: UUID
    prompt_text: str

class PromptOut(BaseModel):
    id: UUID
    session_id: UUID
    prompt_text: str
    ai_response: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class BiasInput(BaseModel):
    prompt_id: UUID
    ai_response: str

class BiasInsightOut(BiasItem):
    id: UUID

    class Config:
        orm_mode = True
