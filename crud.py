from sqlalchemy.orm import Session
from models import Session as SessionModel
from models import *
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import uuid

def create_session(db: Session, model_used: str = None, domain: str = None) -> SessionModel:
    session_obj = SessionModel(id=uuid.uuid4(), model_used=model_used, domain=domain)
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return session_obj

def create_prompt(db: Session, session_id: str, prompt_text: str, ai_response: str) -> Prompt:
    prompt_obj = Prompt(
        id=uuid.uuid4(),
        session_id=session_id,
        prompt_text=prompt_text,
        ai_response=ai_response,
        created_at=datetime.utcnow()
    )
    db.add(prompt_obj)
    db.commit()
    db.refresh(prompt_obj)
    return prompt_obj

def store_bias_insights(db: Session, prompt_id: UUID, bias_data: List[dict]):
    records = []
    for item in bias_data:
        record = BiasInsight(
            id=uuid.uuid4(),
            prompt_id=prompt_id,
            category=item.category,
            score=item.score,
            insight_summary=item.insight_summary,
            #highlighted_terms=item.highlighted_terms
        )
        db.add(record)
        records.append(record)
        #print(record.insight_summary)
    db.commit()
    return records

def create_cross_exam(db: Session, prompt_id: UUID, user_question: str, ai_response: str) -> CrossExam:
    obj = CrossExam(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        user_question=user_question,
        ai_response=ai_response,
        created_at=datetime.utcnow()
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_cross_exams_by_prompt(db: Session, prompt_id: UUID):
    return (
        db.query(CrossExam)
        .filter(CrossExam.prompt_id == prompt_id)
        .order_by(CrossExam.created_at.asc())
        .all()
    )


def create_perspective_output(
    db: Session, prompt_id: UUID, perspective: str, ai_rephrased_output: str
) -> PerspectiveOutput:
    obj = PerspectiveOutput(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        perspective=perspective,
        ai_rephrased_output=ai_rephrased_output
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def create_human_override(
    db: Session, prompt_id: UUID, human_response: str,
    justification: Optional[str], tags: Optional[List[str]]
) -> HumanOverride:
    override = HumanOverride(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        human_response=human_response,
        justification=justification,
        tags=tags
    )
    db.add(override)
    db.commit()
    db.refresh(override)
    return override

