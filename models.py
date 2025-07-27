
from sqlalchemy import Column, String, Text, Float, ForeignKey, JSON, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

def create_database(engine):
    Base.metadata.create_all(bind=engine)
    print("Database created successfully.")

# -----------------------------
# Sessions Table
# -----------------------------
class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    model_used = Column(String(100))
    domain = Column(String(100))

    # Relationships
    prompts = relationship("Prompt", back_populates="session", cascade="all, delete-orphan")


# -----------------------------
# Prompts Table
# -----------------------------
class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    prompt_text = Column(Text, nullable=False)
    ai_response = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="prompts")
    bias_insights = relationship("BiasInsight", back_populates="prompt", cascade="all, delete-orphan")
    cross_exams = relationship("CrossExam", back_populates="prompt", cascade="all, delete-orphan")
    perspectives = relationship("PerspectiveOutput", back_populates="prompt", cascade="all, delete-orphan")
    human_override = relationship("HumanOverride", back_populates="prompt", uselist=False, cascade="all, delete-orphan")


# -----------------------------
# Bias Insights Table
# -----------------------------
class BiasInsight(Base):
    __tablename__ = "bias_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id", ondelete="CASCADE"))
    category = Column(String(100), nullable=False)
    score = Column(Float)
    #highlighted_terms = Column(JSON)
    insight_summary = Column(Text)

    # Relationships
    prompt = relationship("Prompt", back_populates="bias_insights")


# -----------------------------
# Cross Examinations Table
# -----------------------------
class CrossExam(Base):
    __tablename__ = "cross_exams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id", ondelete="CASCADE"))
    user_question = Column(Text, nullable=False)
    ai_response = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    prompt = relationship("Prompt", back_populates="cross_exams")


# -----------------------------
# Perspective Outputs Table
# -----------------------------
class PerspectiveOutput(Base):
    __tablename__ = "perspective_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id", ondelete="CASCADE"))
    perspective = Column(String(100), nullable=False)
    ai_rephrased_output = Column(Text)

    # Relationships
    prompt = relationship("Prompt", back_populates="perspectives")


# -----------------------------
# Human Overrides Table
# -----------------------------
class HumanOverride(Base):
    __tablename__ = "human_overrides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id", ondelete="CASCADE"))
    human_response = Column(Text, nullable=False)
    justification = Column(Text)
    tags = Column(ARRAY(String))

    # Relationships
    prompt = relationship("Prompt", back_populates="human_override")


# -----------------------------
# Bias Reports Table (optional)
# -----------------------------
class BiasReport(Base):
    __tablename__ = "bias_reports"

    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), primary_key=True)
    final_json = Column(JSON)
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)
