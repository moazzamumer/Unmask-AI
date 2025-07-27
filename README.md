# 🧠 Unmask AI – Backend

This is the **backend API** for [Unmask AI](https://github.com/moazzamumer/unmask-ai-fe), a human-first tool for interrogating, reframing, and auditing AI responses. Built with **FastAPI**, this service powers bias detection, cross-examination, PDF report generation, and human override flows used by the frontend.

---

## 📁 Directory Structure

```plaintext
moazzamumer-unmask-ai-be/
├── README.md                # This documentation file
├── main.py                 # FastAPI app entry point
├── routes.py               # All API endpoints
├── crud.py                 # DB insert/query logic
├── database.py             # PostgreSQL connection + session handling
├── models.py               # SQLAlchemy ORM models
├── schemas.py              # Pydantic schemas for validation
├── services.py             # LLM integrations (GPT-4o, bias detection, etc.)
├── sample_main.py          # Mock API routes for testing without tokens
├── requirements.txt        # Python dependencies
├── Dockerfile              # Containerization config
├── start.sh                # Launch script for environments like Railway
└── templates/
    └── unmaskai_report.html  # HTML template for PDF session reports
```

---

## 🛠️ Tech Stack

- **FastAPI** – API framework
- **PostgreSQL** – Database
- **SQLAlchemy** – ORM for relational mapping
- **OpenAI GPT-4o** – Language model integration
- **Jinja2 + WeasyPrint** – For generating downloadable PDF reports

---

## 🚀 Setup & Installation

### ✅ Prerequisites

- Python 3.9+
- PostgreSQL running locally or remotely
- `virtualenv` (recommended)

### 🔧 Installation

```bash
# Clone the repo
git clone https://github.com/your-username/moazzamumer-unmask-ai-be
cd moazzamumer-unmask-ai-be

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### ⚙️ Configure your database

Edit `database.py` and set your database URL:

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/unmaskai"
```

Then create the tables:

```bash
python database.py
```

---

## ▶️ Run the Server

```bash
uvicorn main:app --reload
```

Visit your docs at:

```
http://127.0.0.1:8000/docs
```

---

## 🧪 Testing Without Real API Tokens

Use `sample_main.py` to run the backend with dummy responses for dev/demo:

```bash
uvicorn sample_main:app --reload
```

---

## 📄 API Features

- `POST /sessions` — create a new session
- `POST /prompts/get-ai-response` — submit prompt + get LLM output
- `POST /bias-insights` — detect & store bias insights
- `POST /cross-exams` — ask follow-up questions
- `POST /perspectives` — reframe response with new lens
- `POST /human-overrides` — human-correct the AI
- `GET /sessions/report` — export full PDF report

---

## 🐳 Docker Support

Build and run in a container:

```bash
docker build -t unmask-ai-backend .
docker run -p 8000:8000 unmask-ai-backend
```

For Railway, simply use `start.sh` as the start command.

---

## ✨ Created for the "AI vs H.I." Hackathon by CS Girlies

> Unmask AI makes machine intelligence transparent — and puts human insight back in charge.
