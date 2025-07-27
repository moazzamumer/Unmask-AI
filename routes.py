from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import get_db
import schemas, crud
from typing import List
from services import get_llm
from models import *

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

@router.post("/cross-exams", response_model=schemas.CrossExamOut)
def create_cross_exam(payload: schemas.CrossExamCreate, db: DBSession = Depends(get_db)):
    llm = get_llm("openai")

    # Get original prompt text from DB
    prompt_obj = db.query(Prompt).filter(Prompt.id == payload.prompt_id).first()
    if not prompt_obj:
        raise HTTPException(status_code=404, detail="Prompt not found.")
    
    # Get previous Q&A from DB for this session
    session_id = prompt_obj.session_id
    qa_log = db.query(CrossExam).join(Prompt).filter(
        Prompt.session_id == session_id
    ).order_by(CrossExam.created_at.desc()).limit(5).all()

    qa_log = list(reversed(qa_log))

    previous_qa = [
        {"user_question": qa.user_question, "ai_response": qa.ai_response}
        for qa in qa_log
    ]
    print(previous_qa)

    try:
        ai_response = llm.cross_examine(
        user_prompt=prompt_obj.prompt_text,
        ai_initial_response=prompt_obj.ai_response,
        user_question=payload.user_question,
        previous_qa=previous_qa
        )   
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-exam failed: {str(e)}")

    return crud.create_cross_exam(
        db=db,
        prompt_id=payload.prompt_id,
        user_question=payload.user_question,
        ai_response=ai_response
    )

@router.post("/perspectives", response_model=schemas.PerspectiveOut)
def reframe_perspective(payload: schemas.PerspectiveCreate, db: DBSession = Depends(get_db)):
    prompt_obj = db.query(Prompt).filter(Prompt.id == payload.prompt_id).first()
    if not prompt_obj:
        raise HTTPException(status_code=404, detail="Prompt not found.")

    llm = get_llm("openai")

    try:
        rewritten = llm.reframe_perspective(
            prompt_text=prompt_obj.prompt_text,
            perspective=payload.perspective
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reframing failed: {str(e)}")

    return crud.create_perspective_output(
        db=db,
        prompt_id=payload.prompt_id,
        perspective=payload.perspective,
        ai_rephrased_output=rewritten
    )
