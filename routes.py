from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import get_db
import schemas, crud
from typing import List
from services import get_llm

router = APIRouter()

@router.post("/sessions", response_model=schemas.SessionOut)
def create_session(payload: schemas.SessionCreate, db: DBSession = Depends(get_db)):
    return crud.create_session(db, model_used=payload.model_used, domain=payload.domain)

@router.post("/prompts", response_model=schemas.PromptOut)
def create_prompt(payload: schemas.PromptCreate, db: DBSession = Depends(get_db)):
    # Get GPT-4o response using services
    llm = get_llm("openai")
    try:
        ai_response = llm.analyze_prompt(payload.prompt_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

    return crud.create_prompt(
        db=db,
        session_id=payload.session_id,
        prompt_text=payload.prompt_text,
        ai_response=ai_response
    )

@router.post("/bias-insights", response_model=List[schemas.BiasInsightOut])
def generate_bias_insights(payload: schemas.BiasInput, db: DBSession = Depends(get_db)):
    llm = get_llm("openai")
    try:
        bias_output = llm.detect_bias(ai_response=payload.ai_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bias detection failed: {str(e)}")

    bias_data = bias_output.biases
    if not bias_data:
        raise HTTPException(status_code=422, detail="No biases returned.")

    return crud.store_bias_insights(db, prompt_id=payload.prompt_id, bias_data=bias_data)
