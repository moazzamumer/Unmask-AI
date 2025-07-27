from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router  # assuming routes.py has `router = APIRouter()`
import uvicorn

app = FastAPI(
    title="UnmaskAI API",
    description="Backend for UnmaskAI — Bias detection and analysis",
    version="1.0.0"
)

# Allow frontend (Streamlit, React, etc.) to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(router)

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "UnmaskAI API is running."}

# Allow running via `python main.py`
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
