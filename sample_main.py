
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from uuid import uuid4, UUID
from datetime import datetime
from typing import List
import tempfile
from fastapi import APIRouter
import uvicorn

app = FastAPI()

router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy storage
dummy_sessions = {}
dummy_prompts = {}
dummy_biases = {}
dummy_cross_exams = {}
dummy_perspectives = {}
dummy_overrides = {}

@router.post("/sessions")
def create_session():
    session_id = uuid4()
    dummy_sessions[session_id] = {
        "id": session_id,
        "created_at": datetime.now(),
        "model_used": "gpt-4o",
        "domain": "test"
    }
    return dummy_sessions[session_id]

@router.post("/prompts/get-ai-response")
def create_prompt(session_id: UUID, prompt_text: str):
    prompt_id = uuid4()
    dummy_prompts[prompt_id] = {
        "id": prompt_id,
        "session_id": session_id,
        "prompt_text": prompt_text,
        "ai_response": "This is a dummy AI response.",
        "created_at": datetime.now()
    }
    return dummy_prompts[prompt_id]

@router.post("/bias-insights")
def generate_bias_insights(prompt_id: UUID, ai_response: str):
    dummy_biases[prompt_id] = [
        {"category": "Gender", "score": 0.8, "summary": "Dummy bias summary."}
    ]
    return dummy_biases[prompt_id]

@router.post("/cross-exams")
def create_cross_exam(prompt_id: UUID, user_question: str):
    dummy_cross_exams.setdefault(prompt_id, []).append({
        "user_question": user_question,
        "ai_response": "This is a dummy cross-exam response.",
        "created_at": datetime.now()
    })
    return dummy_cross_exams[prompt_id][-1]

@router.get("/prompts/get-cross-exams-qa")
def list_cross_exams(prompt_id: UUID):
    return dummy_cross_exams.get(prompt_id, [])

@router.post("/perspectives")
def reframe_perspective(prompt_id: UUID, perspective: str):
    dummy_perspectives.setdefault(prompt_id, []).append({
        "perspective": perspective,
        "ai_rephrased_output": f"This is a dummy {perspective} version."
    })
    return dummy_perspectives[prompt_id][-1]

@router.post("/human-overrides")
def create_human_override(prompt_id: UUID, human_response: str, justification: str = "", tags: List[str] = []):
    dummy_overrides[prompt_id] = {
        "human_response": human_response,
        "justification": justification,
        "tags": tags
    }
    return dummy_overrides[prompt_id]

@router.get("/sessions/report")
def generate_bias_report(session_id: UUID, format: str = None):
    prompts = []
    for pid, p in dummy_prompts.items():
        if p["session_id"] == session_id:
            prompts.append({
                "prompt_text": p["prompt_text"],
                "ai_response": p["ai_response"],
                "bias_insights": dummy_biases.get(pid, []),
                "cross_exams": dummy_cross_exams.get(pid, []),
                "perspectives": dummy_perspectives.get(pid, []),
                "human_override": dummy_overrides.get(pid)
            })

    report = {
        "session_id": session_id,
        "model_used": "gpt-4o",
        "domain": "test",
        "created_at": datetime.now(),
        "prompts": prompts
    }

    if format == "pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(b"%PDF-1.4\n% Dummy PDF Content\n%%EOF")
            return FileResponse(f.name, media_type="application/pdf", filename="unmaskai_report_dummy.pdf")

    return report

app.include_router(router)

# Allow running via `python main.py`
if __name__ == "__main__":
    uvicorn.run("sample_main:app", host="0.0.0.0", port=8000, reload=True)