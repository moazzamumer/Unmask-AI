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
    #highlighted_terms: List[str] = []

class SessionCreate(BaseModel):
    model_used: Optional[str]
    domain: Optional[str]

class SessionOut(BaseModel):
    id: UUID
    created_at: datetime
    model_used: Optional[str]
    domain: Optional[str]

    class Config:
        from_attributes = True

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
        from_attributes = True

class BiasInput(BaseModel):
    prompt_id: UUID
    ai_response: str

class BiasInsightOut(BiasItem):
    id: UUID

    class Config:
        from_attributes = True

class CrossExamCreate(BaseModel):
    prompt_id: UUID
    user_question: str

class CrossExamOut(BaseModel):
    id: UUID
    prompt_id: UUID
    user_question: str
    ai_response: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class CrossExamListItem(BaseModel):
    user_question: str
    ai_response: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True 

class PerspectiveCreate(BaseModel):
    prompt_id: UUID
    perspective: str

class PerspectiveOut(BaseModel):
    id: UUID
    prompt_id: UUID
    perspective: str
    ai_rephrased_output: str

    class Config:
        from_attributes = True

class HumanOverrideCreate(BaseModel):
    prompt_id: UUID
    human_response: str
    justification: Optional[str] = None
    tags: Optional[List[str]] = []

class HumanOverrideOut(BaseModel):
    id: UUID
    prompt_id: UUID
    human_response: str
    justification: Optional[str]
    tags: Optional[List[str]]

    class Config:
        from_attributes = True

class BiasInsightMinimal(BaseModel):
    category: str
    score: float
    summary: Optional[str]

class CrossExamMinimal(BaseModel):
    user_question: str
    ai_response: str

class PerspectiveMinimal(BaseModel):
    perspective: str
    ai_rephrased_output: str

class HumanOverrideMinimal(BaseModel):
    human_response: str
    justification: Optional[str]
    tags: Optional[List[str]]

class PromptReport(BaseModel):
    id: UUID
    prompt_text: str
    ai_response: Optional[str]
    bias_insights: List[BiasInsightMinimal]
    cross_exams: List[CrossExamMinimal]
    perspectives: List[PerspectiveMinimal]
    human_override: Optional[HumanOverrideMinimal]

class BiasReportOut(BaseModel):
    session_id: UUID
    model_used: Optional[str]
    domain: Optional[str]
    created_at: datetime
    prompts: List[PromptReport]
