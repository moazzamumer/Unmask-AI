from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import get_db
import schemas, crud
from typing import List, Optional
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from services import get_llm
from models import *
from uuid import UUID
from textwrap import wrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from tempfile import NamedTemporaryFile
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from tempfile import NamedTemporaryFile
import markdown

router = APIRouter()

@router.post("/sessions", response_model=schemas.SessionOut)
def create_session(payload: schemas.SessionCreate, db: DBSession = Depends(get_db)):
    return crud.create_session(db, model_used=payload.model_used, domain=payload.domain)

@router.post("/prompts/get-ai-response", response_model=schemas.PromptOut)
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

@router.get("/prompts/get-cross-exams-qa", response_model=List[schemas.CrossExamListItem])
def list_cross_exams(prompt_id: UUID, db: DBSession = Depends(get_db)):
    cross_exams = crud.get_cross_exams_by_prompt(db, prompt_id)
    return cross_exams


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

@router.post("/human-overrides", response_model=schemas.HumanOverrideOut)
def create_human_override(payload: schemas.HumanOverrideCreate, db: DBSession = Depends(get_db)):
    # Check that the prompt exists
    prompt_obj = db.query(Prompt).filter(Prompt.id == payload.prompt_id).first()
    if not prompt_obj:
        raise HTTPException(status_code=404, detail="Prompt not found.")

    return crud.create_human_override(
        db=db,
        prompt_id=payload.prompt_id,
        human_response=payload.human_response,
        justification=payload.justification,
        tags=payload.tags
    )

env = Environment(loader=FileSystemLoader("templates"))

@router.get("/sessions/report")
def generate_bias_report(session_id: UUID, format: Optional[str] = None, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    prompt_objs = db.query(Prompt).filter(Prompt.session_id == session_id).all()
    prompt_reports = []

    for prompt in prompt_objs:
        biases = db.query(BiasInsight).filter(BiasInsight.prompt_id == prompt.id).all()
        cross_exams = db.query(CrossExam).filter(CrossExam.prompt_id == prompt.id).all()
        perspectives = db.query(PerspectiveOutput).filter(PerspectiveOutput.prompt_id == prompt.id).all()
        human_override = db.query(HumanOverride).filter(HumanOverride.prompt_id == prompt.id).first()

        prompt_reports.append({
            "id": prompt.id,
            "prompt_text": prompt.prompt_text,
            "ai_response": prompt.ai_response,
            "bias_insights": [
                {
                    "category": b.category,
                    "score": b.score,
                    "summary": b.insight_summary
                } for b in biases
            ],
            "cross_exams": [
                {
                    "user_question": q.user_question,
                    "ai_response": q.ai_response
                } for q in cross_exams
            ],
            "perspectives": [
                {
                    "perspective": p.perspective,
                    "ai_rephrased_output": p.ai_rephrased_output
                } for p in perspectives
            ],
            "human_override": (
                {
                    "human_response": human_override.human_response,
                    "justification": human_override.justification,
                    "tags": human_override.tags
                } if human_override else None
            )
        })

    full_report = {
        "session_id": session.id,
        "model_used": session.model_used,
        "domain": session.domain,
        "created_at": session.created_at,
        "prompts": prompt_reports
        }

    for prompt in full_report["prompts"]:
        prompt["ai_response"] = markdown.markdown(prompt["ai_response"])
        for qa in prompt["cross_exams"]:
            qa["ai_response"] = markdown.markdown(qa["ai_response"])
        for p in prompt["perspectives"]:
            p["ai_rephrased_output"] = markdown.markdown(p["ai_rephrased_output"])

        if format != "pdf":
            return full_report
    
    template = env.get_template("unmaskai_report.html")
    html_content = template.render(report=full_report)

    tmp = NamedTemporaryFile(delete=False, suffix=".pdf")
    HTML(string=html_content).write_pdf(tmp.name)

    return FileResponse(tmp.name, media_type="application/pdf", filename="unmaskai_report.pdf")
