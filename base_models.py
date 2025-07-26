from pydantic import BaseModel, Field
from typing import List, Optional

class BiasItem(BaseModel):
    category: str
    score: float = Field(..., ge=0.0, le=1.0)
    summary: Optional[str] = None

class BiasDetectionOutput(BaseModel):
    biases: List[BiasItem]
    highlighted_terms: List[str] = []
    error: Optional[str] = None
